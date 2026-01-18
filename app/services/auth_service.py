from sqlalchemy.orm import Session
from app.services.user_service import get_user_by_email
from app.core.security import verify_password

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    
    if not user:
        return False
        
    if not verify_password(password, user.hashed_password):
        return False
        
    return user