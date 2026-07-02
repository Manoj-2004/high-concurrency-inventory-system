from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.config import settings
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, UserResponse
from app.services import auth_service
from app.schemas import RefreshTokenRequest
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.services.token_service import is_token_blacklisted
from app.schemas import RefreshTokenRequest, LogoutRequest

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate user credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        user_id: str | None = payload.get("sub")
        role: str = payload.get("role")
        
        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()

    if user is None:
        raise credentials_exception

    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    return auth_service.register_user(user_data, db)

@router.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    return auth_service.login_user(form_data, db)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/refresh")
def refresh_token(token_data: RefreshTokenRequest):
    return auth_service.refresh_access_token(token_data.refresh_token)

@router.post("/logout")
def logout(
    logout_data: LogoutRequest,
    token: str = Depends(oauth2_scheme),
):
    return auth_service.logout_user(
        access_token=token,
        refresh_token=logout_data.refresh_token,
    )