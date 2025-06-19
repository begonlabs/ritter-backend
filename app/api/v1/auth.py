from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.api.dependencies import get_database
from app.api.services.user_service import UserProfileService
from app.api.schemas.user import UserProfileResponse, UpdateProfileRequest

router = APIRouter()


@router.get("/me")
async def read_token_info(payload: dict = Depends(get_current_user)):
    return {
        "message": "Token is valid",
        "user_id": payload["sub"],
        "email": payload.get("email", "unknown")
    }


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    try:
        user_service = UserProfileService(db)
        profile = await user_service.get_or_create_user_profile(current_user)
        
        return UserProfileResponse(user=profile)
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving user profile: {str(e)}"
        )


@router.put("/profile")
async def update_user_profile(
    profile_data: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    try:
        user_service = UserProfileService(db)
        
        update_data = {}
        if profile_data.full_name is not None:
            update_data["full_name"] = profile_data.full_name
        if profile_data.metadata is not None:
            update_data["metadata"] = profile_data.metadata
        
        updated_profile = await user_service.update_user_profile(
            current_user["sub"], 
            update_data,
            current_user 
        )
        
        return {
            "message": "Profile updated successfully",
            "user": updated_profile
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating user profile: {str(e)}"
        )


@router.get("/permissions")
async def get_user_permissions(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    try:
        user_service = UserProfileService(db)
        profile = await user_service.get_or_create_user_profile(current_user)
        
        if not profile.role:
            return {
                "permissions": [],
                "role": None
            }
        
        return {
            "permissions": [
                {
                    "name": perm,
                    "description": f"Permission: {perm}",
                    "category": perm.split('.')[0] if '.' in perm else "general",
                    "resource": perm.split('.')[0] if '.' in perm else "unknown",
                    "action": perm.split('.')[1] if '.' in perm and len(perm.split('.')) > 1 else "unknown"
                }
                for perm in profile.role.permissions
            ],
            "role": {
                "id": profile.role.id,
                "name": profile.role.name
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving user permissions: {str(e)}"
        )