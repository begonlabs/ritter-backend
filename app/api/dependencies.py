from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.config import settings
import jwt
from typing import Generator


security = HTTPBearer()

async def get_database() -> Generator[Session, None, None]:
    async for db in get_db():
        yield db



# TODO: implement this sh*t 