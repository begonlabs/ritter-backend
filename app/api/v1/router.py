from fastapi import APIRouter
from app.config import settings

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