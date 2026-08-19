from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Client(TimestampMixin, Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    platform_id: Mapped[int] = mapped_column(ForeignKey("platforms.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    brand_tone: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)
    selected_features_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    brand_tone_mode: Mapped[str] = mapped_column(String, default="manual")
    brand_tone_ai_suggested: Mapped[str | None] = mapped_column(String, nullable=True)

    account = relationship("Account", back_populates="clients")
    platform = relationship("Platform", back_populates="clients")