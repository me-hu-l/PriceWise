from fastapi import APIRouter

from app.api.routes import (
    dashboard,
    drivers,
    forecasts,
    market,
    materials,
    recommendations,
    scenarios,
    suppliers,
)

api_router = APIRouter()
api_router.include_router(materials.router)
api_router.include_router(drivers.router)
api_router.include_router(market.router)
api_router.include_router(suppliers.router)
api_router.include_router(forecasts.router)
api_router.include_router(scenarios.router)
api_router.include_router(recommendations.router)
api_router.include_router(dashboard.router)
