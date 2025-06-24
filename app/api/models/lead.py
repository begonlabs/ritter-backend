from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class Lead(Base):
    __tablename__ = "leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    email = Column(String(255), nullable=True, index=True)
    verified_email = Column(Boolean, default=False, index=True)
    phone = Column(String(50), nullable=True)
    verified_phone = Column(Boolean, default=False, index=True)

    company_name = Column(String(500), nullable=False, index=True)
    company_website = Column(String(500), nullable=True)
    verified_website = Column(Boolean, default=False, index=True)

    address = Column(Text, nullable=True)
    state = Column(String(255), nullable=True, index=True)
    country = Column(String(100), nullable=True, index=True)

    activity = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(255), nullable=True, index=True)

    data_quality_score = Column(Integer, default=1, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_contacted_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<Lead(id={self.id}, company_name='{self.company_name}')>"