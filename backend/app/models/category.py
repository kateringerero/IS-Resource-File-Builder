from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime

from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)

    client_id = Column(Integer, ForeignKey("clients.id"))

    main_category = Column(String, nullable=False)
    subcategory = Column(String, nullable=False)
    description = Column(String, nullable=True)

    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    created_by = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)