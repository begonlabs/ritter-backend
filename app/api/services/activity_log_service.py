from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from app.api.models.activity_log import ActivityLog
from app.api.repositories import ActivityLogRepository, UserRepository
from app.api.schemas.activity_log import LogActivityRequest
from fastapi import HTTPException



class ActivityLogService:
    def __init__(self, db: Session):
        self.db = db
        self.activity_repo = ActivityLogRepository(db)
        self.user_repo = UserRepository(db)


    async def log_activity(
        self,
        supabase_user_id: str,
        activity_data: LogActivityRequest,
        ip_address: str = None,
        user_agent: str = None
    ) -> ActivityLog:
        user_profile = self.user_repo.get_by_supabase_id(supabase_user_id)
        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        activity_log = self.activity_repo.create_activity_log(
            user_id=user_profile.id,
            activity_type=activity_data.activity_type,
            action=activity_data.action,
            description=activity_data.description,
            resource_type=activity_data.resource_type,
            resource_id=activity_data.resource_id,
            metadata=activity_data.metadata,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.user_repo.update_last_activity(supabase_user_id)
        
        return activity_log


    async def get_user_activities(
        self,
        supabase_user_id: str,
        limit: int = 50,
        offset: int = 0,
        activity_type: str = None,
        days_back: int = None
    ) -> List[ActivityLog]:
        
        user_profile = self.user_repo.get_by_supabase_id(supabase_user_id)
        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        return self.activity_repo.get_user_activities(
            user_id=user_profile.id,
            limit=limit,
            offset=offset,
            activity_type=activity_type,
            days_back=days_back
        )


    async def get_recent_activities(
        self,
        limit: int = 100,
        activity_types: List[str] = None
    ) -> List[ActivityLog]:
        return self.activity_repo.get_recent_activities(
            limit=limit,
            activity_types=activity_types
        )


    async def get_activity_stats(
        self,
        supabase_user_id: str = None,
        days_back: int = 30
    ) -> Dict[str, Any]:
        
        user_id = None
        if supabase_user_id:
            user_profile = self.user_repo.get_by_supabase_id(supabase_user_id)
            if user_profile:
                user_id = user_profile.id
        
        return self.activity_repo.get_activity_stats(
            user_id=user_id,
            days_back=days_back
        )


    async def cleanup_old_logs(self, days_to_keep: int = 90) -> int:
        return self.activity_repo.cleanup_old_logs(days_to_keep)