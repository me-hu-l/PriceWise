from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Forecast(Base):
    """Phase 2: driver model + ML residual + ensemble output (roadmap sections 8-15)."""

    __tablename__ = "forecasts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    material_id: Mapped[int] = mapped_column(ForeignKey("materials.id"))
    forecast_date: Mapped[date] = mapped_column(Date)
    target_date: Mapped[date] = mapped_column(Date)
    horizon: Mapped[str] = mapped_column(String(16))
    point_forecast: Mapped[float] = mapped_column(Float)
    lower_bound: Mapped[float] = mapped_column(Float)
    upper_bound: Mapped[float] = mapped_column(Float)
    direction: Mapped[str] = mapped_column(String(16))
    model_version: Mapped[str] = mapped_column(String(32))
    confidence_score: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Model disagreement (roadmap section 15): per-candidate pct-change forecasts.
    baseline_pct_change: Mapped[float | None] = mapped_column(Float, nullable=True)
    driver_pct_change: Mapped[float | None] = mapped_column(Float, nullable=True)
    ml_pct_change: Mapped[float | None] = mapped_column(Float, nullable=True)
    disagreement_level: Mapped[str | None] = mapped_column(String(16), nullable=True)

    # Low-data mode + regime change (roadmap sections 10, 25)
    data_mode: Mapped[str | None] = mapped_column(String(16), nullable=True)
    regime_change_detected: Mapped[bool] = mapped_column(Boolean, default=False)

    # Walk-forward backtest metrics (roadmap sections 26-27)
    mae: Mapped[float | None] = mapped_column(Float, nullable=True)
    rmse: Mapped[float | None] = mapped_column(Float, nullable=True)
    mape: Mapped[float | None] = mapped_column(Float, nullable=True)
    directional_accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    interval_coverage: Mapped[float | None] = mapped_column(Float, nullable=True)

    contributions: Mapped[list["ForecastContribution"]] = relationship(
        back_populates="forecast", cascade="all, delete-orphan"
    )
    confidence_component: Mapped["ConfidenceComponent"] = relationship(
        back_populates="forecast", cascade="all, delete-orphan", uselist=False
    )


class ForecastContribution(Base):
    __tablename__ = "forecast_contributions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    forecast_id: Mapped[int] = mapped_column(ForeignKey("forecasts.id"))
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"))
    contribution_value: Mapped[float] = mapped_column(Float)
    contribution_pct: Mapped[float] = mapped_column(Float)
    direction: Mapped[str] = mapped_column(String(16))
    rank: Mapped[int] = mapped_column(Integer)

    forecast: Mapped["Forecast"] = relationship(back_populates="contributions")
    driver: Mapped["Driver"] = relationship()


class ConfidenceComponent(Base):
    __tablename__ = "confidence_components"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    forecast_id: Mapped[int] = mapped_column(ForeignKey("forecasts.id"), unique=True)
    data_score: Mapped[float] = mapped_column(Float)
    driver_score: Mapped[float] = mapped_column(Float)
    model_score: Mapped[float] = mapped_column(Float)
    market_score: Mapped[float] = mapped_column(Float)
    stability_score: Mapped[float] = mapped_column(Float)
    overall_score: Mapped[float] = mapped_column(Float)
    explanation: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    forecast: Mapped["Forecast"] = relationship(back_populates="confidence_component")
