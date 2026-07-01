from fastapi import FastAPI

from app.routers.auth import router as auth_router

app = FastAPI(
    title="High-Concurrency Inventory System",
    description="FastAPI backend using Redis atomic inventory reservation and PostgreSQL persistence.",
    version="1.0.0",
)

app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "High-Concurrency Inventory System API is running"}