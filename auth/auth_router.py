"""
auth_router.py

Updated to support Swagger UI "Authorize" flow using Form Data.
"""

# =====================================================
# IMPORTS
# =====================================================
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm  # CRITICAL: For Swagger compatibility
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from database import SessionLocal
from models import User
from auth.security import hash_password, verify_password
from auth.jwt import create_token


# =====================================================
# Pydantic Request / Response Schemas
# =====================================================

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    """Standard OAuth2 response format for access tokens."""
    access_token: str
    token_type: str = "bearer"


# =====================================================
# ROUTER CONFIGURATION
# =====================================================

# Defined BEFORE the endpoints to avoid NameError
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# =====================================================
# DATABASE DEPENDENCY
# =====================================================

def get_db():
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
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.email).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    # Create new user with hashed password
    new_user = User(
        email=request.email,
        password=hash_password(request.password),
        role="USER"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}


# =====================================================
# LOGIN ENDPOINT (FIXED FOR SWAGGER)
# =====================================================

@router.post("/login", response_model=AuthResponse)
def login_user(
    # Changed from 'LoginRequest' to 'OAuth2PasswordRequestForm'
    # This allows the Swagger "Authorize" popup to work correctly
    request: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticates user and returns JWT token.
    Swagger UI sends data as form-data, mapping email to 'username'.
    """

    # Fetch user from DB using request.username (which holds the email)
    user = (
        db.query(User)
        .filter(User.email == request.username)
        .first()
    )

    # Verify user exists and password is correct
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create JWT token with standard claims
    token = create_token({
        "sub": user.email,      
        "user_id": user.id,     
        "role": user.role       
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }

