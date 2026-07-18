from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from . import models, schemas, database
from .database import engine
from .routers import auth_router, orders_router, admin_router, agent_router
import os

from sqlalchemy import text
from sqlalchemy.engine.reflection import Inspector

models.Base.metadata.create_all(bind=engine)

try:
    inspector = Inspector.from_engine(engine)
    if "pricing_settings" in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns("pricing_settings")]
        if "service_active" not in columns:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE pricing_settings ADD COLUMN service_active BOOLEAN DEFAULT true"))
except Exception as e:
    print("Auto-migration failed:", e)
app = FastAPI(title="Campus Copies API")

# Allow all origins for dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth_router.router)
app.include_router(orders_router.router)
app.include_router(admin_router.router)
app.include_router(agent_router.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Campus Copies API"}

@app.get("/public/settings", response_model=schemas.PricingSettingsResponse)
def get_public_settings(db: Session = Depends(database.get_db)):
    settings = db.query(models.PricingSettings).first()
    if not settings:
        settings = models.PricingSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings
