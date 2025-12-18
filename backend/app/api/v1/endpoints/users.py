from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.database import get_database
from app.crud.user import UserCRUD
from app.models.user import UserInDB, UserResponse, UserUpdate
from app.api.dependencies import get_current_active_user

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Get current user information.

    Returns the authenticated user's profile.
    """
    return UserResponse(
        _id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_database)
):
    """
    Get all users (paginated).

    Requires authentication.
    """
    user_crud = UserCRUD(db)
    users = await user_crud.get_all(skip=skip, limit=limit)

    return [
        UserResponse(
            _id=str(user.id),
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        for user in users
    ]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_database)
):
    """
    Get a user by ID.

    Requires authentication.
    """
    user_crud = UserCRUD(db)
    user = await user_crud.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(
        _id=str(user.id),
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_database)
):
    """
    Update a user by ID.

    Users can only update their own profile.
    """
    # Check if user is updating their own profile
    if str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )

    user_crud = UserCRUD(db)

    # Check for email uniqueness if being updated
    if user_update.email and user_update.email != current_user.email:
        if await user_crud.exists_by_email(user_update.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    # Check for username uniqueness if being updated
    if user_update.username and user_update.username != current_user.username:
        if await user_crud.exists_by_username(user_update.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

    updated_user = await user_crud.update(user_id, user_update)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(
        _id=str(updated_user.id),
        email=updated_user.email,
        username=updated_user.username,
        first_name=updated_user.first_name,
        last_name=updated_user.last_name,
        is_active=updated_user.is_active,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_database)
):
    """
    Delete a user by ID.

    Users can only delete their own account.
    """
    # Check if user is deleting their own account
    if str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user"
        )

    user_crud = UserCRUD(db)
    deleted = await user_crud.delete(user_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return None
