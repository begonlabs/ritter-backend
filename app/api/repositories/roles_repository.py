from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.repositories.base import BaseRepository
from app.models.user import Role, UserProfile


class RoleRepository(BaseRepository[Role, dict, dict]):
    def __init__(self, db: Session):
        super().__init__(db, Role)


    def get_by_name(self, name: str) -> Optional[Role]:
        return self.db.query(Role).filter(Role.name == name).first()


    def get_all_with_users_count(self) -> List[Dict[str, Any]]:
        roles_with_counts = self.db.query(
            Role,
            func.count(UserProfile.id).label('users_count')
        ).outerjoin(UserProfile).group_by(Role.id).order_by(Role.name).all()

        return [
            {
                "role": role,
                "users_count": count or 0
            }
            for role, count in roles_with_counts
        ]


    def initialize_default_roles(self):
        default_roles = [
            {
                "name": "admin",
                "description": "Administrator. Full access to all system features.",
                "permissions": ["admin.*"]
            },
            {
                "name": "manager",
                "description": "Manager. Can manage users and view system data.",
                "permissions": [
                    "users.read", "users.update", "reports.read", "profile.*"
                ]
            },
            {
                "name": "user",
                "description": "Standard User. Basic access to their own profile.",
                "permissions": ["profile.read", "profile.update", "notifications.read"]
            }
        ]

        for role_data in default_roles:
            if not self.get_by_name(role_data["name"]):
                db_role = Role(
                    name=role_data["name"],
                    description=role_data["description"],
                    permissions=role_data["permissions"],
                    created_at=datetime.utcnow()
                )
                self.db.add(db_role)

        self.db.commit()