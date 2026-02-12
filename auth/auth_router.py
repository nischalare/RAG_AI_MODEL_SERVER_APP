"""
auth_router.py

This file handles:

1. User Registration
2. User Login
3. JWT Token Generation

It follows clean architecture principles:
- Password hashing is handled in auth.security
- JWT creation is handled in auth.jwt
- Database access via dependency injection
"""

# =====================================================
# IMPORTS
# =====================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from database import SessionLocal
from models import User
from auth.security import hash_password, verify_password
from auth.jwt import create_token


# =====================================================
# ROUTER CONFIGURATION
# =====================================================

# All endpoints in this file will start with /auth
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# =====================================================
# Pydantic Request / Response Schemas
# =====================================================

class RegisterRequest(BaseModel):
    """
    Schema for user registration request.

    EmailStr automatically validates email format.
    """
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    """
    Schema for login request.
    """
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """
    Schema for login response.

    Returns:
    - JWT access token
    - Token type (Bearer)
    """
    access_token: str
    token_type: str = "bearer"


# =====================================================
# DATABASE DEPENDENCY
# =====================================================

def get_db():
    """
    Provides a database session to endpoints.

    Why we use this:
    - Ensures DB connection is properly opened
    - Automatically closes after request
    - Prevents connection leaks
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =====================================================
# REGISTER ENDPOINT
# =====================================================

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Registers a new user.

    Steps:
    1. Check if user already exists
    2. Hash password securely
    3. Store user in database
    """

    # Check if email already exists
    existing_user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if existing_user:
        # Prevent duplicate accounts
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    # Create new user instance
    new_user = User(
        email=request.email,
        password=hash_password(request.password),  # Secure hashing
        role="USER"  # Default role
    )

    # Save to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}


# =====================================================
# LOGIN ENDPOINT
# =====================================================

@router.post("/login", response_model=AuthResponse)
def login_user(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticates user and returns JWT token.

    Steps:
    1. Find user by email
    2. Verify password
    3. Generate JWT token
    """

    # Fetch user from DB
    user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    # If user not found OR password invalid
    if not user or not verify_password(
        request.password,
        user.password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Create JWT token
    token = create_token({
        "sub": user.email,      # Subject (standard JWT field)
        "user_id": user.id,     # Custom claim
        "role": user.role       # Used for role-based access
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }
