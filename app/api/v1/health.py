from app.core.security import get_current_user
from fastapi import APIRouter, Depends, HTTPException
import httpx
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config import settings
from app.api.dependencies import get_database
from app.core.database import check_database_connection

router = APIRouter()


@router.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "message": "API is running successfully",
        "project": settings.PROJECT_NAME
    }


@router.get("/db")
async def database_health_check(db: Session = Depends(get_database)):
    """Database health check endpoint"""
    try:
        with db.connection() as conn:
            conn.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "message": "Database connection is working"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "message": f"Database connection failed: {str(e)}"
        }