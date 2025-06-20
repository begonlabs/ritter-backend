from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
from uuid import UUID

from app.api.repositories.base import BaseRepository
from app.api.models.user import UserProfile, Role
from app.api.schemas.user import UpdateProfileRequest



class UserRepository(BaseRepository[UserProfile, dict, UpdateProfileRequest]):
    def __init__(self, db: Session):
        super().__init__(db, UserProfile)


    def get_by_supabase_id(self, supabase_user_id: str) -> Optional[UserProfile]:
        return self.db.query(UserProfile).filter(
            UserProfile.supabase_user_id == supabase_user_id
        ).first()


    def get_with_role(self, user_id: UUID) -> Optional[UserProfile]:
        return self.db.query(UserProfile).options(
            joinedload(UserProfile.role)
        ).filter(UserProfile.id == user_id).first()


    def get_by_supabase_id_with_role(self, supabase_user_id: str) -> Optional[UserProfile]:
        return self.db.query(UserProfile).options(
            joinedload(UserProfile.role)
        ).filter(UserProfile.supabase_user_id == supabase_user_id).first()


    def get_users_by_role(self, role_id: UUID) -> List[UserProfile]:
        return self.db.query(UserProfile).filter(
            UserProfile.role_id == role_id
        ).all()


    def search_users(
        self, 
        search_term: str,
        role_id: Optional[UUID] = None,
        active_only: bool = True
    ) -> List[UserProfile]:
        query = self.db.query(UserProfile).options(joinedload(UserProfile.role))
        
        search_conditions = []
        if search_term:
            search_conditions.extend([
                UserProfile.full_name.like(f"%{search_term}%"),
                UserProfile.supabase_user_id.like(f"%{search_term}%")
            ])
        
        if search_conditions:
            query = query.filter(or_(*search_conditions))
        
        if role_id:
            query = query.filter(UserProfile.role_id == role_id)
        
        if active_only and hasattr(UserProfile, 'is_active'):
            query = query.filter(UserProfile.is_active == True)
        
        return query.all()


    def get_users_paginated(
        self,
        skip: int = 0,
        limit: int = 20,
        role_id: Optional[UUID] = None,
        search_term: Optional[str] = None,
        order_by: str = "created_at",
        order_desc: bool = True
    ) -> Dict[str, Any]:
        """Get paginated users with filters"""
        query = self.db.query(UserProfile).options(joinedload(UserProfile.role))
        
        # Apply filters
        filters = []
        
        if role_id:
            filters.append(UserProfile.role_id == role_id)
        
        if search_term:
            search_conditions = [
                UserProfile.full_name.like(f"%{search_term}%")
            ]
            filters.append(or_(*search_conditions))
        
        if filters:
            query = query.filter(and_(*filters))
        
        # Count total records
        total = query.count()
        
        # Apply ordering
        if hasattr(UserProfile, order_by):
            if order_desc:
                query = query.order_by(getattr(UserProfile, order_by).desc())
            else:
                query = query.order_by(getattr(UserProfile, order_by))
        
        # Apply pagination
        users = query.offset(skip).limit(limit).all()
        
        return {
            "users": users,
            "total": total,
            "page": (skip // limit) + 1 if limit > 0 else 1,
            "per_page": limit,
            "total_pages": (total + limit - 1) // limit if limit > 0 else 1
        }


    def update_last_activity(self, supabase_user_id: str) -> Optional[UserProfile]:
        user = self.get_by_supabase_id(supabase_user_id)
        if user:
            user.last_activity_at = datetime.utcnow()
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        return user


    def get_recent_users(self, days: int = 7, limit: int = 10) -> List[UserProfile]:
        since_date = datetime.utcnow() - timedelta(days=days)
        return self.db.query(UserProfile).options(
            joinedload(UserProfile.role)
        ).filter(
            UserProfile.created_at >= since_date
        ).order_by(UserProfile.created_at.desc()).limit(limit).all()


    def get_active_users_count(self, days: int = 30) -> int:
        since_date = datetime.utcnow() - timedelta(days=days)
        return self.db.query(UserProfile).filter(
            UserProfile.last_activity_at >= since_date
        ).count()


    def get_users_by_role_name(self, role_name: str) -> List[UserProfile]:
        return self.db.query(UserProfile).options(
            joinedload(UserProfile.role)
        ).join(Role).filter(Role.name == role_name).all()


    def update_user_role(self, user_id: UUID, role_id: UUID) -> Optional[UserProfile]:
        user = self.get(user_id)
        if user:
            user.role_id = role_id
            user.updated_at = datetime.utcnow()
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        return user


    def bulk_update_role(self, user_ids: List[UUID], role_id: UUID) -> int:
        updated_count = self.db.query(UserProfile).filter(
            UserProfile.id.in_(user_ids)
        ).update({
            UserProfile.role_id: role_id,
            UserProfile.updated_at: datetime.utcnow()
        }, synchronize_session=False)
        
        self.db.commit()
        return updated_count


    def get_user_stats(self) -> Dict[str, Any]:
        total_users = self.db.query(UserProfile).count()
        
        # Users by role
        role_stats = self.db.query(
            Role.name,
            func.count(UserProfile.id).label('count')
        ).outerjoin(UserProfile).group_by(Role.name).all()
        
        # Recent activity
        last_7_days = datetime.utcnow() - timedelta(days=7)
        recent_active = self.db.query(UserProfile).filter(
            UserProfile.last_activity_at >= last_7_days
        ).count()
        
        # New users this month
        this_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        new_this_month = self.db.query(UserProfile).filter(
            UserProfile.created_at >= this_month
        ).count()
        
        return {
            "total_users": total_users,
            "users_by_role": {role: count for role, count in role_stats},
            "active_last_7_days": recent_active,
            "new_this_month": new_this_month
        }