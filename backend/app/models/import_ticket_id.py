from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime

from app.core.database import Base


class ImportTicketID(Base):
    __tablename__ = "import_ticket_ids"

    id = Column(Integer, primary_key=True, index=True)

    import_id = Column(Integer, ForeignKey("import_files.id"))

    external_ticket_id = Column(String, index=True)

    created_at = Column(DateTime, default=datetime.utcnow)