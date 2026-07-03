from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.routers.auth import get_current_user
from app.services import payment_service

router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


@router.post("/{payment_id}/success")
def payment_success(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return payment_service.mark_payment_success(
        payment_id,
        current_user,
        db,
    )


@router.post("/{payment_id}/failed")
def payment_failed(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return payment_service.mark_payment_failed(
        payment_id,
        current_user,
        db,
    )


@router.get("/{payment_id}")
def get_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return payment_service.get_payment(
        payment_id,
        current_user,
        db,
    )