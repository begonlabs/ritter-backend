from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class SearchConfiguration(Base):
    __tablename__ = "search_configurations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    client_types = Column(JSONB, default=list)
    locations = Column(JSONB, default=list)
    websites = Column(JSONB, default=list)

    validate_emails = Column(Boolean, default=True)
    validate_websites = Column(Boolean, default=True)
    validate_phones = Column(Boolean, default=False)

    company_size_min = Column(Integer, nullable=True)
    company_size_max = Column(Integer, nullable=True)
    industries = Column(JSONB, default=list)
    job_titles = Column(JSONB, default=list)
    keywords = Column(String(500), nullable=True)
    exclude_keywords = Column(String(500), nullable=True)

    created_by = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    usage_count = Column(Integer, default=0)

    is_template = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    metadata = Column(JSONB, default=dict)

    creator = relationship("UserProfile", back_populates="search_configurations")
    search_history = relationship("SearchHistory", back_populates="search_config", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SearchConfiguration(id={self.id}, name='{self.name}')>"