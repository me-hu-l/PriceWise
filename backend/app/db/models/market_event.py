from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class MarketEvent(Base):
    __tablename__ = "market_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    event_type: Mapped[str] = mapped_column(String(32))
    source_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    published_at: Mapped[datetime] = mapped_column(DateTime)
    affected_driver: Mapped[str | None] = mapped_column(String(255), nullable=True)
    affected_material: Mapped[str | None] = mapped_column(String(255), nullable=True)
    impact_direction: Mapped[str] = mapped_column(String(16), default="NEUTRAL")
    impact_magnitude: Mapped[str] = mapped_column(String(16), default="LOW")
    impact_horizon: Mapped[str] = mapped_column(String(16), default="SHORT")
    event_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    processed_by_llm: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
