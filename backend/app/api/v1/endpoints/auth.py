from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.config import settings
from app.core.database import get_database
from app.core.security import verify_password, create_access_token
from app.crud.user import UserCRUD
from app.models.user import UserCreate, UserResponse
from app.schemas.auth import Token, LoginRequest

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db=Depends(get_database)):
    """
    Register a new user.

    - **email**: Valid email address
    - **username**: Unique username (3-50 characters)
    - **first_name**: User's first name
    - **last_name**: User's last name
    - **password**: Strong password (min 8 characters)
    """
    user_crud = UserCRUD(db)

    # Check if email already exists
    if await user_crud.exists_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username already exists
    if await user_crud.exists_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create user
    user = await user_crud.create(user_data)

    # Convert to response model
    return UserResponse(
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


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db=Depends(get_database)):
    """
    Login with email/username and password.

    - **identifier**: Email address or username
    - **password**: User password

    Returns a JWT access token.
    """
    user_crud = UserCRUD(db)

    # Try to find user by email or username
    user = None

    # Check if identifier looks like an email
    if "@" in login_data.identifier:
        user = await user_crud.get_by_email(login_data.identifier)
    else:
        user = await user_crud.get_by_username(login_data.identifier)

    # Verify user exists and password is correct
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Create access token with user information including role
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role.value
        },
        expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")
