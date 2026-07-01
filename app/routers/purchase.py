from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.routers.auth import get_current_user
from app.schemas import OrderResponse, PurchaseRequest
from app.services import purchase_service

router = APIRouter(prefix="/purchase", tags=["Purchase"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def purchase_product(
    purchase_data: PurchaseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return purchase_service.purchase_product(purchase_data, current_user, db)