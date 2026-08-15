import requests
import json
from datetime import datetime
from src.schema import CanonicalEventRecord

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:7b"

def extract_from_unstructured(log_text: str, log_source: str) -> CanonicalEventRecord:
    """Uses local Ollama LLM to extract structured fields from raw text logs."""
    schema_definition = CanonicalEventRecord.model_json_schema()
    
    prompt = f"""
You are an expert security analyst. Extract the relevant fields from the following unstructured log entry.
Return ONLY a valid JSON object matching this schema exactly. Do not output any markdown formatting or extra text.
CRITICAL: Squeeze as much context out of the log as possible! Place all extra contextual details (like URLs, User Agents, Sender addresses, action statuses, DNS resolution IPs, HTTP methods) into the 'metadata' dict field.
Schema:
{json.dumps(schema_definition, indent=2)}

Log Source: {log_source}
Log Entry:
{log_text}
"""
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "format": "json",
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=120)
        response.raise_for_status()
        result_text = response.json().get("response", "{}")
        
        parsed_json = json.loads(result_text)
        
        # Override log_source and raw_ref to ensure they are accurate
        parsed_json['log_source'] = log_source
        parsed_json['raw_ref'] = log_text
        
        return CanonicalEventRecord(**parsed_json)
    except Exception as e:
        print(f"Error calling Ollama for log extraction: {e}")
        # Return a fallback record in case of failure
        return CanonicalEventRecord(
            timestamp_utc=datetime.utcnow(),
            event_type="extraction_failed",
            log_source=log_source,
            raw_ref=log_text
        )
