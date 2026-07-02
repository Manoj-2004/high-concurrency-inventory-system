from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from uuid import uuid4

from app.models import Order, OrderItem, OrderStatus, Product, User
from app.redis_client import redis_client
from app.schemas import PurchaseRequest
from app.database import SessionLocal
from app.kafka.producer import publish_purchase_event

def purchase_product_kafka(
    purchase_data: PurchaseRequest,
    current_user: User,
    db: Session,
):
    product = (
        db.query(Product)
        .filter(Product.id == purchase_data.product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    redis_key = f"product:{product.id}:stock"

    remaining_stock = redis_client.decrby(
        redis_key,
        purchase_data.quantity,
    )

    if remaining_stock < 0:
        redis_client.incrby(redis_key, purchase_data.quantity)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Out of stock",
        )

    event = {
        "event_id": str(uuid4()),
        "user_id": current_user.id,
        "product_id": product.id,
        "quantity": purchase_data.quantity,
    }

    publish_purchase_event(event)

    return {
        "message": "Purchase accepted and queued for processing."
    }
            
            
def purchase_product(
    purchase_data: PurchaseRequest,
    current_user: User,
    db: Session,
):
    product = db.query(Product).filter(Product.id == purchase_data.product_id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    redis_key = f"product:{product.id}:stock"

    remaining_stock = redis_client.decrby(redis_key, purchase_data.quantity)

    if remaining_stock < 0:
        redis_client.incrby(redis_key, purchase_data.quantity)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Out of stock",
        )

    try:
        total_amount = product.price * purchase_data.quantity

        new_order = Order(
            user_id=current_user.id,
            status=OrderStatus.CONFIRMED.value,
            total_amount=total_amount,
        )

        db.add(new_order)
        db.commit()
        db.refresh(new_order)

        order_item = OrderItem(
            order_id=new_order.id,
            product_id=product.id,
            quantity=purchase_data.quantity,
            price=product.price,
        )
        
        db.add(order_item)

        product.stock = product.stock - purchase_data.quantity

        db.commit()
        db.refresh(new_order)

        return new_order
    
    except Exception:
        db.rollback()
        redis_client.incrby(redis_key, purchase_data.quantity)
        raise
    
def finalize_order_background(
    order_id: int,
    product_id: int,
    quantity: int,
):
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        product = db.query(Product).filter(Product.id == product_id).first()

        if not order or not product:
            return

        product.stock = product.stock - quantity
        order.status = OrderStatus.CONFIRMED.value

        db.commit()

    except Exception:
        db.rollback()
        redis_client.incrby(f"product:{product_id}:stock", quantity)
        raise    

def purchase_product_background(
    purchase_data: PurchaseRequest,
    current_user: User,
    db: Session,
    background_tasks,
):
    product = db.query(Product).filter(Product.id == purchase_data.product_id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    redis_key = f"product:{product.id}:stock"

    remaining_stock = redis_client.decrby(redis_key, purchase_data.quantity)

    if remaining_stock < 0:
        redis_client.incrby(redis_key, purchase_data.quantity)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Out of stock",
        )

    total_amount = product.price * purchase_data.quantity

    new_order = Order(
        user_id=current_user.id,
        status=OrderStatus.PENDING.value,
        total_amount=total_amount,
    )

    db.add(new_order)
    db.flush()

    order_item = OrderItem(
        order_id=new_order.id,
        product_id=product.id,
        quantity=purchase_data.quantity,
        price=product.price,
    )

    db.add(order_item)
    db.commit()
    db.refresh(new_order)

    background_tasks.add_task(
        finalize_order_background,
        new_order.id,
        product.id,
        purchase_data.quantity,
    )

    return new_order