from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from app.api.models.user import UserProfile, Role
from app.api.schemas.user import UserProfile as UserProfileSchema, RoleSchema, UpdateProfileRequest
from app.api.repositories import UserRepository, RoleRepository
from app.core.security import supabase
from fastapi import HTTPException



class UserProfileService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)

    async def get_or_create_user_profile(self, supabase_user_data: dict) -> UserProfileSchema:
        supabase_user_id = supabase_user_data["sub"]
        
        db_profile = self.user_repo.get_by_supabase_id_with_role(supabase_user_id)
        
        if not db_profile:
            db_profile = await self._create_user_profile(supabase_user_data)

        self.user_repo.update_last_activity(supabase_user_id)
        return await self._build_user_profile_response(db_profile, supabase_user_data)


    async def _create_user_profile(self, supabase_user_data: dict) -> UserProfile:
        """Create a new user profile"""
        full_name = None
        if "user_metadata" in supabase_user_data:
            metadata = supabase_user_data["user_metadata"]
            full_name = metadata.get("full_name") or metadata.get("name")

        default_role = self.role_repo.get_by_name("user")
        
        user_data = {
            "supabase_user_id": supabase_user_data["sub"],
            "full_name": full_name,
            "user_metadata": supabase_user_data.get("user_metadata", {}),
            "role_id": default_role.id if default_role else None,
            "created_at": datetime.utcnow(),
            "last_activity_at": datetime.utcnow()
        }
        db_profile = self.user_repo.create(user_data)
        
        return self.user_repo.get_by_supabase_id_with_role(db_profile.supabase_user_id)


    async def _build_user_profile_response(self, db_profile: UserProfile, supabase_user_data: dict) -> UserProfileSchema:
        role_data = None
        if db_profile.role:
            role_data = RoleSchema(
                id=db_profile.role.id,
                name=db_profile.role.name,
                permissions=db_profile.role.permissions or []
            )
        
        return UserProfileSchema(
            id=supabase_user_data["sub"],
            email=supabase_user_data.get("email", ""),
            full_name=db_profile.full_name,
            role=role_data,
            last_activity_at=db_profile.last_activity_at,
            created_at=db_profile.created_at,
            user_metadata=supabase_user_data.get("user_metadata", {})
        )


    async def update_user_profile(self, supabase_user_id: str, update_data: dict, current_supabase_data: dict) -> UserProfileSchema:
        db_profile = self.user_repo.get_by_supabase_id(supabase_user_id)
        
        if not db_profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        profile_update = UpdateProfileRequest(
            full_name=update_data.get("full_name"),
            metadata=update_data.get("metadata")
        )
        
        updated_profile = self.user_repo.update(db_profile, profile_update)
        updated_profile_with_role = self.user_repo.get_by_supabase_id_with_role(supabase_user_id)
    
        return await self._build_user_profile_response(updated_profile_with_role, current_supabase_data)


    async def invite_user(self, email: str, full_name: str, role_id: str) -> dict:
        try:
            role = self.role_repo.get(UUID(role_id))
            if not role:
                raise HTTPException(status_code=400, detail="Invalid role ID")
            
            response = supabase.auth.admin.invite_user_by_email(
                email=email,
                options={
                    "data": {
                        "full_name": full_name,
                        "invited_by_admin": True
                    }
                }
            )

            user_data = {
                "supabase_user_id": response.user.id,
                "full_name": full_name,
                "user_metadata": {"invited_by_admin": True},
                "role_id": UUID(role_id),
                "created_at": datetime.utcnow(),
                "last_activity_at": datetime.utcnow()
            }
            
            db_profile = self.user_repo.create(user_data)
            
            return {
                "id": response.user.id,
                "email": response.user.email,
                "full_name": full_name,
                "invited_at": response.user.created_at
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error inviting user: {str(e)}"
            )


    async def initialize_default_roles(self):
        self.role_repo.initialize_default_roles()


    async def get_user_by_id(self, user_id: UUID) -> Optional[UserProfile]:
        return self.user_repo.get_with_role(user_id)
    

    async def search_users(self, search_term: str, role_id: Optional[UUID] = None) -> list[UserProfile]:
        return self.user_repo.search_users(search_term, role_id)
    

    async def get_users_paginated(self, skip: int = 0, limit: int = 20, **filters) -> Dict[str, Any]:
        return self.user_repo.get_users_paginated(skip=skip, limit=limit, **filters)
    

    async def update_user_role(self, user_id: UUID, role_id: UUID) -> Optional[UserProfile]:
        return self.user_repo.update_user_role(user_id, role_id)
    

    async def get_user_stats(self) -> Dict[str, Any]:
        return self.user_repo.get_user_stats()
    

    async def get_recent_users(self, days: int = 7, limit: int = 10) -> list[UserProfile]:
        return self.user_repo.get_recent_users(days, limit)
    

    async def get_users_by_role_name(self, role_name: str) -> list[UserProfile]:
        return self.user_repo.get_users_by_role_name(role_name)
    

    async def get_active_users_count(self, days: int = 30) -> int:
        return self.user_repo.get_active_users_count(days)
    

    async def bulk_update_role(self, user_ids: list[UUID], role_id: UUID) -> int:
        return self.user_repo.bulk_update_role(user_ids, role_id)