from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from datetime import datetime

from app.core.database import Base


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True, index=True)

    client_id = Column(Integer, ForeignKey("clients.id"))
    import_id = Column(Integer, ForeignKey("import_files.id"))

    started_by = Column(Integer)

    status = Column(String, default="queued")

    tickets_limit = Column(Integer, default=250)

    total_ticket_ids = Column(Integer, default=0)
    fetched_tickets_count = Column(Integer, default=0)
    analyzed_tickets_count = Column(Integer, default=0)

    support_count = Column(Integer, default=0)
    non_support_count = Column(Integer, default=0)

    brand_tone_ai_suggested = Column(String, nullable=True)

    summary_json = Column(JSON, nullable=True)

    error_message = Column(String, nullable=True)

    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)