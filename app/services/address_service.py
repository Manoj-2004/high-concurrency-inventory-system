from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Address, User
from app.schemas import AddressCreate, AddressUpdate


def create_address(address_data: AddressCreate, current_user: User, db: Session):
    if address_data.is_default:
        db.query(Address).filter(Address.user_id == current_user.id).update(
            {"is_default": False}
        )

    address = Address(
        user_id=current_user.id,
        **address_data.model_dump(),
    )

    db.add(address)
    db.commit()
    db.refresh(address)

    return address

def update_address(
    address_id: int,
    address_data: AddressUpdate,
    current_user: User,
    db: Session,
):
    address = get_address(address_id, current_user, db)

    update_data = address_data.model_dump(exclude_unset=True)

    if update_data.get("is_default") is True:
        db.query(Address).filter(Address.user_id == current_user.id).update(
            {"is_default": False}
        )

    for field, value in update_data.items():
        setattr(address, field, value)

    db.commit()
    db.refresh(address)

    return address

def get_my_addresses(current_user: User, db: Session):
    return db.query(Address).filter(Address.user_id == current_user.id).all()


def get_address(address_id: int, current_user: User, db: Session):
    address = (
        db.query(Address)
        .filter(Address.id == address_id, Address.user_id == current_user.id)
        .first()
    )
    
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    return address


def delete_address(address_id: int, current_user: User, db: Session):
    address = get_address(address_id, current_user, db)

    db.delete(address)
    db.commit()

    return {"message": "Address deleted successfully"}