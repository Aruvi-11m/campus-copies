from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from . import models
from .database import engine
from .routers import auth_router, orders_router, admin_router, agent_router
import os

models.Base.metadata.create_all(bind=engine)

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
