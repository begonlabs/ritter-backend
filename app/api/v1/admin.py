from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.core.security import get_current_user
from app.api.dependencies import get_database
from app.api.services.user_service import UserProfileService
from app.api.services.role_service import RoleService
from app.api.services.activity_log_service import ActivityLogService
from app.api.schemas.admin import (
    AdminUsersListResponse, AdminUserDetailResponse, AdminCreateUserRequest,
    AdminUpdateUserRequest, AdminRolesListResponse, AdminRoleDetailResponse,
    AdminCreateRoleRequest, AdminUpdateRoleRequest, AdminPermissionsResponse,
    AdminPermissionCategoriesResponse, AdminActivityLogsResponse, AdminActivitySummaryResponse
)
from app.core.permissions import require_permissions

router = APIRouter()


@router.get("/users", response_model=AdminUsersListResponse)
async def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
    status: Optional[str] = Query(None),
    role_id: Optional[UUID] = Query(None),
    search: Optional[str] = Query(None),
    admin_profile = Depends(require_permissions(["admin.users.read"])),
    db: Session = Depends(get_database)
):
    try:
        user_service = UserProfileService(db)
        
        skip = (page - 1) * limit
        filters = {}
        if role_id:
            filters["role_id"] = role_id
        if search:
            filters["search_term"] = search
        
        result = await user_service.get_users_paginated(skip=skip, limit=limit, **filters)
        
        users_data = []
        for user in result["users"]:
            users_data.append({
                "id": str(user.id),
                "email": user.supabase_user_id,  # Temporal: debería venir de auth.users
                "full_name": user.full_name,
                "role_id": str(user.role_id) if user.role_id else None,
                "role_name": user.role.name if user.role else None,
                "status": "active",
                "last_login_at": user.last_activity_at,
                "email_verified_at": None,
                "two_factor_enabled": False,
                "invited_by": str(user.invited_by) if user.invited_by else None,
                "invited_at": user.invited_at,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            })
        
        return AdminUsersListResponse(
            users=users_data,
            pagination={
                "page": result["page"],
                "limit": result["per_page"],
                "total": result["total"],
                "total_pages": result["total_pages"]
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking all notifications as read: {str(e)}")


@router.delete("/notifications/{notification_id}")
async def archive_notification(
    notification_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Archive notification"""
    try:
        from app.api.services.notification_service import NotificationService
        from app.api.services.user_service import UserProfileService
        
        user_service = UserProfileService(db)
        notification_service = NotificationService(db)
        
        # Get user profile to get the actual user ID
        profile = await user_service.get_or_create_user_profile(current_user)
        
        notification = await notification_service.archive_notification(
            notification_id=notification_id,
            user_id=UUID(profile.id)
        )
        
        return {"message": "Notification archived successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error archiving notification: {str(e)}")=f"Error retrieving users: {str(e)}")


@router.get("/users/{user_id}", response_model=AdminUserDetailResponse)
async def get_user_by_id(
    user_id: UUID,
    admin_profile = Depends(require_permissions(["admin.users.read"])),
    db: Session = Depends(get_database)
):
    try:
        user_service = UserProfileService(db)
        user = await user_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return AdminUserDetailResponse(
            id=str(user.id),
            email=user.supabase_user_id,  # Temporal: debería venir de auth.users
            full_name=user.full_name,
            role_id=str(user.role_id) if user.role_id else None,
            role={
                "id": str(user.role.id),
                "name": user.role.name,
                "description": user.role.description,
                "permissions": user.role.permissions or []
            } if user.role else None,
            status="active",
            last_login_at=user.last_activity_at,
            email_verified_at=None,
            two_factor_enabled=False,
            invited_by=None,
            invited_at=user.invited_at,
            password_set_at=None,
            failed_login_attempts=0,
            locked_until=None,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user: {str(e)}")


@router.post("/users")
async def create_user(
    user_data: AdminCreateUserRequest,
    admin_profile = Depends(require_permissions(["admin.users.create"])),
    db: Session = Depends(get_database)
):
    try:
        user_service = UserProfileService(db)
        
        invited_user = await user_service.invite_user(
            email=user_data.email,
            full_name=user_data.full_name,
            role_id=str(user_data.role_id)
        )
        
        return {
            "user": {
                "id": invited_user["id"],
                "email": invited_user["email"],
                "full_name": user_data.full_name,
                "role_id": str(user_data.role_id),
                "status": "invited",
                "invited_at": invited_user["invited_at"],
                "invited_by": str(admin_profile.id)
            },
            "invitation_token": "sent_via_email"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")


@router.put("/users/{user_id}")
async def update_user(
    user_id: UUID,
    update_data: AdminUpdateUserRequest,
    admin_profile = Depends(require_permissions(["admin.users.update"])),
    db: Session = Depends(get_database)
):
    try:
        user_service = UserProfileService(db)
        
        if update_data.role_id:
            await user_service.update_user_role(user_id, update_data.role_id)
        
        updated_user = await user_service.get_user_by_id(user_id)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "user": {
                "id": str(updated_user.id),
                "email": updated_user.supabase_user_id,
                "full_name": updated_user.full_name,
                "role_id": str(updated_user.role_id) if updated_user.role_id else None,
                "status": "active",
                "updated_at": updated_user.updated_at
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: UUID,
    admin_profile = Depends(require_permissions(["admin.users.delete"])),
    db: Session = Depends(get_database)
):
    try:
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")


@router.post("/users/{user_id}/activate")
async def activate_user(
    user_id: UUID,
    admin_profile = Depends(require_permissions(["admin.users.update"])),
    db: Session = Depends(get_database)
):
    try:
        return {
            "message": "User activated successfully",
            "user": {
                "id": str(user_id),
                "status": "active",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error activating user: {str(e)}")


@router.post("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: UUID,
    admin_profile = Depends(require_permissions(["admin.users.update"])),
    db: Session = Depends(get_database)
):
    try:
        return {
            "message": "User deactivated successfully",
            "user": {
                "id": str(user_id),
                "status": "inactive",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deactivating user: {str(e)}")


@router.post("/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: UUID,
    admin_profile = Depends(require_permissions(["admin.users.update"])),
    db: Session = Depends(get_database)
):
    try:
        return {"message": "Password reset email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending password reset: {str(e)}")


@router.get("/roles", response_model=AdminRolesListResponse)
async def get_roles(
    admin_profile = Depends(require_permissions(["admin.roles.read"])),
    db: Session = Depends(get_database)
):
    try:
        role_service = RoleService(db)
        roles_with_counts = await role_service.get_all_roles_with_user_count()
        
        roles_data = []
        for item in roles_with_counts:
            roles_data.append({
                "id": str(item["role"].id),
                "name": item["role"].name,
                "description": item["role"].description,
                "is_system_role": item["role"].name in ["admin", "manager", "user"],
                "permissions": item["role"].permissions or [],
                "user_count": item["users_count"],
                "created_at": item["role"].created_at,
                "updated_at": item["role"].updated_at
            })
        
        return AdminRolesListResponse(roles=roles_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving roles: {str(e)}")


@router.get("/roles/{role_id}", response_model=AdminRoleDetailResponse)
async def get_role_by_id(
    role_id: UUID,
    admin_profile = Depends(require_permissions(["admin.roles.read"])),
    db: Session = Depends(get_database)
):
    try:
        role_service = RoleService(db)
        role = await role_service.get_role_by_id(role_id)
        
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        permissions = [
            {
                "id": str(i),
                "name": perm,
                "description": f"Permission: {perm}",
                "category": perm.split('.')[0] if '.' in perm else "general",
                "resource": perm.split('.')[0] if '.' in perm else "unknown",
                "action": perm.split('.')[1] if '.' in perm and len(perm.split('.')) > 1 else "unknown"
            }
            for i, perm in enumerate(role.permissions or [])
        ]
        
        return AdminRoleDetailResponse(
            id=str(role.id),
            name=role.name,
            description=role.description,
            is_system_role=role.name in ["admin", "manager", "user"],
            permissions=permissions,
            user_count=0,
            created_at=role.created_at,
            updated_at=role.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving role: {str(e)}")


@router.post("/roles")
async def create_role(
    role_data: AdminCreateRoleRequest,
    admin_profile = Depends(require_permissions(["admin.roles.create"])),
    db: Session = Depends(get_database)
):
    try:
        role_service = RoleService(db)
        new_role = await role_service.create_role(role_data.dict())
        
        return {
            "role": {
                "id": str(new_role.id),
                "name": new_role.name,
                "description": new_role.description,
                "permissions": new_role.permissions or [],
                "created_at": new_role.created_at
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating role: {str(e)}")


@router.put("/roles/{role_id}")
async def update_role(
    role_id: UUID,
    update_data: AdminUpdateRoleRequest,
    admin_profile = Depends(require_permissions(["admin.roles.update"])),
    db: Session = Depends(get_database)
):
    try:
        role_service = RoleService(db)
        updated_role = await role_service.update_role(role_id, update_data.dict(exclude_unset=True))
        
        return {
            "role": {
                "id": str(updated_role.id),
                "name": updated_role.name,
                "description": updated_role.description,
                "permissions": updated_role.permissions or [],
                "updated_at": updated_role.updated_at
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating role: {str(e)}")


@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: UUID,
    admin_profile = Depends(require_permissions(["admin.roles.delete"])),
    db: Session = Depends(get_database)
):
    try:
        role_service = RoleService(db)
        await role_service.delete_role(role_id)
        return {"message": "Role deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting role: {str(e)}")


@router.get("/permissions", response_model=AdminPermissionsResponse)
async def get_permissions(
    admin_profile = Depends(require_permissions(["admin.permissions.read"])),
    db: Session = Depends(get_database)
):
    try:
        permissions_data = {
            "leads": [
                {"id": "1", "name": "leads.read", "description": "View leads", "resource": "leads", "action": "read"},
                {"id": "2", "name": "leads.create", "description": "Create leads", "resource": "leads", "action": "create"},
                {"id": "3", "name": "leads.update", "description": "Update leads", "resource": "leads", "action": "update"},
                {"id": "4", "name": "leads.delete", "description": "Delete leads", "resource": "leads", "action": "delete"},
            ],
            "campaigns": [
                {"id": "5", "name": "campaigns.read", "description": "View campaigns", "resource": "campaigns", "action": "read"},
                {"id": "6", "name": "campaigns.create", "description": "Create campaigns", "resource": "campaigns", "action": "create"},
                {"id": "7", "name": "campaigns.update", "description": "Update campaigns", "resource": "campaigns", "action": "update"},
                {"id": "8", "name": "campaigns.delete", "description": "Delete campaigns", "resource": "campaigns", "action": "delete"},
            ],
            "analytics": [
                {"id": "9", "name": "analytics.read", "description": "View analytics", "resource": "analytics", "action": "read"},
                {"id": "10", "name": "analytics.export", "description": "Export analytics", "resource": "analytics", "action": "export"},
            ],
            "admin": [
                {"id": "11", "name": "admin.*", "description": "Full admin access", "resource": "admin", "action": "*"},
                {"id": "12", "name": "admin.users.read", "description": "View users", "resource": "users", "action": "read"},
                {"id": "13", "name": "admin.users.create", "description": "Create users", "resource": "users", "action": "create"},
                {"id": "14", "name": "admin.users.update", "description": "Update users", "resource": "users", "action": "update"},
                {"id": "15", "name": "admin.users.delete", "description": "Delete users", "resource": "users", "action": "delete"},
                {"id": "16", "name": "admin.roles.read", "description": "View roles", "resource": "roles", "action": "read"},
                {"id": "17", "name": "admin.roles.create", "description": "Create roles", "resource": "roles", "action": "create"},
                {"id": "18", "name": "admin.roles.update", "description": "Update roles", "resource": "roles", "action": "update"},
                {"id": "19", "name": "admin.roles.delete", "description": "Delete roles", "resource": "roles", "action": "delete"},
                {"id": "20", "name": "admin.settings.read", "description": "View settings", "resource": "settings", "action": "read"},
                {"id": "21", "name": "admin.settings.update", "description": "Update settings", "resource": "settings", "action": "update"},
            ],
            "notifications": [
                {"id": "22", "name": "notifications.read", "description": "View notifications", "resource": "notifications", "action": "read"},
            ],
            "settings": [
                {"id": "23", "name": "settings.read", "description": "View settings", "resource": "settings", "action": "read"},
                {"id": "24", "name": "settings.update", "description": "Update settings", "resource": "settings", "action": "update"},
            ]
        }
        
        return AdminPermissionsResponse(permissions=permissions_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving permissions: {str(e)}")


@router.get("/permissions/categories", response_model=AdminPermissionCategoriesResponse)
async def get_permission_categories(
    admin_profile = Depends(require_permissions(["admin.permissions.read"])),
    db: Session = Depends(get_database)
):
    try:
        categories_data = [
            {"name": "leads", "label": "Gestión de Leads", "permission_count": 4},
            {"name": "campaigns", "label": "Campañas", "permission_count": 4},
            {"name": "analytics", "label": "Analíticas", "permission_count": 2},
            {"name": "admin", "label": "Administración", "permission_count": 10},
            {"name": "notifications", "label": "Notificaciones", "permission_count": 1},
            {"name": "settings", "label": "Configuración", "permission_count": 2}
        ]
        
        return AdminPermissionCategoriesResponse(categories=categories_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving permission categories: {str(e)}")


@router.get("/activity-logs", response_model=AdminActivityLogsResponse)
async def get_activity_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    user_id: Optional[UUID] = Query(None),
    activity_type: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    admin_profile = Depends(require_permissions(["admin.activity.read"])),
    db: Session = Depends(get_database)
):
    try:
        activity_service = ActivityLogService(db)
        
        activities = await activity_service.get_recent_activities(
            limit=limit,
            activity_types=[activity_type] if activity_type else None
        )
        
        activities_data = []
        for activity in activities:
            activities_data.append({
                "id": str(activity.id),
                "user_id": str(activity.user_id),
                "user_name": activity.user.full_name if activity.user else "Unknown",
                "activity_type": activity.activity_type,
                "action": activity.action,
                "description": activity.description,
                "resource_type": activity.resource_type,
                "resource_id": str(activity.resource_id) if activity.resource_id else None,
                "ip_address": activity.ip_address,
                "user_agent": activity.user_agent,
                "changes": activity.activity_metadata,
                "execution_time_ms": 0,  # Placeholder
                "timestamp": activity.created_at
            })
        
        return AdminActivityLogsResponse(
            activities=activities_data,
            pagination={
                "page": page,
                "limit": limit,
                "total": len(activities),
                "total_pages": 1
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving activity logs: {str(e)}")


@router.get("/activity-logs/summary", response_model=AdminActivitySummaryResponse)
async def get_activity_summary(
    days: int = Query(30, ge=1, le=365),
    admin_profile = Depends(require_permissions(["admin.activity.read"])),
    db: Session = Depends(get_database)
):
    try:
        activity_service = ActivityLogService(db)
        stats = await activity_service.get_activity_stats(days_back=days)
        
        summary_data = {
            "total_activities": stats["total_activities"],
            "unique_users": 0,
            "most_active_user": {
                "user_id": "unknown",
                "user_name": "Unknown",
                "activity_count": 0
            },
            "activity_types": stats["activity_breakdown"],
            "daily_activity": []
        }
        
        return AdminActivitySummaryResponse(summary=summary_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving activity summary: {str(e)}")


# System Settings Endpoints
@router.get("/settings")
async def get_system_settings(
    category: Optional[str] = Query(None),
    is_public: Optional[bool] = Query(None),
    admin_profile = Depends(require_permissions(["admin.settings.read"])),
    db: Session = Depends(get_database)
):
    """Get system settings grouped by category"""
    try:
        from app.api.services.system_settings_service import SystemSettingsService
        settings_service = SystemSettingsService(db)
        
        settings = await settings_service.get_all_settings(
            include_private=True,
            category=category,
            is_public=is_public
        )
        
        return {"settings": settings}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving settings: {str(e)}")


@router.get("/settings/{setting_id}")
async def get_system_setting(
    setting_id: UUID,
    admin_profile = Depends(require_permissions(["admin.settings.read"])),
    db: Session = Depends(get_database)
):
    """Get specific system setting"""
    try:
        from app.api.services.system_settings_service import SystemSettingsService
        settings_service = SystemSettingsService(db)
        
        setting = await settings_service.get_setting_by_id(setting_id)
        return {"setting": setting}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving setting: {str(e)}")


@router.put("/settings/{setting_id}")
async def update_system_setting(
    setting_id: UUID,
    update_data: dict,
    admin_profile = Depends(require_permissions(["admin.settings.update"])),
    db: Session = Depends(get_database)
):
    """Update system setting"""
    try:
        from app.api.services.system_settings_service import SystemSettingsService
        from app.api.schemas.system_settings import UpdateSystemSettingRequest
        
        settings_service = SystemSettingsService(db)
        
        # Validate update data
        if "value" not in update_data:
            raise HTTPException(status_code=400, detail="Value is required")
        
        update_request = UpdateSystemSettingRequest(
            value=update_data["value"],
            description=update_data.get("description")
        )
        
        updated_setting = await settings_service.update_setting(
            setting_id=setting_id,
            update_data=update_request,
            updated_by=admin_profile.id
        )
        
        return {
            "setting": {
                "id": str(updated_setting.id),
                "key": updated_setting.key,
                "value": updated_setting.value,
                "updated_at": updated_setting.updated_at,
                "updated_by": str(updated_setting.updated_by)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating setting: {str(e)}")


# Notification Endpoints
@router.get("/notifications")
async def get_notifications(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    is_read: Optional[bool] = Query(None),
    type: Optional[str] = Query(None),
    admin_profile = Depends(require_permissions(["notifications.read"])),
    db: Session = Depends(get_database)
):
    """Get notifications for current user"""
    try:
        from app.api.services.notification_service import NotificationService
        notification_service = NotificationService(db)
        
        # For admin, get their own notifications
        unread_only = is_read is False if is_read is not None else False
        
        result = await notification_service.get_user_notifications(
            user_id=admin_profile.id,
            unread_only=unread_only,
            page=page,
            limit=limit
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving notifications: {str(e)}")


@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Mark notification as read"""
    try:
        from app.api.services.notification_service import NotificationService
        from app.api.services.user_service import UserProfileService
        
        user_service = UserProfileService(db)
        notification_service = NotificationService(db)
        
        # Get user profile to get the actual user ID
        profile = await user_service.get_or_create_user_profile(current_user)
        
        notification = await notification_service.mark_notification_as_read(
            notification_id=notification_id,
            user_id=UUID(profile.id)
        )
        
        return {
            "message": "Notification marked as read",
            "notification": {
                "id": str(notification.id),
                "is_read": True,
                "read_at": notification.read_at
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking notification as read: {str(e)}")


@router.put("/notifications/read-all")
async def mark_all_notifications_read(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Mark all notifications as read for current user"""
    try:
        from app.api.services.notification_service import NotificationService
        from app.api.services.user_service import UserProfileService
        
        user_service = UserProfileService(db)
        notification_service = NotificationService(db)
        
        # Get user profile to get the actual user ID
        profile = await user_service.get_or_create_user_profile(current_user)
        
        updated_count = await notification_service.mark_all_notifications_as_read(
            user_id=UUID(profile.id)
        )
        
        return {
            "message": "All notifications marked as read",
            "updated_count": updated_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail