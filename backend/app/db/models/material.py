from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Material(Base):
    __tablename__ = "materials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    material_code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(128))
    description: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    unit: Mapped[str] = mapped_column(String(32))
    currency: Mapped[str] = mapped_column(String(8), default="USD")
    criticality: Mapped[str] = mapped_column(String(16), default="MEDIUM")
    current_price: Mapped[float] = mapped_column(Float)
    current_price_date: Mapped[date] = mapped_column(Date)
    lead_time_days: Mapped[int] = mapped_column(Integer)
    single_source_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    components: Mapped[list["MaterialComponent"]] = relationship(
        back_populates="material", cascade="all, delete-orphan"
    )
    price_observations: Mapped[list["PriceObservation"]] = relationship(
        back_populates="material", cascade="all, delete-orphan"
    )
    supplier_quotes: Mapped[list["SupplierQuote"]] = relationship(
        back_populates="material", cascade="all, delete-orphan"
    )


class MaterialComponent(Base):
    __tablename__ = "material_components"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    material_id: Mapped[int] = mapped_column(ForeignKey("materials.id"))
    component_name: Mapped[str] = mapped_column(String(255))
    component_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    percentage_of_cost: Mapped[float] = mapped_column(Float)
    unit: Mapped[str | None] = mapped_column(String(32), nullable=True)
    description: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    material: Mapped["Material"] = relationship(back_populates="components")
    component_drivers: Mapped[list["ComponentDriver"]] = relationship(
        back_populates="component", cascade="all, delete-orphan"
    )
