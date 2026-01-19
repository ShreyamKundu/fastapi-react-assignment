from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.users import User, UserRole
from app.schemas.user import UserCreate
from app.core.security import get_password_hash
from app.schemas.user import UserUpdate 

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user(db: Session, user_id: int):
    """
    Get a user by their unique ID.
    """
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user: UserCreate):
    """
    Creates a new user in the database.
    
    1. Hashes the password.
    2. Creates the DB model instance.
    3. Commits the transaction.
    4. Refreshes the instance to get the generated ID.
    """
    hashed_password = get_password_hash(user.password)
    
    db_user = User(
        email=user.email,
        name=user.name,
        hashed_password=hashed_password,
        is_active=True,
        role=UserRole.USER
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_in: UserUpdate):
    """
    Update a user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    # Check if new email already exists
    if user_in.email is not None and user_in.email != user.email:
        existing_user = get_user_by_email(db, email=user_in.email)
        if existing_user:
            return None 

    update_data = user_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if field == "password":
            hashed_password = get_password_hash(value)
            setattr(user, "hashed_password", hashed_password)
        else:
            setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    """
    Delete a user by ID.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
        
    db.delete(user)
    db.commit()
    return user

def get_users(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    search: str | None = None, 
    role: UserRole | None = None
) -> list[User]:
    """
    Fetch users with optional search and role filtering.
    """
    query = db.query(User)

    if role:
        query = query.filter(User.role == role)

    if search:
        search_pattern = f"%{search}%" 
        query = query.filter(
            or_(
                User.name.ilike(search_pattern),
                User.email.ilike(search_pattern)
            )
        )

    return query.offset(skip).limit(limit).all()