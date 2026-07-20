# Trigger server restart for persistence check
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from . import models, schemas, database, auth
from .database import engine
from .routers import auth_router, orders_router, admin_router, agent_router
import os

from sqlalchemy import text
from sqlalchemy.engine.reflection import Inspector

models.Base.metadata.create_all(bind=engine)

from sqlalchemy import inspect
from sqlalchemy.types import Integer, String, Float, Boolean, DateTime

def get_column_type_str(col_type):
    if isinstance(col_type, Integer):
        return "INTEGER"
    elif isinstance(col_type, String):
        return "VARCHAR"
    elif isinstance(col_type, Float):
        return "FLOAT"
    elif isinstance(col_type, Boolean):
        return "BOOLEAN"
    elif isinstance(col_type, DateTime):
        return "TIMESTAMP"
    return None

try:
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    with engine.begin() as conn:
        for table_name, table in models.Base.metadata.tables.items():
            if table_name in existing_tables:
                existing_columns = [col['name'] for col in inspector.get_columns(table_name)]
                for col_name, column in table.columns.items():
                    if col_name not in existing_columns:
                        type_str = get_column_type_str(column.type)
                        if type_str:
                            default_clause = ""
                            if isinstance(column.type, Boolean):
                                default_clause = " DEFAULT true" if col_name == "service_active" else " DEFAULT false"
                            
                            sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {type_str}{default_clause}"
                            print(f"Executing migration: {sql}")
                            conn.execute(text(sql))
except Exception as e:
    print("Auto-migration failed:", e)

# Auto-seed admin user if missing
try:
    with engine.connect() as conn:
        db = database.SessionLocal()
        admin_username = os.environ.get("ADMIN_USERNAME", "admin")
        admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
        
        admin = db.query(models.Admin).filter(models.Admin.username == admin_username).first()
        if not admin:
            hashed_password = auth.get_password_hash(admin_password)
            new_admin = models.Admin(username=admin_username, password_hash=hashed_password)
            db.add(new_admin)
            db.commit()
            print(f"Auto-seeded admin user: {admin_username}")
        db.close()
except Exception as e:
    print("Auto-seed admin failed:", e)

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

from fastapi import HTTPException
from fastapi.responses import RedirectResponse

@app.get("/{url_path:path}")
def redirect_malformed_url(url_path: str):
    if url_path.startswith("http://") or url_path.startswith("https://"):
        return RedirectResponse(url=url_path)
    raise HTTPException(status_code=404, detail="Not Found")
