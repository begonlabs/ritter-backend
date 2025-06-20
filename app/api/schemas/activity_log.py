from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID



class LogActivityRequest(BaseModel):
    activity_type: str
    action: str
    description: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "activity_type": "user_action",
                "action": "profile_update",
                "description": "User updated their profile information",
                "resource_type": "user_profile",
                "resource_id": "123e4567-e89b-12d3-a456-426614174000",
                "metadata": {
                    "fields_updated": ["full_name", "phone"],
                    "ip_address": "192.168.1.1"
                }
            }
        }


class LogActivityResponse(BaseModel):
    message: str
    activity_id: UUID
    logged_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Activity logged successfully",
                "activity_id": "123e4567-e89b-12d3-a456-426614174000",
                "logged_at": "2024-01-15T10:30:00Z"
            }
        }


class ActivityLogSchema(BaseModel):
    id: UUID
    user_id: UUID
    activity_type: str
    action: str
    description: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = Field(alias="activity_metadata")
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True 