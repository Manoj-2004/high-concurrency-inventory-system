from datetime import datetime
from decimal import Decimal
from typing import List

from pydantic import BaseModel, EmailStr, Field


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
    user_id: int
    status: str
    total_amount: Decimal
    created_at: datetime
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True