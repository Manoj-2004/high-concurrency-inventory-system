from fastapi import HTTPException
from sqlalchemy.orm import joinedload, Session

from app.models import Order, User
from app.schemas import OrderStatusUpdate


def get_my_orders(current_user: User, db: Session):
    return (
        db.query(Order)
        .filter(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )


def get_order(order_id: int, current_user: User, db: Session):
    order = (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(
            Order.id == order_id,
            Order.user_id == current_user.id,
        )
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    return order

def get_all_orders(db: Session):
    return (
        db.query(Order)
        .options(joinedload(Order.items))
        .order_by(Order.created_at.desc())
        .all()
    )
    
def get_order_admin(order_id: int, db: Session):

    order = (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(Order.id == order_id)
        .first()
    )

    if not order:
        raise HTTPException(404, "Order not found")

    return order

def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: Session,
):

    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .first()
    )

    if not order:
        raise HTTPException(404, "Order not found")

    order.status = status_update.status.value

    db.commit()
    db.refresh(order)

    return order