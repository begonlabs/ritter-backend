from fastapi import APIRouter, Depends
from app.core.security import get_current_user

router = APIRouter()


@router.get("/me")
async def read_token_info(payload: dict = Depends(get_current_user)):
    return {
        "message": "Token is valid",
        "user_id": payload["sub"],
        "email": payload.get("email", "unknown")
    }