from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from app.api.models.notification import Notification
from app.api.repositories.notification_repository import NotificationRepository
from app.api.repositories.user_repository import UserRepository
from app.api.schemas.notification import CreateNotificationRequest
from fastapi import HTTPException


class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_repo = NotificationRepository(db)
        self.user_repo = UserRepository(db)

    async def get_user_notifications(
        self,
        user_id: UUID,
        unread_only: bool = False,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Get user notifications with pagination"""
        offset = (page - 1) * limit
        
        notifications = self.notification_repo.get_user_notifications(
            user_id=user_id,
            unread_only=unread_only,
            limit=limit,
            offset=offset
        )
        
        total = self.notification_repo.count({"user_id": user_id, "is_archived": False})
        unread_count = self.notification_repo.get_unread_count(user_id)
        
        return {
            "notifications": notifications,
            "unread_count": unread_count,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit if limit > 0 else 1
            }
        }

    async def mark_notification_as_read(
        self,
        notification_id: UUID,
        user_id: UUID
    ) -> Optional[Notification]:
        """Mark a notification as read"""
        notification = self.notification_repo.mark_as_read(notification_id, user_id)
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return notification

    async def mark_all_notifications_as_read(self, user_id: UUID) -> int:
        """Mark all user notifications as read"""
        return self.notification_repo.mark_all_as_read(user_id)

    async def archive_notification(
        self,
        notification_id: UUID,
        user_id: UUID
    ) -> Optional[Notification]:
        """Archive a notification"""
        notification = self.notification_repo.archive_notification(notification_id, user_id)
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return notification

    async def create_notification(
        self,
        notification_data: CreateNotificationRequest
    ) -> Notification:
        """Create a new notification"""
        # Verify user exists
        user = self.user_repo.get(notification_data.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return self.notification_repo.create_notification(
            user_id=notification_data.user_id,
            type=notification_data.type,
            title=notification_data.title,
            message=notification_data.message,
            priority=notification_data.priority,
            action_url=notification_data.action_url,
            action_text=notification_data.action_text,
            action_data=notification_data.action_data,
            related_type=notification_data.related_type,
            related_id=notification_data.related_id,
            expires_at=notification_data.expires_at
        )

    async def create_system_notification(
        self,
        user_ids: List[UUID],
        title: str,
        message: str,
        type: str = "system",
        priority: int = 1,
        action_url: str = None,
        action_text: str = None
    ) -> List[Notification]:
        """Create notifications for multiple users"""
        notifications = []
        
        for user_id in user_ids:
            try:
                notification = self.notification_repo.create_notification(
                    user_id=user_id,
                    type=type,
                    title=title,
                    message=message,
                    priority=priority,
                    action_url=action_url,
                    action_text=action_text
                )
                notifications.append(notification)
            except Exception as e:
                # Log error but continue with other users
                print(f"Error creating notification for user {user_id}: {e}")
        
        return notifications

    async def create_welcome_notification(self, user_id: UUID) -> Notification:
        """Create welcome notification for new users"""
        return self.notification_repo.create_notification(
            user_id=user_id,
            type="welcome",
            title="¡Bienvenido a RitterFinder!",
            message="Tu cuenta ha sido creada exitosamente. Explora todas las funcionalidades disponibles.",
            priority=1,
            action_url="/dashboard",
            action_text="Ir al Dashboard"
        )

    async def create_campaign_notification(
        self,
        user_id: UUID,
        campaign_id: UUID,
        campaign_name: str,
        status: str
    ) -> Notification:
        """Create campaign status notification"""
        if status == "completed":
            title = "Campaña Completada"
            message = f"La campaña '{campaign_name}' se ha completado exitosamente."
        elif status == "failed":
            title = "Campaña Fallida"
            message = f"La campaña '{campaign_name}' ha fallado. Revisa los detalles."
        else:
            title = "Actualización de Campaña"
            message = f"La campaña '{campaign_name}' cambió su estado a {status}."
        
        return self.notification_repo.create_notification(
            user_id=user_id,
            type="campaign_update",
            title=title,
            message=message,
            priority=2,
            action_url=f"/campaigns/{campaign_id}",
            action_text="Ver Campaña",
            related_type="campaigns",
            related_id=campaign_id
        )

    async def cleanup_notifications(self) -> Dict[str, int]:
        """Clean up expired and old notifications"""
        expired_count = self.notification_repo.cleanup_expired_notifications()
        old_count = self.notification_repo.cleanup_old_read_notifications(days_to_keep=30)
        
        return {
            "expired_notifications_removed": expired_count,
            "old_notifications_removed": old_count
        }