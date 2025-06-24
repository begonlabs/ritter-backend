from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


class NotificationSchema(BaseModel):
    id: UUID
    type: str
    title: str
    message: str
    priority: int = 0
    is_read: bool = False
    read_at: Optional[datetime] = None
    action_url: Optional[str] = None
    action_text: Optional[str] = None
    action_data: Optional[Dict[str, Any]] = None
    related_type: Optional[str] = None
    related_id: Optional[UUID] = None
    created_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationsListResponse(BaseModel):
    notifications: List[NotificationSchema]
    unread_count: int
    pagination: Dict[str, Any]


class CreateNotificationRequest(BaseModel):
    user_id: UUID
    type: str
    title: str
    message: str
    priority: int = 0
    action_url: Optional[str] = None
    action_text: Optional[str] = None
    action_data: Optional[Dict[str, Any]] = None
    related_type: Optional[str] = None
    related_id: Optional[UUID] = None
    expires_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "type": "system_update",
                "title": "System Maintenance",
                "message": "System will be under maintenance tonight from 2-4 AM",
                "priority": 2,
                "action_url": "/maintenance",
                "action_text": "View Details"
            }
        }