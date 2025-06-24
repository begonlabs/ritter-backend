from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


class SystemSettingSchema(BaseModel):
    id: UUID
    category: str
    key: str
    value: Optional[str] = None
    value_type: str = "string"
    description: Optional[str] = None
    is_public: bool = False
    is_encrypted: bool = False
    validation_rules: Optional[Dict[str, Any]] = None
    default_value: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UpdateSystemSettingRequest(BaseModel):
    value: str
    description: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "value": "smtp.gmail.com",
                "description": "Gmail SMTP server for sending emails"
            }
        }


class CreateSystemSettingRequest(BaseModel):
    category: str
    key: str
    value: Optional[str] = None
    value_type: str = "string"
    description: Optional[str] = None
    is_public: bool = False
    is_encrypted: bool = False
    validation_rules: Optional[Dict[str, Any]] = None
    default_value: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "category": "email",
                "key": "smtp_host",
                "value": "smtp.gmail.com",
                "value_type": "string",
                "description": "SMTP server hostname",
                "is_public": False
            }
        }


class SystemSettingsListResponse(BaseModel):
    settings: Dict[str, List[SystemSettingSchema]]