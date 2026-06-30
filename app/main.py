from fastapi import FastAPI

from app import models
from app.database import Base, engine

app = FastAPI(
    title="High-Concurrency Inventory System",
    description="FastAPI backend using Redis atomic inventory reservation and PostgreSQL persistence.",
    version="1.0.0",
)

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "High-Concurrency Inventory System API is running"}