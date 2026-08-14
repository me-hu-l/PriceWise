from datetime import date

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    supplier_code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    country: Mapped[str | None] = mapped_column(String(128), nullable=True)
    qualification_status: Mapped[str] = mapped_column(String(32), default="QUALIFIED")
    lead_time_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    single_source: Mapped[bool] = mapped_column(Boolean, default=False)
    share_of_supply: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    quotes: Mapped[list["SupplierQuote"]] = relationship(
        back_populates="supplier", cascade="all, delete-orphan"
    )


class SupplierQuote(Base):
    __tablename__ = "supplier_quotes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"))
    material_id: Mapped[int] = mapped_column(ForeignKey("materials.id"))
    quote_date: Mapped[date] = mapped_column(Date)
    quoted_price: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(8), default="USD")
    unit: Mapped[str | None] = mapped_column(String(32), nullable=True)
    previous_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    claimed_change_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    reason: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    valid_until: Mapped[date | None] = mapped_column(Date, nullable=True)

    supplier: Mapped["Supplier"] = relationship(back_populates="quotes")
    material: Mapped["Material"] = relationship(back_populates="supplier_quotes")
