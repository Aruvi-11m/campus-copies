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

@app.get("/public/debug-storage")
def debug_storage():
    import json
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    
    sa_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    folder_id = os.environ.get("GOOGLE_DRIVE_FOLDER_ID")
    
    result = {
        "sa_json_present": sa_json is not None,
        "sa_json_length": len(sa_json) if sa_json else 0,
        "folder_id_present": folder_id is not None,
        "folder_id": folder_id,
        "drive_service_initialization": "Not tested"
    }
    
    if sa_json:
        try:
            sa_info = json.loads(sa_json)
            result["sa_client_email"] = sa_info.get("client_email")
            
            creds = service_account.Credentials.from_service_account_info(
                sa_info, scopes=['https://www.googleapis.com/auth/drive']
            )
            service = build('drive', 'v3', credentials=creds)
            # Try to fetch some files from drive to verify credentials
            files_res = service.files().list(pageSize=1).execute()
            result["drive_service_initialization"] = "Success"
            result["can_list_files"] = True
        except Exception as e:
            result["drive_service_initialization"] = "Failed"
            result["error"] = str(e)
            
    return result
