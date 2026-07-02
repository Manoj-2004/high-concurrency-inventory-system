from datetime import datetime, timedelta, timezone
from app.services.token_service import blacklist_token, is_token_blacklisted
from fastapi import HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.models import User
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas import UserCreate
from jose import JWTError, jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def logout_user(access_token: str, refresh_token: str):
    blacklist_token(access_token)
    blacklist_token(refresh_token)

    return {
        "message": "Logged out successfully"
    }

def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )
    to_encode.update({"exp": expire, "type": "refresh"})

    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    
def refresh_access_token(refresh_token: str) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
    )

    if is_token_blacklisted(refresh_token):
        raise credentials_exception

    try:
        payload = jwt.decode(
            refresh_token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        user_id = payload.get("sub")
        token_type = payload.get("type")

        if user_id is None or token_type != "refresh":
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    new_access_token = create_access_token(data={"sub": str(user_id)})

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def register_user(user_data: UserCreate, db: Session) -> User:
    existing_user = db.query(User).filter(User.email == user_data.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def login_user(
    form_data: OAuth2PasswordRequestForm,
    db: Session,
) -> dict:
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    refresh_token = create_refresh_token(data={"sub": str(user.id), "role": user.role.value})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }