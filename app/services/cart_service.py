from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import CartItem, Product, User, Address, PaymentStatus, Payment
from app.schemas import CartItemCreate, CheckoutRequest

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

def checkout_cart(checkout_data: CheckoutRequest, current_user: User, db: Session):
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
        
    address = (
        db.query(Address)
        .filter(
            Address.id == checkout_data.address_id,
            Address.user_id == current_user.id,
        )
        .first()
    )

    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found",
        )

    total_amount = 0

    for cart_item in cart_items:
        product = (
            db.query(Product)
            .filter(Product.id == cart_item.product_id)
            .first()
        )

        total_amount += product.price * cart_item.quantity
    
    event_id = str(uuid4())
    payment = Payment(
        event_id=event_id,
        user_id=current_user.id,
        amount=total_amount,
        status=PaymentStatus.PENDING,
        address_id=address.id,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    return {
        "payment_id": payment.id,
        "event_id": payment.event_id,
        "amount": payment.amount,
        "status": payment.status,
    }