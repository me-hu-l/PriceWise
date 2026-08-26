import sys
from pathlib import Path
import os

backend_dir = Path(__file__).resolve().parents[2]
os.chdir(backend_dir)
sys.path.insert(0, str(backend_dir))

print(f"Current working directory: {os.getcwd()}")

from app.db.database import SessionLocal
db = SessionLocal()
from app.services.forecast_service import generate_forecast
from app.db.models import Material

material = db.query(Material).filter(Material.id == 1).first()
if material is None:
    print("Material with ID 1 not found.")
else:
    print(f"Generating forecast for material ID {material.id}: {material.name}")
    forecast = generate_forecast(db, material)
    print(f"Generated forecast for material ID {material.id}: {forecast}")