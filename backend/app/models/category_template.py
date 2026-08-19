from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime

from app.core.database import Base


class CategoryTemplate(Base):
    __tablename__ = "category_templates"

    id = Column(Integer, primary_key=True, index=True)
    platform_code = Column(String, nullable=True)

    main_category = Column(String, nullable=False)
    subcategory = Column(String, nullable=False)
    description = Column(String, nullable=True)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)