"""
Endpoints de administración.
Solo accesibles para usuarios con rol ADMIN.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.database import get_database
from app.api.dependencies_admin import get_current_admin_user
from app.crud.user import UserCRUD
from app.models.user import (
    UserInDB,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserRole
)

router = APIRouter()


@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_admin: UserInDB = Depends(get_current_admin_user),
    db=Depends(get_database)
):
    """
    Obtener todos los usuarios del sistema.
    Solo accesible para administradores.
    """
    user_crud = UserCRUD(db)
    users = await user_crud.get_all_users(skip=skip, limit=limit)

    return [
        UserResponse(
            _id=str(user.id),
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        for user in users
    ]


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_by_admin(
    user: UserCreate,
    current_admin: UserInDB = Depends(get_current_admin_user),
    db=Depends(get_database)
):
    """
    Crear un nuevo usuario.
    Solo accesible para administradores.

    El administrador puede crear usuarios con rol 'user' o 'admin'.
    """
    user_crud = UserCRUD(db)

    # Verificar si el username ya existe
    existing_user = await user_crud.get_by_username(user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está registrado"
        )

    # Verificar si el email ya existe
    existing_email = await user_crud.get_by_email(user.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )

    # Crear el usuario
    created_user = await user_crud.create(user)

    return UserResponse(
        _id=str(created_user.id),
        email=created_user.email,
        username=created_user.username,
        first_name=created_user.first_name,
        last_name=created_user.last_name,
        role=created_user.role,
        is_active=created_user.is_active,
        created_at=created_user.created_at,
        updated_at=created_user.updated_at
    )


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_admin(
    user_id: str,
    current_admin: UserInDB = Depends(get_current_admin_user),
    db=Depends(get_database)
):
    """
    Eliminar un usuario.
    Solo accesible para administradores.

    No se puede eliminar a sí mismo.
    """
    # Verificar que no se esté eliminando a sí mismo
    if str(current_admin.id) == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puede eliminar su propio usuario"
        )

    user_crud = UserCRUD(db)
    deleted = await user_crud.delete(user_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    return None


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user_by_admin(
    user_id: str,
    user_update: UserUpdate,
    current_admin: UserInDB = Depends(get_current_admin_user),
    db=Depends(get_database)
):
    """
    Actualizar un usuario.
    Solo accesible para administradores.

    El administrador puede cambiar el rol de un usuario.
    """
    user_crud = UserCRUD(db)

    # Si se está actualizando el username, verificar que no exista
    if user_update.username:
        existing_user = await user_crud.get_by_username(user_update.username)
        if existing_user and str(existing_user.id) != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está registrado"
            )

    # Si se está actualizando el email, verificar que no exista
    if user_update.email:
        existing_email = await user_crud.get_by_email(str(user_update.email))
        if existing_email and str(existing_email.id) != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )

    # Actualizar el usuario
    updated_user = await user_crud.update(user_id, user_update)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    return UserResponse(
        _id=str(updated_user.id),
        email=updated_user.email,
        username=updated_user.username,
        first_name=updated_user.first_name,
        last_name=updated_user.last_name,
        role=updated_user.role,
        is_active=updated_user.is_active,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at
    )


@router.get("/stats")
async def get_admin_stats(
    current_admin: UserInDB = Depends(get_current_admin_user),
    db=Depends(get_database)
):
    """
    Obtener estadísticas del sistema.
    Solo accesible para administradores.
    """
    user_crud = UserCRUD(db)

    total_users = await db.users.count_documents({})
    active_users = await db.users.count_documents({"is_active": True})
    admin_users = await db.users.count_documents({"role": UserRole.ADMIN.value})
    regular_users = await db.users.count_documents({"role": UserRole.USER.value})

    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": total_users - active_users,
        "admin_users": admin_users,
        "regular_users": regular_users
    }
