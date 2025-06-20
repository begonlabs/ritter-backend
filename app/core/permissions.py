from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.api.dependencies import get_database
from app.api.services.user_service import UserProfileService
from typing import List


async def check_permissions(
    required_permissions: List[str],
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    user_service = UserProfileService(db)
    profile = await user_service.get_or_create_user_profile(current_user)
    
    if not profile.role or not profile.role.permissions:
        raise HTTPException(
            status_code=403, 
            detail="Access denied: No permissions assigned"
        )
    
    user_permissions = profile.role.permissions
    
    for required_perm in required_permissions:
        for user_perm in user_permissions:
            if user_perm.endswith('.*'):
                if required_perm.startswith(user_perm[:-1]):
                    return profile
            elif user_perm == required_perm:
                return profile
    
    raise HTTPException(
        status_code=403, 
        detail=f"Access denied: Required permissions: {', '.join(required_permissions)}"
    )


def require_permissions(permissions: List[str]):
    async def permission_dependency(
        current_user: dict = Depends(get_current_user),
        db: Session = Depends(get_database)
    ):
        return await check_permissions(permissions, current_user, db)
    
    return permission_dependency