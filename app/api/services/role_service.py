from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from uuid import UUID

from app.api.models.user import Role
from app.api.repositories import RoleRepository
from fastapi import HTTPException



class RoleService:
    def __init__(self, db: Session):
        self.db = db
        self.role_repo = RoleRepository(db)


    async def get_role_by_id(self, role_id: UUID) -> Optional[Role]:
        return self.role_repo.get(role_id)


    async def get_role_by_name(self, name: str) -> Optional[Role]:
        return self.role_repo.get_by_name(name)


    async def get_all_roles(self, skip: int = 0, limit: int = 100) -> List[Role]:
        return self.role_repo.get_multi(skip=skip, limit=limit, order_by="name")


    async def get_all_roles_with_user_count(self) -> List[Dict[str, Any]]:
        return self.role_repo.get_all_with_users_count()


    async def create_role(self, role_data: dict) -> Role:
        existing_role = self.role_repo.get_by_name(role_data.get("name"))
        if existing_role:
            raise HTTPException(
                status_code=400, 
                detail=f"Role with name '{role_data.get('name')}' already exists"
            )
        
        return self.role_repo.create(role_data)


    async def update_role(self, role_id: UUID, update_data: dict) -> Optional[Role]:
        role = self.role_repo.get(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        if "name" in update_data:
            existing_role = self.role_repo.get_by_name(update_data["name"])
            if existing_role and existing_role.id != role_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Role with name '{update_data['name']}' already exists"
                )
        
        return self.role_repo.update(role, update_data)


    async def delete_role(self, role_id: UUID) -> Optional[Role]:
        role = self.role_repo.get(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        
        return self.role_repo.delete(role_id)


    async def search_roles(self, search_term: str) -> List[Role]:
        return self.role_repo.search(search_term, ["name", "description"])


    async def get_role_permissions(self, role_id: UUID) -> List[str]:
        role = self.role_repo.get(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        return role.permissions or []


    async def update_role_permissions(self, role_id: UUID, permissions: List[str]) -> Role:
        role = self.role_repo.get(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        return self.role_repo.update(role, {"permissions": permissions})


    async def add_permission_to_role(self, role_id: UUID, permission: str) -> Role:
        role = self.role_repo.get(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        current_permissions = role.permissions or []
        if permission not in current_permissions:
            current_permissions.append(permission)
            return self.role_repo.update(role, {"permissions": current_permissions})
        
        return role


    async def remove_permission_from_role(self, role_id: UUID, permission: str) -> Role:
        role = self.role_repo.get(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        current_permissions = role.permissions or []
        if permission in current_permissions:
            current_permissions.remove(permission)
            return self.role_repo.update(role, {"permissions": current_permissions})
        
        return role


    async def initialize_default_roles(self):
        self.role_repo.initialize_default_roles()