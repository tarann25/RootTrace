import json
from datetime import datetime
from src.schema import CanonicalEventRecord

def decode_wazuh(log: dict) -> CanonicalEventRecord:
    """Parses a Wazuh alert JSON into a CanonicalEventRecord."""
    timestamp_str = log.get("timestamp", "")
    try:
        timestamp = datetime.fromisoformat(timestamp_str.replace("+0000", "+00:00"))
    except ValueError:
        timestamp = datetime.utcnow()

    rule = log.get("rule", {})
    data = log.get("data", {})
    network = data.get("network", {})
    identity = data.get("identity", {})
    
    return CanonicalEventRecord(
        timestamp_utc=timestamp,
        host=log.get("agent", {}).get("name"),
        user=identity.get("target_user") or identity.get("user_principal_name"),
        source_ip=network.get("srcip"),
        event_type=rule.get("description", "wazuh_alert"),
        log_source="wazuh",
        metadata={
            "auth_method": data.get("authentication", {}).get("auth_method_used"),
            "passkey_status": data.get("authentication", {}).get("passkey_info", {}).get("passkey_status"),
            "vpn_provider": network.get("vpn_provider"),
            "device": data.get("device_info", {}).get("os"),
            "browser": data.get("device_info", {}).get("browser")
        },
        raw_ref=log
    )

def decode_cloudtrail(log: dict) -> CanonicalEventRecord:
    """Parses an AWS CloudTrail JSON log into a CanonicalEventRecord."""
    timestamp_str = log.get("eventTime", "")
    try:
        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    except ValueError:
        timestamp = datetime.utcnow()

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
            "account_id": user_identity.get("accountId")
        },
        raw_ref=log
    )
