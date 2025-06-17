from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config import settings
from app.api.dependencies import get_database
from app.core.database import check_database_connection

api_router = APIRouter()


@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "message": "API is running successfully",
        "project": settings.PROJECT_NAME
    }


@api_router.get("/health/db")
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