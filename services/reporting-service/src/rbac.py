from typing import Callable

from fastapi import Depends, HTTPException, status


def require_roles(*allowed_roles: str, get_current_user) -> Callable:
    async def _check(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "Permisos insuficientes para esta operación",
            )
        return current_user

    return _check
