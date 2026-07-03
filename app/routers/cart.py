from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.auth import get_current_user
from app.models import User
from app.schemas import (
    CartItemCreate,
    CartItemResponse,
    CartResponse,
    CheckoutRequest
)
from app.services import cart_service

router = APIRouter(
    prefix="/cart",
    tags=["Cart"],
)


@router.post(
    "/items",
    response_model=CartItemResponse,
)
def add_to_cart(
    cart_data: CartItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return cart_service.add_to_cart(
        cart_data,
        current_user,
        db,
    )


@router.get(
    "",
    response_model=list[CartItemResponse],
)
def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return cart_service.get_cart(
        current_user,
        db,
    )


@router.delete("/items/{cart_item_id}")
def remove_cart_item(
    cart_item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return cart_service.remove_cart_item(
        cart_item_id,
        current_user,
        db,
    )


@router.delete("")
def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return cart_service.clear_cart(
        current_user,
        db,
    )
    
@router.post("/checkout")
def checkout_cart(
    checkout_data: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return cart_service.checkout_cart(checkout_data, current_user, db)