from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.inventory_service import sync_redis_stock_from_db

from app.dependencies import require_admin
from app.models import User

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
)


@router.post("/sync-redis")
def sync_redis(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return sync_redis_stock_from_db(db)