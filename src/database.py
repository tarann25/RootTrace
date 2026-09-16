import os
import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import create_engine, Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_DIR = "data"
DATABASE_URL = f"sqlite:///{os.path.join(DATABASE_DIR, 'roottrace.db')}"

os.makedirs(DATABASE_DIR, exist_ok=True)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), default="Untitled Incident Investigation")
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    summary = Column(Text, nullable=True)
    report_markdown = Column(Text, nullable=True)

    log_files = relationship("LogFile", back_populates="incident", cascade="all, delete-orphan")
    events = relationship("ParsedEvent", back_populates="incident", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "summary": self.summary,
            "has_report": bool(self.report_markdown),
            "log_files_count": len(self.log_files) if self.log_files else 0,
            "events_count": len(self.events) if self.events else 0
        }

class LogFile(Base):
    __tablename__ = "log_files"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id = Column(String(36), ForeignKey("incidents.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=True)  # e.g. wazuh, cloudtrail, email_gateway, proxy, dns, generic
    file_path = Column(String(500), nullable=True)
    raw_content = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    incident = relationship("Incident", back_populates="log_files")

    def to_dict(self):
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "filename": self.filename,
            "file_type": self.file_type,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None
        }

class ParsedEvent(Base):
    __tablename__ = "parsed_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id = Column(String(36), ForeignKey("incidents.id"), nullable=False)
    cluster_id = Column(String(50), default="cluster_1")
    timestamp_utc = Column(DateTime, nullable=False)
    host = Column(String(255), nullable=True)
    user = Column(String(255), nullable=True)
    source_ip = Column(String(100), nullable=True)
    event_type = Column(String(255), nullable=False)
    log_source = Column(String(100), nullable=False)
    metadata_json = Column(Text, default="{}")
    raw_ref = Column(Text, nullable=True)

    incident = relationship("Incident", back_populates="events")

    def to_dict(self):
        import json
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "cluster_id": self.cluster_id,
            "timestamp_utc": self.timestamp_utc.isoformat() if self.timestamp_utc else None,
            "host": self.host,
            "user": self.user,
            "source_ip": self.source_ip,
            "event_type": self.event_type,
            "log_source": self.log_source,
            "metadata": json.loads(self.metadata_json) if self.metadata_json else {},
            "raw_ref": self.raw_ref
        }

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
