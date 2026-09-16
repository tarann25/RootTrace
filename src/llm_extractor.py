import requests
import json
from datetime import datetime, timezone
from src.schema import CanonicalEventRecord

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:7b"

def extract_from_unstructured(log_text: str, log_source: str) -> CanonicalEventRecord:
    """Uses local Ollama LLM to extract structured fields from raw text logs."""
    prompt = f"""You are a cybersecurity log parser. Extract fields from this {log_source} log into JSON.
Return JSON with exact keys:
"timestamp_utc" (ISO 8601 string, e.g. "2026-08-05T14:00:00Z"),
"host" (string or null),
"user" (username or null),
"source_ip" (IP or null),
"event_type" (concise event name),
"log_source" ("{log_source}"),
"metadata" (object with key extracted info like urls, action, method, status)

Log Entry:
{log_text}
"""
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "format": "json",
        "stream": False,
        "options": {
            "temperature": 0.0,
            "num_predict": 256
        }
    }
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=30)
        response.raise_for_status()
        result_text = response.json().get("response", "{}")
        
        parsed_json = json.loads(result_text)
        parsed_json['log_source'] = log_source
        parsed_json['raw_ref'] = log_text
        
        if "timestamp_utc" in parsed_json and isinstance(parsed_json["timestamp_utc"], str):
            try:
                parsed_json["timestamp_utc"] = datetime.fromisoformat(parsed_json["timestamp_utc"].replace("Z", "+00:00"))
            except Exception:
                parsed_json["timestamp_utc"] = datetime.now(timezone.utc)
        else:
            parsed_json["timestamp_utc"] = datetime.now(timezone.utc)
            
        return CanonicalEventRecord(**parsed_json)
    except Exception as e:
        print(f"Error calling Ollama for log extraction: {e}")
        return CanonicalEventRecord(
            timestamp_utc=datetime.now(timezone.utc),
            event_type="extraction_fallback",
            log_source=log_source,
            raw_ref=log_text
        )
