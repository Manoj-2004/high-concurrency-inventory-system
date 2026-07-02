from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.product import router as products_router
from app.routers.purchase import router as purchase_router
from app.routers.inventory import router as inventory_router

app = FastAPI(
    title="High-Concurrency Inventory System",
    description="FastAPI backend using Redis atomic inventory reservation and PostgreSQL persistence.",
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(purchase_router)
app.include_router(inventory_router)

@app.get("/")
def root():
    return {"message": "High-Concurrency Inventory System API is running"}