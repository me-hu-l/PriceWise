from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class CustomPriceObservation(Base):
    """User-uploaded price history kept separate from seeded observations."""

    __tablename__ = "custom_price_observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    material_id: Mapped[int] = mapped_column(ForeignKey("materials.id"))
    date: Mapped[date] = mapped_column(Date)
    price: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(8), default="USD")
    unit: Mapped[str | None] = mapped_column(String(32), nullable=True)
    supplier_id: Mapped[int | None] = mapped_column(nullable=True)
    quantity: Mapped[float | None] = mapped_column(Float, nullable=True)
    contract_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    data_quality: Mapped[str | None] = mapped_column(String(16), nullable=True)