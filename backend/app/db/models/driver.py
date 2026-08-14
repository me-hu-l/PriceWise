from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Driver(Base):
    __tablename__ = "drivers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(32))  # RAW_MATERIAL, ENERGY, FX, ...
    description: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(32), nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    default_lag_days: Mapped[int] = mapped_column(Integer, default=0)
    directionality: Mapped[str | None] = mapped_column(String(16), nullable=True)
    reliability_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    component_links: Mapped[list["ComponentDriver"]] = relationship(
        back_populates="driver", cascade="all, delete-orphan"
    )
    observations: Mapped[list["DriverObservation"]] = relationship(
        back_populates="driver", cascade="all, delete-orphan"
    )


class ComponentDriver(Base):
    """Edge of the material knowledge graph: component -> driver."""

    __tablename__ = "component_drivers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    component_id: Mapped[int] = mapped_column(ForeignKey("material_components.id"))
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"))
    relationship_strength: Mapped[float] = mapped_column(Float)
    elasticity: Mapped[float | None] = mapped_column(Float, nullable=True)
    lag_period: Mapped[int] = mapped_column(Integer, default=0)
    direction: Mapped[str] = mapped_column(String(16), default="POSITIVE")
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    rationale: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    component: Mapped["MaterialComponent"] = relationship(back_populates="component_drivers")
    driver: Mapped["Driver"] = relationship(back_populates="component_links")


class DriverObservation(Base):
    __tablename__ = "driver_observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"))
    date: Mapped[date] = mapped_column(Date)
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str | None] = mapped_column(String(32), nullable=True)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_quality: Mapped[float | None] = mapped_column(Float, nullable=True)

    driver: Mapped["Driver"] = relationship(back_populates="observations")
