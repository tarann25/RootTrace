import os
import json
from src.decoders import decode_wazuh, decode_cloudtrail
from src.llm_extractor import extract_from_unstructured
from src.correlation import correlate_events

def run_pipeline():
    data_dir = "data/sample_phishing_01"
    events = []

    print("[*] Processing Structured Logs...")
    
    # 1. Wazuh Alerts
    with open(os.path.join(data_dir, "alerts.json"), "r") as f:
        wazuh_log = json.load(f)
        event = decode_wazuh(wazuh_log)
        events.append(event)
        print(f"  -> Decoded Wazuh Alert: {event.event_type}")

    # 2. CloudTrail Logs
    with open(os.path.join(data_dir, "cloudtrail.json"), "r") as f:
        ct_log = json.load(f)
        event = decode_cloudtrail(ct_log)
        events.append(event)
        print(f"  -> Decoded CloudTrail Event: {event.event_type}")

    print("\n[*] Processing Unstructured Logs via Local LLM...")
    
    # 3. Email Gateway (Unstructured/Semi-Structured)
    with open(os.path.join(data_dir, "email_gateway.json"), "r") as f:
        email_content = f.read()
        event = extract_from_unstructured(email_content, "email_gateway")
        events.append(event)
        print("  -> LLM Extracted Email Gateway Log")

    # 4. Proxy Access
    with open(os.path.join(data_dir, "proxy_access.log"), "r") as f:
        proxy_content = f.read()
        event = extract_from_unstructured(proxy_content, "web_proxy")
        events.append(event)
        print("  -> LLM Extracted Proxy Log")

    # 5. DNS Queries
    with open(os.path.join(data_dir, "queries.log"), "r") as f:
        dns_content = f.read()
        event = extract_from_unstructured(dns_content, "dns_query")
        events.append(event)
        print("  -> LLM Extracted DNS Query Log")

    print(f"\n[*] Extracted {len(events)} Canonical Events in total.")
    
    print("\n[*] Running Deterministic Correlation Engine (Stage 3)...")
    clusters = correlate_events(events)
    
    print(f"[*] Formed {len(clusters)} Incident Cluster(s):")
    for cluster in clusters:
        print(f"\n=== {cluster.cluster_id} ===")
        print(f"Shared Entities: {', '.join(cluster.entities)}")
        print("Chronological Timeline Skeleton:")
        # Stage 4 preview: chronologically sorted
        for e in sorted(cluster.events, key=lambda x: x.timestamp_utc):
            print(f"  [{e.timestamp_utc}] ({e.log_source}) -> User: {e.user} | IP: {e.source_ip} | Type: {e.event_type}")

if __name__ == "__main__":
    run_pipeline()
