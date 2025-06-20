from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.api.dependencies import get_database
from app.api.services.user_service import UserProfileService
from app.api.services.activity_log_service import ActivityLogService
from app.api.schemas.user import UserProfileResponse, UpdateProfileRequest, InviteUserRequest, InviteUserResponse
from app.api.schemas.activity_log import LogActivityRequest, LogActivityResponse
from app.core.permissions import require_permissions

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


@router.post("/invite-user", response_model=InviteUserResponse)
async def invite_user(
    invite_data: InviteUserRequest,
    admin_profile = Depends(require_permissions(["admin.users.create"])),
    db: Session = Depends(get_database)
):
    try:
        user_service = UserProfileService(db)
        
        invited_user = await user_service.invite_user(
            email=invite_data.email,
            full_name=invite_data.full_name,
            role_id=str(invite_data.role_id)
        )
        
        return InviteUserResponse(
            message="User invited successfully",
            user=invited_user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error inviting user: {str(e)}"
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


@router.post("/log-activity", response_model=LogActivityResponse)
async def log_activity(
    activity_data: LogActivityRequest,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    try:
        activity_service = ActivityLogService(db)
        
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        activity_log = await activity_service.log_activity(
            supabase_user_id=current_user["sub"],
            activity_data=activity_data,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return LogActivityResponse(
            message="Activity logged successfully",
            activity_id=activity_log.id,
            logged_at=activity_log.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error logging activity: {str(e)}"
        )