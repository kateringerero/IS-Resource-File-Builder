from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime

from app.core.database import Base


class ClientGorgiasCredential(Base):
    __tablename__ = "client_gorgias_credentials"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, unique=True)

    email = Column(String, nullable=False)
    api_key_encrypted = Column(String, nullable=False)
    api_base_url = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)