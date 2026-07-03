from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.routers.auth import get_current_user
from app.schemas import AddressCreate, AddressResponse, AddressUpdate
from app.services import address_service

router = APIRouter(
    prefix="/addresses",
    tags=["Addresses"],
)


@router.post("/", response_model=AddressResponse)
def create_address(
    address_data: AddressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return address_service.create_address(address_data, current_user, db)


@router.get("/", response_model=list[AddressResponse])
def get_my_addresses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return address_service.get_my_addresses(current_user, db)


@router.get("/{address_id}", response_model=AddressResponse)
def get_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return address_service.get_address(address_id, current_user, db)


@router.delete("/{address_id}")
def delete_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return address_service.delete_address(address_id, current_user, db)

@router.put("/{address_id}", response_model=AddressResponse)
def update_address(
    address_id: int,
    address_data: AddressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return address_service.update_address(
        address_id,
        address_data,
        current_user,
        db,
    )