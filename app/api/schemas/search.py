from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from app.api.models.search_history import SearchStatus


# Search Configuration Schemas
class CreateSearchConfigurationRequest(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    client_types: Optional[List[str]] = []
    locations: Optional[List[str]] = []
    websites: Optional[List[str]] = []
    validate_emails: bool = True
    validate_websites: bool = True
    validate_phones: bool = False
    company_size_min: Optional[int] = None
    company_size_max: Optional[int] = None
    industries: Optional[List[str]] = []
    job_titles: Optional[List[str]] = []
    keywords: Optional[str] = None
    exclude_keywords: Optional[str] = None
    is_template: bool = False
    is_public: bool = False
    metadata: Optional[Dict[str, Any]] = {}

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Empresas de Energía Solar en Madrid",
                "description": "Búsqueda de empresas especializadas en energía solar",
                "client_types": ["empresas", "pymes"],
                "locations": ["Madrid", "Barcelona"],
                "validate_emails": True,
                "validate_websites": True,
                "keywords": "energía solar, paneles solares",
                "is_public": False
            }
        }


class UpdateSearchConfigurationRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    client_types: Optional[List[str]] = None
    locations: Optional[List[str]] = None
    websites: Optional[List[str]] = None
    validate_emails: Optional[bool] = None
    validate_websites: Optional[bool] = None
    validate_phones: Optional[bool] = None
    company_size_min: Optional[int] = None
    company_size_max: Optional[int] = None
    industries: Optional[List[str]] = None
    job_titles: Optional[List[str]] = None
    keywords: Optional[str] = None
    exclude_keywords: Optional[str] = None
    is_public: Optional[bool] = None


class SearchConfigurationSchema(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    client_types: List[str] = []
    locations: List[str] = []
    websites: List[str] = []
    validate_emails: bool
    validate_websites: bool
    validate_phones: bool
    company_size_min: Optional[int] = None
    company_size_max: Optional[int] = None
    industries: List[str] = []
    job_titles: List[str] = []
    keywords: Optional[str] = None
    exclude_keywords: Optional[str] = None
    is_template: bool
    is_public: bool
    usage_count: int
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SearchConfigurationDetailSchema(SearchConfigurationSchema):
    metadata: Dict[str, Any] = {}
    created_by_name: Optional[str] = None


# Search Execution Schemas
class ExecuteSearchRequest(BaseModel):
    query_name: Optional[str] = None
    search_config_id: Optional[UUID] = None
    search_parameters: Dict[str, Any] = Field(..., description="Search parameters")
    filters_applied: Optional[Dict[str, Any]] = {}

    class Config:
        json_schema_extra = {
            "example": {
                "query_name": "Búsqueda de empresas solares",
                "search_config_id": "123e4567-e89b-12d3-a456-426614174000",
                "search_parameters": {
                    "client_types": ["empresas"],
                    "locations": ["Madrid"],
                    "validate_emails": True,
                    "max_results": 100
                }
            }
        }


class SearchHistorySchema(BaseModel):
    id: UUID
    user_id: UUID
    search_config_id: Optional[UUID] = None
    query_name: Optional[str] = None
    search_parameters: Dict[str, Any]
    filters_applied: Dict[str, Any] = {}
    status: SearchStatus
    total_results: int
    valid_results: int
    duplicate_results: int
    execution_time_ms: Optional[int] = None
    pages_scraped: int
    websites_searched: List[str] = []
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    results_file_url: Optional[str] = None
    results_summary: Dict[str, Any] = {}

    class Config:
        from_attributes = True


class SearchHistoryDetailSchema(SearchHistorySchema):
    user_name: Optional[str] = None
    config_name: Optional[str] = None
    metadata: Dict[str, Any] = {}


# Response Schemas
class SearchConfigurationsListResponse(BaseModel):
    configurations: List[SearchConfigurationSchema]
    pagination: Dict[str, Any]


class SearchHistoryListResponse(BaseModel):
    history: List[SearchHistoryDetailSchema]
    pagination: Dict[str, Any]
    statistics: Optional[Dict[str, Any]] = None


class SearchExecutionResponse(BaseModel):
    search: Dict[str, Any]
    message: str


class SearchStatusResponse(BaseModel):
    search: SearchHistorySchema


class DuplicateConfigurationRequest(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Copia de configuración energía solar",
                "description": "Configuración duplicada para nuevas búsquedas"
            }
        }


# Search Options Schemas
class SearchOptionValue(BaseModel):
    value: str
    label: str
    description: Optional[str] = None


class SearchLocationOption(BaseModel):
    value: str
    label: str
    country: str
    region: Optional[str] = None


class SearchWebsiteOption(BaseModel):
    domain: str
    name: str
    description: str
    is_active: bool
    success_rate: Optional[float] = None


class SearchOptionsResponse(BaseModel):
    options: Dict[str, List[Any]]
    validation_options: Dict[str, Any]


# Analytics Schemas
class SearchStatisticsResponse(BaseModel):
    statistics: Dict[str, Any]
    monthly_breakdown: List[Dict[str, Any]]
    quality_distribution: Dict[str, int]


class SearchPerformanceResponse(BaseModel):
    performance: Dict[str, Any]
    trends: Dict[str, List[Dict[str, Any]]]
    website_performance: List[Dict[str, Any]]