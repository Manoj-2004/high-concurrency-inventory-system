from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.inventory_service import sync_redis_stock_from_db

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
)


@router.post("/sync-redis")
def sync_redis(db: Session = Depends(get_db)):
    return sync_redis_stock_from_db(db)