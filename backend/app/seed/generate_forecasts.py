"""Precompute forecasts for every material after seeding raw data (roadmap section 39).

Usage: called automatically at the end of app.seed.seed_database.seed(). Can also
be run standalone: `python -m app.seed.generate_forecasts` (re-seeds nothing,
just (re)generates forecasts against whatever is already in the DB).
"""

from __future__ import annotations

from app.db.database import SessionLocal
from app.services import forecast_service, material_service


def generate_all_forecasts() -> int:
    db = SessionLocal()
    count = 0
    try:
        for material in material_service.list_materials(db):
            forecast = forecast_service.generate_forecast(db, material)
            if forecast is not None:
                count += 1
        return count
    finally:
        db.close()


if __name__ == "__main__":
    n = generate_all_forecasts()
    print(f"Precomputed forecasts for {n} materials.")
