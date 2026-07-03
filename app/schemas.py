from datetime import datetime
from decimal import Decimal
from typing import List

from pydantic import BaseModel, EmailStr, Field
from app.models import OrderStatus

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class LogoutRequest(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    description: str | None = None
    price: Decimal = Field(..., gt=0)
    category: str = Field(..., min_length=2, max_length=100)
    stock: int = Field(..., ge=0)


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: Decimal
    category: str
    stock: int
    created_at: datetime

    class Config:
        from_attributes = True


class PurchaseRequest(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=10)


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: Decimal

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    status: str
    total_amount: Decimal
    created_at: datetime

    shipping_full_name: str | None
    shipping_phone: str | None
    shipping_address_line_1: str | None
    shipping_address_line_2: str | None
    shipping_city: str | None
    shipping_state: str | None
    shipping_postal_code: str | None
    shipping_country: str | None

    items: list[OrderItemResponse]

    class Config:
        from_attributes = True
        
class CartItemCreate(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(default=1, gt=0)

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    items: list[CartItemResponse]
    
    
class AddressCreate(BaseModel):
    full_name: str
    phone: str
    address_line_1: str
    address_line_2: str | None = None
    city: str
    state: str
    postal_code: str
    country: str = "India"
    is_default: bool = False


class AddressResponse(AddressCreate):
    id: int

    class Config:
        from_attributes = True
        
class AddressUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    is_default: bool | None = None
    
class CheckoutRequest(BaseModel):
    address_id: int = Field(..., gt=0)
    
class OrderStatusUpdate(BaseModel):
    status: OrderStatus