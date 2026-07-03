from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import CartItem, Product, User
from app.schemas import CartItemCreate

from uuid import uuid4
from app.kafka.producer import publish_purchase_event

def add_to_cart(cart_data: CartItemCreate, current_user: User, db: Session):
    product = db.query(Product).filter(Product.id == cart_data.product_id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    
    if cart_data.quantity > product.stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only {product.stock} items available",
        )

    existing_item = (
        db.query(CartItem)
        .filter(
            CartItem.user_id == current_user.id,
            CartItem.product_id == cart_data.product_id,
        )
        .first()
    )

    if existing_item:
        new_quantity = existing_item.quantity + cart_data.quantity
        if new_quantity > product.stock:
            raise HTTPException(
                status_code=400,
                detail=f"Only {product.stock} items available",
            )
        existing_item.quantity = new_quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item

    cart_item = CartItem(
        user_id=current_user.id,
        product_id=cart_data.product_id,
        quantity=cart_data.quantity,
    )

    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)

    return cart_item


def get_cart(current_user: User, db: Session):
    return (
        db.query(CartItem)
        .filter(CartItem.user_id == current_user.id)
        .all()
    )


def remove_cart_item(cart_item_id: int, current_user: User, db: Session):
    cart_item = (
        db.query(CartItem)
        .filter(
            CartItem.id == cart_item_id,
            CartItem.user_id == current_user.id,
        )
        .first()
    )

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found",
        )

    db.delete(cart_item)
    db.commit()

    return {"message": "Cart item removed successfully"}


def clear_cart(current_user: User, db: Session):
    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()
    db.commit()

    return {"message": "Cart cleared successfully"}

def checkout_cart(current_user: User, db: Session):
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

    event = {
        "event_id": str(uuid4()),
        "user_id": current_user.id,
        "items": [
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
            }
            for item in cart_items
        ],
    }

    publish_purchase_event(event, event["items"][0]["product_id"])

    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()

    return {
        "message": "Checkout request accepted",
        "event_id": event["event_id"],
    }