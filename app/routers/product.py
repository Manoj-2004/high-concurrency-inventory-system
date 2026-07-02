from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ProductCreate, ProductResponse
from app.services import product_service
from app.dependencies import require_admin
from app.models import User

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return product_service.create_product(product_data, db)


@router.get("/", response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return product_service.get_products(db)

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = product_service.get_product(product_id, db)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return product