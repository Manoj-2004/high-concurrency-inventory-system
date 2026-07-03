from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.kafka.producer import publish_purchase_event
from app.models import CartItem, Payment, PaymentStatus, User, Product
from uuid import uuid4


def mark_payment_success(payment_id: int, current_user: User, db: Session):
    payment = (
        db.query(Payment)
        .filter(
            Payment.id == payment_id,
            Payment.user_id == current_user.id,
        )
        .first()
    )

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.status != PaymentStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment is already processed",
        )

    cart_items = (
        db.query(CartItem)
        .filter(CartItem.user_id == current_user.id)
        .all()
    )

    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty",
        )

    current_total = 0

    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        current_total += product.price * item.quantity

    if current_total != payment.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart total changed after checkout. Please checkout again.",
        )
    
    event = {
        "event_id": payment.event_id,
        "user_id": current_user.id,
        "address_id": payment.address_id,
        "items": [
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
            }
            for item in cart_items
        ],
    }

    payment.gateway_transaction_id = f"SIM-{uuid4()}"
    payment.status = PaymentStatus.SUCCESS
    
    
    db.commit()

    publish_purchase_event(event, event["items"][0]["product_id"])

    return {
        "message": "Payment successful. Order processing started.",
        "event_id": payment.event_id,
    }

def mark_payment_failed(payment_id: int, current_user: User, db: Session):
    payment = (
        db.query(Payment)
        .filter(
            Payment.id == payment_id,
            Payment.user_id == current_user.id,
        )
        .first()
    )

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.status != PaymentStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail="Payment already processed",
        )

    payment.status = PaymentStatus.FAILED

    db.commit()

    return {
        "message": "Payment marked as failed"
    }
    
def get_payment(payment_id: int, current_user: User, db: Session):
    payment = (
        db.query(Payment)
        .filter(
            Payment.id == payment_id,
            Payment.user_id == current_user.id,
        )
        .first()
    )

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found",
        )

    return payment