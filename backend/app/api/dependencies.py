from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.database import get_database
from app.core.security import decode_access_token
from app.crud.user import UserCRUD
from app.models.user import UserInDB

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db=Depends(get_database)
) -> UserInDB:
    """
    Dependency to get the current authenticated user.

    Validates the JWT token and returns the user from the database.
    Raises HTTPException if token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode token
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise credentials_exception

    # Get user_id from token
    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # Get user from database
    user_crud = UserCRUD(db)
    user = await user_crud.get_by_id(user_id)

    if user is None:
        raise credentials_exception

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    return user


async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
    """
    Dependency to get the current active user.

    Additional check to ensure user is active.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user
