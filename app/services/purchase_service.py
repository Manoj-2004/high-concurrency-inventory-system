from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Order, OrderItem, OrderStatus, Product, User
from app.redis_client import redis_client
from app.schemas import PurchaseRequest


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