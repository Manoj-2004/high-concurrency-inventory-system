from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.product import router as products_router
from app.routers.purchase import router as purchase_router
from app.routers.inventory import router as inventory_router
from app.routers.cart import router as cart_router
from app.routers.address import router as address_router
from app.routers.payment import router as payment_router
from app.routers.order import router as order_router
from app.routers.admin import router as admin_router


app = FastAPI(
    title="High-Concurrency Inventory System",
    description="FastAPI backend using Redis atomic inventory reservation and PostgreSQL persistence.",
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(purchase_router)
app.include_router(inventory_router)
app.include_router(cart_router)
app.include_router(address_router)
app.include_router(payment_router)
app.include_router(order_router)
app.include_router(admin_router)



@app.get("/")
def root():
    return {"message": "High-Concurrency Inventory System API is running"}