import os
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from src.schema import CanonicalEventRecord
from src.decoders import decode_wazuh, decode_cloudtrail, decode_email_gateway_dict, decode_proxy_log, decode_dns_log
from src.llm_extractor import extract_from_unstructured
from src.correlation import correlate_events, IncidentCluster
from src.report import generate_report_content
from src.database import Incident, LogFile, ParsedEvent, SessionLocal, init_db

def parse_file_to_events(file_path: str, filename: Optional[str] = None) -> List[CanonicalEventRecord]:
    """Parses an arbitrary log file into one or more CanonicalEventRecord objects."""
    fname = (filename or os.path.basename(file_path)).lower()
    events: List[CanonicalEventRecord] = []

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read().strip()

    if not content:
        return events

    # Attempt JSON parse first
    try:
        data = json.loads(content)
        # Handle list of JSON objects
        items = data if isinstance(data, list) else [data]
        
        for item in items:
            if not isinstance(item, dict):
                continue
                
            # Wazuh check
            if "rule" in item and ("agent" in item or "decoder" in item or "data" in item):
                events.append(decode_wazuh(item))
            # CloudTrail check
            elif "eventVersion" in item or "userIdentity" in item or "eventSource" in item:
                events.append(decode_cloudtrail(item))
            # Email Gateway check
            elif "sender" in item and ("recipient" in item or "envelope_from" in str(item.get("sender"))):
                events.append(decode_email_gateway_dict(item))
            else:
                # Fallback to LLM extraction for generic JSON record
                event = extract_from_unstructured(json.dumps(item), fname)
                events.append(event)
        return events
    except json.JSONDecodeError:
        pass

    # Unstructured / raw text line processing
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    
    # Determine log source hint
    log_source_hint = "generic_log"
    if "proxy" in fname:
        log_source_hint = "web_proxy"
    elif "dns" in fname or "quer" in fname:
        log_source_hint = "dns_query"
    elif "mail" in fname or "email" in fname:
        log_source_hint = "email_gateway"
    elif "auth" in fname or "syslog" in fname:
        log_source_hint = "system_auth"

    # If small number of lines (<= 5), process each line or group
    # For sample logs like queries.log (2 lines) or proxy_access.log (1 line)
    for line in lines:
        if line.startswith("#"):
            continue
        event = decode_proxy_log(line)
        if not event:
            event = decode_dns_log(line)
        if not event:
            event = extract_from_unstructured(line, log_source_hint)
        events.append(event)

    return events

