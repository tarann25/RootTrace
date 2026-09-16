import os
import shutil
import uuid
import requests
from typing import List, Optional
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, PlainTextResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import get_db, init_db, Incident, LogFile, ParsedEvent
from src.pipeline import reconstruct_incident_pipeline

app = FastAPI(
    title="RootTrace API",
    description="Incident Timeline Reconstructor & Root Cause Analysis Engine",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_BASE_DIR = "data/uploads"
SAMPLE_DATA_DIR = "data/sample_phishing_01"
os.makedirs(UPLOAD_BASE_DIR, exist_ok=True)

@app.on_event("startup")
def on_startup():
    init_db()

class IncidentCreateRequest(BaseModel):
    title: Optional[str] = "Phishing & Cloud Reconnaissance Incident"

@app.get("/api/health")
def check_health():
    ollama_ok = False
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=3)
        ollama_ok = r.status_code == 200
    except Exception:
        ollama_ok = False

    return {
        "status": "online",
        "service": "RootTrace API",
        "ollama_available": ollama_ok,
        "ollama_model": "qwen2.5:7b"
    }

@app.post("/api/incidents")
def create_incident(req: IncidentCreateRequest, db: Session = Depends(get_db)):
    incident = Incident(title=req.title or "New Incident Investigation")
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident.to_dict()

@app.get("/api/incidents")
def list_incidents(db: Session = Depends(get_db)):
    incidents = db.query(Incident).order_by(Incident.created_at.desc()).all()
    return [inc.to_dict() for inc in incidents]

@app.get("/api/incidents/{incident_id}")
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    events = db.query(ParsedEvent).filter(ParsedEvent.incident_id == incident_id).order_by(ParsedEvent.timestamp_utc.asc()).all()
    log_files = db.query(LogFile).filter(LogFile.incident_id == incident_id).all()

    # Extract distinct entities
    users = sorted(list(set(e.user for e in events if e.user)))
    ips = sorted(list(set(e.source_ip for e in events if e.source_ip)))
    
    # Collect domains from event metadata
    domains = set()
    for e in events:
        meta = e.to_dict()["metadata"]
        if "urls_detected" in meta and isinstance(meta["urls_detected"], list):
            for u in meta["urls_detected"]:
                if "//" in u:
                    domains.add(u.split("//")[1].split("/")[0])
        if "url" in meta and "//" in str(meta["url"]):
            domains.add(str(meta["url"]).split("//")[1].split("/")[0])
        if "query" in meta:
            domains.add(str(meta["query"]))

    # Duration calculation
    duration_min = 0
    if len(events) >= 2 and events[0].timestamp_utc and events[-1].timestamp_utc:
        delta = events[-1].timestamp_utc - events[0].timestamp_utc
        duration_min = round(delta.total_seconds() / 60.0, 1)

    return {
        **incident.to_dict(),
        "summary": incident.summary,
        "report_markdown": incident.report_markdown,
        "log_files": [lf.to_dict() for lf in log_files],
        "events": [e.to_dict() for e in events],
        "entities": {
            "users": users,
            "ips": ips,
            "domains": sorted(list(domains))
        },
        "metrics": {
            "total_events": len(events),
            "compromised_users": len(users),
            "malicious_ips": len(ips),
            "phishing_domains": len(domains),
            "duration_minutes": duration_min
        }
    }

@app.post("/api/incidents/{incident_id}/upload")
async def upload_log_files(incident_id: str, files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident_dir = os.path.join(UPLOAD_BASE_DIR, incident_id)
    os.makedirs(incident_dir, exist_ok=True)

    uploaded_records = []
    for file in files:
        safe_filename = os.path.basename(file.filename)
        dest_path = os.path.join(incident_dir, safe_filename)
        
        content = await file.read()
        text_content = content.decode("utf-8", errors="replace")
        
        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(text_content)

        log_file = LogFile(
            incident_id=incident_id,
            filename=safe_filename,
            file_path=dest_path,
            raw_content=text_content
        )
        db.add(log_file)
        uploaded_records.append(safe_filename)

    db.commit()
    return {"message": f"Successfully uploaded {len(uploaded_records)} files", "files": uploaded_records}

@app.post("/api/incidents/{incident_id}/load-sample")
def load_sample_dataset(incident_id: str, db: Session = Depends(get_db)):
    """Loads the pre-packaged sample phishing attack suite into the incident."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if not os.path.exists(SAMPLE_DATA_DIR):
        raise HTTPException(status_code=500, detail="Sample dataset directory not found")

    incident_dir = os.path.join(UPLOAD_BASE_DIR, incident_id)
    os.makedirs(incident_dir, exist_ok=True)

    loaded = []
    for fname in os.listdir(SAMPLE_DATA_DIR):
        src_path = os.path.join(SAMPLE_DATA_DIR, fname)
        if os.path.isfile(src_path):
            dest_path = os.path.join(incident_dir, fname)
            shutil.copyfile(src_path, dest_path)
            
            with open(dest_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            log_file = LogFile(
                incident_id=incident_id,
                filename=fname,
                file_path=dest_path,
                raw_content=content
            )
            db.add(log_file)
            loaded.append(fname)

    db.commit()
    return {"message": f"Loaded {len(loaded)} sample log files", "files": loaded}

@app.post("/api/incidents/{incident_id}/reconstruct")
def reconstruct_incident(incident_id: str, db: Session = Depends(get_db)):
    """Executes the full pipeline: parsing, LLM extraction, correlation, report generation."""
    try:
        result = reconstruct_incident_pipeline(incident_id, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/incidents/{incident_id}/report")
def get_incident_report(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident or not incident.report_markdown:
        raise HTTPException(status_code=404, detail="Report not generated yet")
    return {"report_markdown": incident.report_markdown, "summary": incident.summary}

@app.get("/api/incidents/{incident_id}/report/download")
def download_incident_report(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident or not incident.report_markdown:
        raise HTTPException(status_code=404, detail="Report not available")

    filename = f"roottrace_incident_{incident_id[:8]}_report.md"
    return Response(
        content=incident.report_markdown,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
