from fastapi import APIRouter, Depends, HTTPException
import httpx
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config import settings
from app.api.dependencies import get_database
from app.core.database import check_database_connection

from app.api.v1 import auth, health, admin, layout

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(layout.router, prefix="/layout", tags=["layout"])