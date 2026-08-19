from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean
from datetime import datetime

from app.core.database import Base


class TicketClassification(Base):
    __tablename__ = "ticket_classifications"

    id = Column(Integer, primary_key=True, index=True)

    analysis_run_id = Column(Integer, ForeignKey("analysis_runs.id"))
    ticket_id = Column(Integer, ForeignKey("tickets.id"))

    ai_main_category = Column(String, nullable=True)
    ai_subcategory = Column(String, nullable=True)

    ai_confidence = Column(Float, nullable=True)
    ai_reason = Column(String, nullable=True)

    is_support_ticket = Column(Boolean, nullable=True)

    suggested_new_main_category = Column(String, nullable=True)
    suggested_new_subcategory = Column(String, nullable=True)

    review_status = Column(String, default="pending")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)