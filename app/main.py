from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.v1.router import api_router
from app.config import settings
from app.core.database import check_database_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"🚀 Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"🌍 Environment: {settings.ENVIRONMENT}")
    
    db_connected = await check_database_connection()
    if db_connected:
        print("✅ Database connection successful")
    else:
        print("❌ Database connection failed")
    
    yield
    

    print("Shutting down...")

app = FastAPI(
    title = settings.PROJECT_NAME,
    version = settings.VERSION,
    lifespan = lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = settings.BACKEND_CORS_ORIGINS,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

app.include_router(api_router, prefix = settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": "/docs"
    }