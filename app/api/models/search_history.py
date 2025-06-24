from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid
import enum


class SearchStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False, index=True)
    search_config_id = Column(UUID(as_uuid=True), ForeignKey("search_configurations.id"), nullable=True, index=True)

    query_name = Column(String(255), nullable=True)
    search_parameters = Column(JSONB, nullable=False)
    filters_applied = Column(JSONB, default=dict)

    status = Column(Enum(SearchStatus), default=SearchStatus.PENDING, index=True)
    total_results = Column(Integer, default=0)
    valid_results = Column(Integer, default=0)
    duplicate_results = Column(Integer, default=0)

    execution_time_ms = Column(Integer, nullable=True)
    pages_scraped = Column(Integer, default=0)
    websites_searched = Column(JSONB, default=list)

    started_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)

    results_file_url = Column(String(500), nullable=True)
    results_summary = Column(JSONB, default=dict)
    metadata = Column(JSONB, default=dict)

    user = relationship("UserProfile", back_populates="search_history")
    search_config = relationship("SearchConfiguration", back_populates="search_history")


    def __repr__(self):
        return f"<SearchHistory(id={self.id}, user_id={self.user_id}, status='{self.status}')>"