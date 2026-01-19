from enum import Enum
from pydantic import BaseModel, EmailStr, ConfigDict

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    name: str | None = None
    password: str | None = None
    role: UserRole | None = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    role: UserRole
    
    model_config = ConfigDict(from_attributes=True)