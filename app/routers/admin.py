from fastapi import APIRouter, Depends
from app.dependencies import require_admin
from app.models import User
from app.schemas import OrderResponse, OrderStatusUpdate
from app.services import order_service
from sqlalchemy.orm import Session
from app.database import get_db


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)

@router.get("/orders", response_model=list[OrderResponse])
def get_orders(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return order_service.get_all_orders(db)

@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return order_service.get_order_admin(order_id, db)


@router.patch("/orders/{order_id}/status", response_model=OrderResponse)
def update_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return order_service.update_order_status(
        order_id,
        status_update,
        db,
    )