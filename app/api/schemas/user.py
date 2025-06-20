from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID



class RoleSchema(BaseModel):
    id: UUID
    name: str
    permissions: List[str]


class UserProfileResponse(BaseModel):
    user: "UserProfile"


class UserProfile(BaseModel):
    id: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[RoleSchema] = None
    last_activity_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    user_metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "Juan Pérez",
                "metadata": {
                    "phone": "+1234567890",
                    "preferences": {
                        "theme": "dark",
                        "language": "es"
                    }
                }
            }
        }


class InviteUserRequest(BaseModel):
    email: EmailStr
    full_name: str
    role_id: UUID

    class Config:
        json_schema_extra = {
            "example": {
                "email": "newuser@usuario.com",
                "full_name": "New User",
                "role_id": "da415454-e3ce-450a-936e-3e6c370c495e"
            }
        }


class InviteUserResponse(BaseModel):
    message: str
    user: Dict[str, Any]