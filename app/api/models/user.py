from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid



class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    supabase_user_id = Column(String, unique = True, nullable = False, index = True)
    
    full_name = Column(String(255), nullable = True)
    avatar_url = Column(String(500), nullable = True)
    phone = Column(String(20), nullable = True)
    
    user_metadata = Column(JSONB, nullable = True)
    
    last_activity_at = Column(DateTime(timezone = True), nullable = True)
    created_at = Column(DateTime(timezone=True), server_default = func.now())
    updated_at = Column(DateTime(timezone=True), server_default = func.now(), onupdate = func.now())
    

    role_id = Column(UUID(as_uuid = True), ForeignKey("roles.id"), nullable = True)
    role = relationship("Role", back_populates = "users")
    
    activity_logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<UserProfile(id={self.id}, full_name='{self.full_name}')>"


class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    name = Column(String(50), unique = True, nullable = False)
    description = Column(Text, nullable = True)

    permissions = Column(JSONB, nullable = True, default = list)

    created_at = Column(DateTime(timezone = True), server_default = func.now())
    updated_at = Column(DateTime(timezone = True), server_default = func.now(), onupdate = func.now())

    users = relationship("UserProfile", back_populates = "role")

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"