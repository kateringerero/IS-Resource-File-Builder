from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON
from datetime import datetime

from app.core.database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)

    client_id = Column(Integer, ForeignKey("clients.id"))
    import_id = Column(Integer, ForeignKey("import_files.id"))

    external_ticket_id = Column(String, index=True)

    subject = Column(String, nullable=True)

    customer_message = Column(String, nullable=True)
    agent_response = Column(String, nullable=True)

    status = Column(String, nullable=True)
    channel = Column(String, nullable=True)

    created_at_source = Column(DateTime, nullable=True)
    closed_at_source = Column(DateTime, nullable=True)

    raw_ticket_json = Column(JSON, nullable=True)

    is_valid_closed_ticket = Column(Boolean, default=True)
    excluded_reason = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)