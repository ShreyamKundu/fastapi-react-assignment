# app/services/user_service.py
from sqlalchemy.orm import Session
from app.models.users import User
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
        is_superuser=False
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_in: UserUpdate):
    """
    Update a user's details.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    # Update fields only if they are provided
    if user_in.email:
        user.email = user_in.email
    if user_in.name:
        user.name = user_in.name
    if user_in.password:
        from app.core.security import get_password_hash
        user.hashed_password = get_password_hash(user_in.password)
        
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