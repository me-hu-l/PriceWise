"""Import all model modules so SQLAlchemy's declarative registry is fully populated."""

from app.db.models.material import Material, MaterialComponent
from app.db.models.driver import Driver, ComponentDriver, DriverObservation
from app.db.models.price import PriceObservation
from app.db.models.market_event import MarketEvent
from app.db.models.supplier import Supplier, SupplierQuote
from app.db.models.forecast import Forecast, ForecastContribution, ConfidenceComponent
from app.db.models.recommendation import Recommendation, Evidence

__all__ = [
    "Material",
    "MaterialComponent",
    "Driver",
    "ComponentDriver",
    "DriverObservation",
    "PriceObservation",
    "MarketEvent",
    "Supplier",
    "SupplierQuote",
    "Forecast",
    "ForecastContribution",
    "ConfidenceComponent",
    "Recommendation",
    "Evidence",
]
