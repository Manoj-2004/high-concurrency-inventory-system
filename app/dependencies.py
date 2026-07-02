from fastapi import Depends, HTTPException, status

from app.models import User, UserRole
from app.routers.auth import get_current_user


def require_role(required_role: UserRole):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{required_role.value} role required",
            )

        return current_user

    return role_checker


require_admin = require_role(UserRole.ADMIN)