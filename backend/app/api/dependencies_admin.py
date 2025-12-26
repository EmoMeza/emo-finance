"""
Dependencias para rutas de administración.
"""
from fastapi import Depends, HTTPException, status
from app.api.dependencies import get_current_active_user
from app.models.user import UserInDB, UserRole


async def get_current_admin_user(
    current_user: UserInDB = Depends(get_current_active_user)
) -> UserInDB:
    """
    Verifica que el usuario actual sea un administrador.
    Lanza una excepción 403 Forbidden si no lo es.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos de administrador para realizar esta acción"
        )
    return current_user
