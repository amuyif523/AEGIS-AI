from typing import Iterable, List
from fastapi import Depends, HTTPException, status
from . import models
from .auth import get_current_user


def require_roles(allowed_roles: Iterable[models.UserRole]):
    """
    Dependency factory to enforce role membership.
    """

    def _dependency(current_user: models.User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized for this action",
            )
        return current_user

    return _dependency


admin_roles: List[models.UserRole] = [
    models.UserRole.ADMIN,
    models.UserRole.SYS_ADMIN,
    models.UserRole.COMMAND,
    models.UserRole.NATIONAL_SUPERVISOR,
]

dispatcher_roles: List[models.UserRole] = admin_roles + [
    models.UserRole.POLICE,
    models.UserRole.FIRE,
    models.UserRole.MEDICAL,
    models.UserRole.TRAFFIC,
    models.UserRole.DISASTER,
    models.UserRole.MILITARY,
]
