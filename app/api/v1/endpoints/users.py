from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.users import User, UserRole 
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import (
    create_user, 
    get_user_by_email, 
    update_user, 
    delete_user, 
    get_users
)
from app.api.deps import get_current_user, get_current_admin 

router = APIRouter()

# ADMIN DASHBOARD (GET ALL)
@router.get("/", response_model=list[UserResponse])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    role: Optional[UserRole] = None,
    current_user: User = Depends(get_current_admin)
) -> Any:
    """
    Retrieve all users.
    - Only Admins can access this.
    - Supports Pagination (skip, limit).
    - Supports Search (name or email).
    - Supports Filtering (role).
    """
    users = get_users(
        db, 
        skip=skip, 
        limit=limit, 
        search=search, 
        role=role
    )
    return users

# REGISTRATION (PUBLIC)
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user_in: UserCreate, 
    db: Session = Depends(get_db)
) -> Any:
    """
    Register a new user.
    """
    user = get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = create_user(db, user=user_in)
    return user

# PROFILE (Authenticated USER)
@router.get("/me", response_model=UserResponse)
def read_user_me(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get current logged-in user information.
    """
    return current_user

# UPDATE (OWNER ONLY)
@router.put("/{user_id}", response_model=UserResponse)
def update_user_endpoint(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update a user.
    Only Admins can change roles.
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )

    # If a normal user tries to send "role": "admin", we block them.
    if user_in.role is not None and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot assign roles. Please contact an admin."
        )
        
    user = update_user(db, user_id, user_in)
    
    if not user:
        raise HTTPException(
            status_code=400, 
            detail="Update failed. User not found or email already exists."
        )
    return user

# DELETE (ADMIN ONLY)
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
) -> None:
    """
    Delete a user.
    """
    user = delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return None