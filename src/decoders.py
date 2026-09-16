import re
import json
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from src.schema import CanonicalEventRecord

def parse_iso_or_fallback(timestamp_str: str) -> datetime:
    """Safely parses ISO timestamp variants to a UTC datetime."""
    if not timestamp_str:
        return datetime.now(timezone.utc)
    try:
        clean_str = timestamp_str.replace("Z", "+00:00").replace("+0000", "+00:00")
        dt = datetime.fromisoformat(clean_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return datetime.now(timezone.utc)

def decode_wazuh(log: dict) -> CanonicalEventRecord:
    """Parses a Wazuh alert JSON into a CanonicalEventRecord."""
    timestamp = parse_iso_or_fallback(log.get("timestamp", ""))

    rule = log.get("rule", {})
    data = log.get("data", {})
    network = data.get("network", {})
    identity = data.get("identity", {})
    
    metadata = {
        "auth_method": data.get("authentication", {}).get("auth_method_used"),
        "passkey_status": data.get("authentication", {}).get("passkey_info", {}).get("passkey_status"),
        "vpn_provider": network.get("vpn_provider"),
        "device": data.get("device_info", {}).get("os"),
        "browser": data.get("device_info", {}).get("browser")
    }
    if network.get("geo_location"):
        metadata["geo_location"] = network.get("geo_location")

    return CanonicalEventRecord(
        timestamp_utc=timestamp,
        host=log.get("agent", {}).get("name"),
        user=identity.get("target_user") or identity.get("user_principal_name"),
        source_ip=network.get("srcip"),
        event_type=rule.get("description", "wazuh_alert"),
        log_source="wazuh",
        metadata={k: v for k, v in metadata.items() if v is not None},
        raw_ref=log
    )

def decode_cloudtrail(log: dict) -> CanonicalEventRecord:
    """Parses an AWS CloudTrail JSON log into a CanonicalEventRecord."""
    timestamp = parse_iso_or_fallback(log.get("eventTime", ""))
    user_identity = log.get("userIdentity", {})
    
    return CanonicalEventRecord(
        timestamp_utc=timestamp,
        host=log.get("awsRegion"),
        user=user_identity.get("userName"),
        source_ip=log.get("sourceIPAddress"),
        event_type=log.get("eventName", "cloudtrail_event"),
        log_source="cloudtrail",
        metadata={
            "user_agent": log.get("userAgent"),
            "arn": user_identity.get("arn"),
            "account_id": user_identity.get("accountId"),
            "event_source": log.get("eventSource")
        },
        raw_ref=log
    )

def decode_email_gateway_dict(log: dict) -> CanonicalEventRecord:
    """Direct deterministic decoder for structured email gateway records."""
    timestamp = parse_iso_or_fallback(log.get("timestamp", ""))
    sender = log.get("sender", {})
    recipient = log.get("recipient", "")
    user = recipient.split("@")[0] if "@" in recipient else recipient

    metadata = {
        "sender": sender.get("envelope_from"),
        "header_from": sender.get("header_from"),
        "sender_ip": sender.get("sender_ip"),
        "mail_server_hostname": sender.get("mail_server_hostname"),
        "recipient": recipient,
        "subject": log.get("subject"),
        "authentication_results": log.get("authentication_results"),
        "urls_detected": log.get("body_analysis", {}).get("urls_detected", []),
        "action_taken": log.get("action_taken")
    }

    return CanonicalEventRecord(
        timestamp_utc=timestamp,
        host=sender.get("mail_server_hostname"),
        user=user,
        source_ip=sender.get("sender_ip"),
        event_type=log.get("event_type", "email_reception"),
        log_source="email_gateway",
        metadata={k: v for k, v in metadata.items() if v is not None},
        raw_ref=log
    )

PROXY_LOG_REGEX = re.compile(
    r'^(\d+\.\d+\.\d+\.\d+)\s+-\s+([^\s]+)\s+\[([^\]]+)\]\s+"([A-Z]+)\s+([^\s]+)\s+HTTP/[^"]+"\s+(\d+)\s+(\d+)\s+"([^"]*)"\s+"([^"]*)"(?:\s+CATEGORY="([^"]*)")?(?:\s+ACTION="([^"]*)")?'
)

def decode_proxy_log(line: str) -> Optional[CanonicalEventRecord]:
    """Decodes common access proxy / web log entries."""
    match = PROXY_LOG_REGEX.match(line.strip())
    if not match:
        return None

    src_ip, user, ts_str, method, path, status, size, referer, ua, category, action = match.groups()
    try:
        dt = datetime.strptime(ts_str, "%d/%b/%Y:%H:%M:%S %z")
    except Exception:
        dt = datetime.now(timezone.utc)

    metadata = {
        "method": method,
        "path": path,
        "status_code": status,
        "url": referer if referer else path,
        "user_agent": ua,
        "category": category,
        "action_status": action or "allowed"
    }

    return CanonicalEventRecord(
        timestamp_utc=dt,
        host="web_proxy_gateway",
        user=user if user != "-" else None,
        source_ip=src_ip,
        event_type="phishing_attempt" if (category and "phish" in category.lower()) else "web_proxy_access",
        log_source="web_proxy",
        metadata={k: v for k, v in metadata.items() if v is not None},
        raw_ref=line
    )

DNS_LOG_REGEX = re.compile(
    r'^(\d{2}-[A-Za-z]{3}-\d{4} \d{2}:\d{2}:\d{2}(?:\.\d+)?)\s+client\s+(\d+\.\d+\.\d+\.\d+)(?:#\d+)?\s*\(([^)]+)\):\s*(query|response):\s*([^\n]+)'
)

def decode_dns_log(line: str) -> Optional[CanonicalEventRecord]:
    """Decodes BIND / standard DNS query and response log entries."""
    match = DNS_LOG_REGEX.match(line.strip())
    if not match:
        return None

    ts_str, src_ip, domain, q_type, detail = match.groups()
    try:
        # BIND format: 05-Aug-2026 14:02:15.104
        dt = datetime.strptime(ts_str, "%d-%b-%Y %H:%M:%S.%f")
        dt = dt.replace(tzinfo=timezone.utc)
    except Exception:
        dt = datetime.now(timezone.utc)

    metadata = {
        "query": domain,
        "dns_action": q_type,
        "detail": detail.strip()
    }
    if "response:" in line and "NOERROR" in detail:
        metadata["response_status"] = "NOERROR"
        ip_match = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', detail)
        if ip_match:
            metadata["response_ip"] = ip_match.group(0)

    return CanonicalEventRecord(
        timestamp_utc=dt,
        host="internal_dns_resolver",
        user=None,
        source_ip=src_ip,
        event_type="dns_query" if q_type == "query" else "dns_response",
        log_source="dns_query",
        metadata=metadata,
        raw_ref=line
    )
