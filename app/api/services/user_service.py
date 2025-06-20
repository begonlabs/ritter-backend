from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, Dict, Any
from datetime import datetime
from app.api.models.user import UserProfile, Role
from app.api.schemas.user import UserProfile as UserProfileSchema, RoleSchema
from app.core.security import supabase
from fastapi import HTTPException



class UserProfileService:
    def __init__(self, db: Session):
        self.db = db


    async def get_or_create_user_profile(self, supabase_user_data: dict) -> UserProfileSchema:
        supabase_user_id = supabase_user_data["sub"]
        
        db_profile = self.db.query(UserProfile).filter(
            UserProfile.supabase_user_id == supabase_user_id
        ).first()
        
        if not db_profile:
            db_profile = await self._create_user_profile(supabase_user_data)
        
        db_profile.last_activity_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_profile)
        
        return await self._build_user_profile_response(db_profile, supabase_user_data)


    async def _create_user_profile(self, supabase_user_data: dict) -> UserProfile:

        full_name = None
        if "user_metadata" in supabase_user_data:
            metadata = supabase_user_data["user_metadata"]
            full_name = metadata.get("full_name") or metadata.get("name")

        default_role = self.db.query(Role).filter(Role.name == "user").first()
        
        db_profile = UserProfile(
            supabase_user_id=supabase_user_data["sub"],
            full_name=full_name,
            user_metadata=supabase_user_data.get("user_metadata", {}),
            role_id=default_role.id if default_role else None,
            created_at=datetime.utcnow(),
            last_activity_at=datetime.utcnow()
        )
        
        self.db.add(db_profile)
        self.db.commit()
        self.db.refresh(db_profile)
        
        return db_profile


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
        db_profile = self.db.query(UserProfile).filter(
            UserProfile.supabase_user_id == supabase_user_id
        ).first()
        
        if not db_profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        if "full_name" in update_data:
            db_profile.full_name = update_data["full_name"]
        
        if "metadata" in update_data:
            current_metadata = db_profile.user_metadata or {}
            current_metadata.update(update_data["metadata"])
            db_profile.user_metadata = current_metadata
        
        db_profile.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_profile)

        return await self._build_user_profile_response(db_profile, current_supabase_data)


    async def invite_user(self, email: str, full_name: str, role_id: str) -> dict:
        try:
            role = self.db.query(Role).filter(Role.id == role_id).first()
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

            db_profile = UserProfile(
                supabase_user_id=response.user.id,
                full_name=full_name,
                user_metadata={"invited_by_admin": True},
                role_id=role_id,
                created_at=datetime.utcnow(),
                last_activity_at=datetime.utcnow()
            )
            
            self.db.add(db_profile)
            self.db.commit()
            self.db.refresh(db_profile)
            
            return {
                "id": response.user.id,
                "email": response.user.email,
                "full_name": full_name,
                "invited_at": response.user.created_at
            }
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error inviting user: {str(e)}"
            )


    async def initialize_default_roles(self):
        default_roles = [
            {
                "name": "admin",
                "description": "Administrator with full access",
                "permissions": ["admin.*", "users.*", "roles.*", "system.*"]
            },
            {
                "name": "manager",
                "description": "Manager with elevated permissions",
                "permissions": ["users.update", "users.read", "roles.read"]
            },
            {
                "name": "user", 
                "description": "Standard user",
                "permissions": ["profile.read", "profile.update", "notifications.read"]
            }
        ]
        
        for role_data in default_roles:
            existing_role = self.db.query(Role).filter(Role.name == role_data["name"]).first()
            if not existing_role:
                role = Role(**role_data)
                self.db.add(role)
        
        self.db.commit()