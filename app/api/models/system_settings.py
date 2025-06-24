from sqlalchemy import Column, String, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class SystemSettings(Base):
    __tablename__ = "system_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category = Column(String(100), nullable=False, index=True)
    key = Column(String(255), nullable=False, index=True)
    value = Column(Text, nullable=True)
    value_type = Column(String(50), default='string')
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=False)
    is_encrypted = Column(Boolean, default=False)
    
    validation_rules = Column(JSONB, default=dict)
    default_value = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    def __repr__(self):
        return f"<SystemSettings(id={self.id}, category='{self.category}', key='{self.key}')>"