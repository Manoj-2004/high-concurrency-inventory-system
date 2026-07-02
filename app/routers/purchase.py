from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User
from app.routers.auth import get_current_user
from app.schemas import PurchaseRequest
from app.services import purchase_service

router = APIRouter(prefix="/purchase", tags=["Purchase"])


@router.post("/", status_code=status.HTTP_202_ACCEPTED)
def purchase_product(
    purchase_data: PurchaseRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if settings.use_kafka:
        return purchase_service.purchase_product_kafka(
            purchase_data,
            current_user,
            db,
        )

    if settings.use_background_tasks:
        return purchase_service.purchase_product_background(
            purchase_data,
            current_user,
            db,
            background_tasks,
        )

    return purchase_service.purchase_product(
        purchase_data,
        current_user,
        db,
    )