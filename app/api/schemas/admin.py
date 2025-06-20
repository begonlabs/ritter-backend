from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class AdminUserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    role_id: Optional[str] = None
    role_name: Optional[str] = None
    status: str
    last_login_at: Optional[datetime] = None
    email_verified_at: Optional[datetime] = None
    two_factor_enabled: bool = False
    invited_by: Optional[str] = None
    invited_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AdminUserDetailResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    role_id: Optional[str] = None
    role: Optional[Dict[str, Any]] = None
    status: str
    last_login_at: Optional[datetime] = None
    email_verified_at: Optional[datetime] = None
    two_factor_enabled: bool = False
    invited_by: Optional[str] = None
    invited_at: Optional[datetime] = None
    password_set_at: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class AdminUsersListResponse(BaseModel):
    users: List[AdminUserResponse]
    pagination: Dict[str, Any]


class AdminCreateUserRequest(BaseModel):
    email: EmailStr
    full_name: str
    role_id: UUID


class AdminUpdateUserRequest(BaseModel):
    full_name: Optional[str] = None
    role_id: Optional[UUID] = None
    status: Optional[str] = None


class AdminRoleResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    is_system_role: bool = False
    permissions: List[str] = []
    user_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AdminRoleDetailResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    is_system_role: bool = False
    permissions: List[Dict[str, Any]] = []
    user_count: int = 0
    created_at: datetime
    updated_at: datetime


class AdminRolesListResponse(BaseModel):
    roles: List[AdminRoleResponse]


class AdminCreateRoleRequest(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: List[str]


class AdminUpdateRoleRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None


class AdminPermissionResponse(BaseModel):
    id: str
    name: str
    description: str
    resource: str
    action: str


class AdminPermissionCategoryResponse(BaseModel):
    name: str
    label: str
    permission_count: int


class AdminPermissionsResponse(BaseModel):
    permissions: Dict[str, List[AdminPermissionResponse]]


class AdminPermissionCategoriesResponse(BaseModel):
    categories: List[AdminPermissionCategoryResponse]


class AdminActivityLogResponse(BaseModel):
    id: str
    user_id: str
    user_name: str
    activity_type: str
    action: str
    description: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    changes: Optional[Dict[str, Any]] = None
    execution_time_ms: int = 0
    timestamp: datetime


class AdminActivityLogsResponse(BaseModel):
    activities: List[AdminActivityLogResponse]
    pagination: Dict[str, Any]


class AdminActivitySummaryResponse(BaseModel):
    summary: Dict[str, Any]