from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.core.security import get_current_user
from app.api.dependencies import get_database
from app.api.services.user_service import UserProfileService
from app.api.services.notification_service import NotificationService

router = APIRouter()


@router.get("/user-info")
async def get_user_info(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get minimal user info for layout header"""
    try:
        user_service = UserProfileService(db)
        profile = await user_service.get_or_create_user_profile(current_user)
        
        return {
            "user": {
                "id": profile.id,
                "full_name": profile.full_name,
                "email": current_user.get("email", ""),
                "role_name": profile.role.name if profile.role else "user",
                "last_login_at": profile.last_activity_at
            },
            "session": {
                "expires_at": None,  # Manejado por Supabase
                "time_remaining_minutes": None  # Manejado por Supabase
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user info: {str(e)}")


@router.get("/notifications")
async def get_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get user notifications"""
    try:
        user_service = UserProfileService(db)
        notification_service = NotificationService(db)
        
        # Get user profile to get the actual user ID
        profile = await user_service.get_or_create_user_profile(current_user)
        
        result = await notification_service.get_user_notifications(
            user_id=UUID(profile.id),
            unread_only=unread_only,
            page=1,
            limit=limit
        )
        
        return {
            "notifications": [
                {
                    "id": str(notif.id),
                    "type": notif.type,
                    "title": notif.title,
                    "message": notif.message,
                    "priority": notif.priority,
                    "is_read": notif.is_read,
                    "created_at": notif.created_at,
                    "action_url": notif.action_url,
                    "action_text": notif.action_text
                }
                for notif in result["notifications"]
            ],
            "unread_count": result["unread_count"]
        }
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
        user_service = UserProfileService(db)
        notification_service = NotificationService(db)
        
        # Get user profile to get the actual user ID
        profile = await user_service.get_or_create_user_profile(current_user)
        
        await notification_service.mark_notification_as_read(
            notification_id=notification_id,
            user_id=UUID(profile.id)
        )
        
        return {
            "success": True,
            "message": "Notification marked as read"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking notification as read: {str(e)}")


@router.post("/notifications/mark-all-read")
async def mark_all_notifications_read(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Mark all user notifications as read"""
    try:
        user_service = UserProfileService(db)
        notification_service = NotificationService(db)
        
        # Get user profile to get the actual user ID
        profile = await user_service.get_or_create_user_profile(current_user)
        
        marked_count = await notification_service.mark_all_notifications_as_read(
            user_id=UUID(profile.id)
        )
        
        return {
            "marked_count": marked_count,
            "message": "All notifications marked as read"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking all notifications as read: {str(e)}")