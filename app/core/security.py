from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from app.config import settings

security = HTTPBearer()

supabase: Client = create_client(
    f"https://{settings.SUPABASE_PROJECT_ID}.supabase.co",
    settings.SUPABASE_ANON_KEY
)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    
    try:
        user = supabase.auth.get_user(token)
        
        if not user.user:
            raise HTTPException(status_code=401, detail="Invalid token")
            
        return {
            "sub": user.user.id,
            "email": user.user.email,
            "user_metadata": user.user.user_metadata,
            "app_metadata": user.user.app_metadata
        }
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token validation failed: {str(e)}")