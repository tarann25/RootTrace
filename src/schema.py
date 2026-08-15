from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field

class CanonicalEventRecord(BaseModel):
    timestamp_utc: datetime = Field(..., description="UTC timestamp of the event")
    host: Optional[str] = Field(None, description="Hostname or IP address of the system where the event occurred")
    user: Optional[str] = Field(None, description="Username associated with the event")
    source_ip: Optional[str] = Field(None, description="Source IP address of the network connection")
    event_type: str = Field(..., description="Category of the event (e.g., 'login_failed', 'dns_query')")
    log_source: str = Field(..., description="Source system generating the log (e.g., 'wazuh', 'cloudtrail', 'syslog')")
    raw_ref: Any = Field(..., description="Reference or original raw log entry for auditing")