def reconstruct_incident_pipeline(incident_id: str, db: Optional[Session] = None) -> Dict[str, Any]:
    """
    Main orchestration pipeline:
    1. Loads log files associated with the incident from DB or disk.
    2. Decodes/extracts all events to CanonicalEventRecord.
    3. Runs correlation engine to produce IncidentClusters.
    4. Synthesizes executive narrative and renders incident report.
    5. Persists results in DB.
    """
    close_db_at_end = False
    if db is None:
        db = SessionLocal()
        close_db_at_end = True

    try:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            raise ValueError(f"Incident with ID {incident_id} not found")

        incident.status = "processing"
        db.commit()

        # Delete previously parsed events for this incident if re-running
        db.query(ParsedEvent).filter(ParsedEvent.incident_id == incident_id).delete()
        db.commit()

        events: List[CanonicalEventRecord] = []
        log_files = db.query(LogFile).filter(LogFile.incident_id == incident_id).all()

        for log_file in log_files:
            file_events = []
            if log_file.file_path and os.path.exists(log_file.file_path):
                file_events = parse_file_to_events(log_file.file_path, log_file.filename)
            elif log_file.raw_content:
                # Save temp or parse directly
                temp_path = f"/tmp/{log_file.id}_{log_file.filename}"
                with open(temp_path, "w", encoding="utf-8") as tf:
                    tf.write(log_file.raw_content)
                file_events = parse_file_to_events(temp_path, log_file.filename)
                if os.path.exists(temp_path):
                    os.remove(temp_path)

            events.extend(file_events)

        if not events:
            incident.status = "failed"
            incident.summary = "No valid events could be parsed from the uploaded logs."
            db.commit()
            return {"error": "No events parsed"}

        # Run Correlation Engine
        clusters = correlate_events(events)
        if not clusters:
            primary_cluster = IncidentCluster("cluster_1")
            for e in events:
                primary_cluster.add_event(e)
            clusters = [primary_cluster]

        primary_cluster = clusters[0]

        # Generate Executive Narrative & Report
        rendered_md, summary = generate_report_content(primary_cluster)

        # Update Incident in Database
        incident.summary = summary
        incident.report_markdown = rendered_md
        incident.status = "completed"

        # Persist Parsed Events
        def get_naive(dt):
            return dt.replace(tzinfo=None) if dt.tzinfo is not None else dt

        for cluster in clusters:
            for event in cluster.events:
                db_event = ParsedEvent(
                    incident_id=incident_id,
                    cluster_id=cluster.cluster_id,
                    timestamp_utc=get_naive(event.timestamp_utc),
                    host=event.host,
                    user=event.user,
                    source_ip=event.source_ip,
                    event_type=event.event_type,
                    log_source=event.log_source,
                    metadata_json=json.dumps(event.metadata or {}),
                    raw_ref=str(event.raw_ref)
                )
                db.add(db_event)

        db.commit()

        # Save to reports folder as well
        reports_dir = "reports"
        os.makedirs(reports_dir, exist_ok=True)
        report_file_path = os.path.join(reports_dir, f"{incident_id}_report.md")
        with open(report_file_path, "w", encoding="utf-8") as rf:
            rf.write(rendered_md)

        # Calculate metrics
        sorted_events = sorted(primary_cluster.events, key=lambda x: get_naive(x.timestamp_utc))
        duration_minutes = 0
        if len(sorted_events) >= 2:
            delta = get_naive(sorted_events[-1].timestamp_utc) - get_naive(sorted_events[0].timestamp_utc)
            duration_minutes = round(delta.total_seconds() / 60.0, 1)

        users = sorted(list(set(e.split(":", 1)[1] for e in primary_cluster.entities if e.startswith("user:"))))
        ips = sorted(list(set(e.split(":", 1)[1] for e in primary_cluster.entities if e.startswith("ip:"))))
        domains = sorted(list(set(e.split(":", 1)[1] for e in primary_cluster.entities if e.startswith("domain:"))))

        return {
            "incident_id": incident.id,
            "title": incident.title,
            "status": incident.status,
            "summary": summary,
            "report_markdown": rendered_md,
            "metrics": {
                "total_events": len(sorted_events),
                "compromised_users": len(users),
                "malicious_ips": len(ips),
                "phishing_domains": len(domains),
                "duration_minutes": duration_minutes
            },
            "entities": {
                "users": users,
                "ips": ips,
                "domains": domains
            },
            "clusters": [c.to_dict() for c in clusters],
            "timeline": [e.model_dump() for e in sorted_events]
        }

    except Exception as e:
        db.rollback()
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if incident:
            incident.status = "failed"
            incident.summary = f"Pipeline execution failed: {str(e)}"
            db.commit()
        raise e
    finally:
        if close_db_at_end:
            db.close()

def run_pipeline():
    """CLI testing helper that loads data/sample_phishing_01 into SQLite and executes reconstruction."""
    init_db()
    db = SessionLocal()
    data_dir = "data/sample_phishing_01"

    # Create sample incident
    incident = Incident(title="Phishing-to-Cloud Reconnaissance Investigation")
    db.add(incident)
    db.commit()
    db.refresh(incident)

    print(f"[*] Created test incident: {incident.id}")

    # Register sample files
    sample_files = ["alerts.json", "cloudtrail.json", "email_gateway.json", "proxy_access.log", "queries.log"]
    for fname in sample_files:
        fpath = os.path.join(data_dir, fname)
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            log_file = LogFile(
                incident_id=incident.id,
                filename=fname,
                file_path=fpath,
                raw_content=content
            )
            db.add(log_file)
    db.commit()

    print("[*] Running Incident Reconstruction Pipeline...")
    result = reconstruct_incident_pipeline(incident.id, db)
    print(f"\n[+] Reconstruction Completed! Status: {result['status']}")
    print(f"    Total Events Correlated: {result['metrics']['total_events']}")
    print(f"    Entities: {result['entities']}")
    print(f"    Summary: {result['summary'][:150]}...")
    db.close()

if __name__ == "__main__":
    run_pipeline()
