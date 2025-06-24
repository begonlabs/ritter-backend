from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from datetime import datetime, timedelta
from uuid import UUID

from app.api.repositories.base import BaseRepository
from app.api.models.notification import Notification


class NotificationRepository(BaseRepository[Notification, dict, dict]):
    def __init__(self, db: Session):
        super().__init__(db, Notification)

    def get_user_notifications(
        self,
        user_id: UUID,
        unread_only: bool = False,
        limit: int = 20,
        offset: int = 0
    ) -> List[Notification]:
        """Get notifications for a specific user"""
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        # Filter out archived notifications
        query = query.filter(Notification.is_archived == False)
        
        # Filter out expired notifications
        query = query.filter(
            or_(
                Notification.expires_at.is_(None),
                Notification.expires_at > datetime.utcnow()
            )
        )
        
        return query.order_by(desc(Notification.created_at)).offset(offset).limit(limit).all()

    def get_unread_count(self, user_id: UUID) -> int:
        """Get count of unread notifications for user"""
        return self.db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False,
                Notification.is_archived == False
            )
        ).count()

    def mark_as_read(self, notification_id: UUID, user_id: UUID) -> Optional[Notification]:
        """Mark a notification as read"""
        notification = self.db.query(Notification).filter(
            and_(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
        ).first()
        
        if notification and not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            self.db.add(notification)
            self.db.commit()
            self.db.refresh(notification)
        
        return notification

    def mark_all_as_read(self, user_id: UUID) -> int:
        """Mark all user notifications as read"""
        updated_count = self.db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        ).update({
            Notification.is_read: True,
            Notification.read_at: datetime.utcnow()
        }, synchronize_session=False)
        
        self.db.commit()
        return updated_count

    def archive_notification(self, notification_id: UUID, user_id: UUID) -> Optional[Notification]:
        """Archive a notification"""
        notification = self.db.query(Notification).filter(
            and_(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
        ).first()
        
        if notification:
            notification.is_archived = True
            notification.archived_at = datetime.utcnow()
            self.db.add(notification)
            self.db.commit()
            self.db.refresh(notification)
        
        return notification

    def create_notification(
        self,
        user_id: UUID,
        type: str,
        title: str,
        message: str,
        priority: int = 0,
        action_url: str = None,
        action_text: str = None,
        action_data: dict = None,
        related_type: str = None,
        related_id: UUID = None,
        expires_at: datetime = None
    ) -> Notification:
        """Create a new notification"""
        notification_data = {
            "user_id": user_id,
            "type": type,
            "title": title,
            "message": message,
            "priority": priority,
            "action_url": action_url,
            "action_text": action_text,
            "action_data": action_data or {},
            "related_type": related_type,
            "related_id": related_id,
            "expires_at": expires_at,
            "created_at": datetime.utcnow()
        }
        
        return self.create(notification_data)

    def cleanup_expired_notifications(self) -> int:
        """Remove expired notifications"""
        deleted_count = self.db.query(Notification).filter(
            and_(
                Notification.expires_at.isnot(None),
                Notification.expires_at < datetime.utcnow()
            )
        ).delete()
        
        self.db.commit()
        return deleted_count

    def cleanup_old_read_notifications(self, days_to_keep: int = 30) -> int:
        """Remove old read notifications"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        deleted_count = self.db.query(Notification).filter(
            and_(
                Notification.is_read == True,
                Notification.read_at < cutoff_date
            )
        ).delete()
        
        self.db.commit()
        return deleted_count