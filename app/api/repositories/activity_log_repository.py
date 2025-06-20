from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from datetime import datetime, timedelta
from uuid import UUID

from app.api.repositories.base import BaseRepository
from app.api.models.activity_log import ActivityLog
from app.api.models.user import UserProfile



class ActivityLogRepository(BaseRepository[ActivityLog, dict, dict]):
    def __init__(self, db: Session):
        super().__init__(db, ActivityLog)


    def create_activity_log(
        self,
        user_id: UUID,
        activity_type: str,
        action: str,
        description: str = None,
        resource_type: str = None,
        resource_id: UUID = None,
        metadata: dict = None,
        ip_address: str = None,
        user_agent: str = None
    ) -> ActivityLog:
        """Create a new activity log entry"""
        log_data = {
            "user_id": user_id,
            "activity_type": activity_type,
            "action": action,
            "description": description,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "activity_metadata": metadata,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "created_at": datetime.utcnow()
        }
        
        return self.create(log_data)


    def get_user_activities(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
        activity_type: str = None,
        days_back: int = None
    ) -> List[ActivityLog]:
        """Get activities for a specific user"""
        query = self.db.query(ActivityLog).filter(ActivityLog.user_id == user_id)
        
        if activity_type:
            query = query.filter(ActivityLog.activity_type == activity_type)
        
        if days_back:
            since_date = datetime.utcnow() - timedelta(days=days_back)
            query = query.filter(ActivityLog.created_at >= since_date)
        
        return query.order_by(desc(ActivityLog.created_at)).offset(offset).limit(limit).all()


    def get_recent_activities(
        self,
        limit: int = 100,
        activity_types: List[str] = None
    ) -> List[ActivityLog]:
        query = self.db.query(ActivityLog).options(
            joinedload(ActivityLog.user)
        )
        
        if activity_types:
            query = query.filter(ActivityLog.activity_type.in_(activity_types))
        
        return query.order_by(desc(ActivityLog.created_at)).limit(limit).all()


    def get_activity_stats(
        self,
        user_id: UUID = None,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Get activity statistics"""
        since_date = datetime.utcnow() - timedelta(days=days_back)
        query = self.db.query(ActivityLog).filter(ActivityLog.created_at >= since_date)
        
        if user_id:
            query = query.filter(ActivityLog.user_id == user_id)
        
        # Count by activity type
        activity_counts = {}
        for log in query.all():
            activity_counts[log.activity_type] = activity_counts.get(log.activity_type, 0) + 1
        
        return {
            "total_activities": query.count(),
            "activity_breakdown": activity_counts,
            "period_days": days_back
        }


    def cleanup_old_logs(self, days_to_keep: int = 90) -> int:
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        deleted_count = self.db.query(ActivityLog).filter(
            ActivityLog.created_at < cutoff_date
        ).delete()
        
        self.db.commit()
        return deleted_count