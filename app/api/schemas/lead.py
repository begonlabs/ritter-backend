from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# Lead Schemas
class LeadSchema(BaseModel):
    id: UUID
    email: Optional[str] = None
    verified_email: bool = False
    phone: Optional[str] = None
    verified_phone: bool = False
    company_name: str
    company_website: Optional[str] = None
    verified_website: bool = False
    address: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    activity: str
    description: Optional[str] = None
    category: Optional[str] = None
    data_quality_score: int
    created_at: datetime
    updated_at: datetime
    last_contacted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UpdateLeadRequest(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    address: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    activity: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    last_contacted_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "email": "contacto@empresa.com",
                "phone": "+34 912 345 678",
                "company_name": "Empresa Solar SA",
                "category": "Energía Renovable",
                "description": "Empresa especializada en energía solar"
            }
        }


class BulkUpdateLeadsRequest(BaseModel):
    lead_ids: List[UUID] = Field(..., description="List of lead IDs to update")
    updates: Dict[str, Any] = Field(..., description="Fields to update")

    class Config:
        json_schema_extra = {
            "example": {
                "lead_ids": ["123e4567-e89b-12d3-a456-426614174000"],
                "updates": {
                    "category": "Energía Renovable",
                    "last_contacted_at": "2024-01-15T10:30:00Z"
                }
            }
        }


class BulkDeleteLeadsRequest(BaseModel):
    lead_ids: List[UUID] = Field(..., description="List of lead IDs to delete")

    class Config:
        json_schema_extra = {
            "example": {
                "lead_ids": ["123e4567-e89b-12d3-a456-426614174000"]
            }
        }


# Lead Detail Schema with additional information
class LeadDetailSchema(LeadSchema):
    contact_history: List[Dict[str, Any]] = []
    related_leads: List[Dict[str, Any]] = []


# Response Schemas
class LeadsListResponse(BaseModel):
    leads: List[LeadSchema]
    pagination: Dict[str, Any]
    filters_applied: Dict[str, Any]
    summary: Dict[str, Any]


class LeadDetailResponse(BaseModel):
    lead: LeadDetailSchema


class LeadStatisticsResponse(BaseModel):
    statistics: Dict[str, Any]
    top_categories: List[Dict[str, Any]]
    top_states: List[Dict[str, Any]]
    trends: Dict[str, List[Dict[str, Any]]]


class LeadQualityAnalysisResponse(BaseModel):
    quality_analysis: Dict[str, Any]
    quality_by_source: List[Dict[str, Any]]
    improvement_opportunities: Dict[str, Any]


class LeadExportResponse(BaseModel):
    export: Dict[str, Any]
    filters_applied: Dict[str, Any]
    fields_exported: List[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "export": {
                    "data": [{"company_name": "Empresa Solar", "email": "contacto@solar.com"}],  # For JSON format
                    "content": "company_name,email\nEmpresa Solar,contacto@solar.com",  # For CSV format
                    "file_name": "leads_export_20240115_103000.json",
                    "file_size": 1024,
                    "format": "json",
                    "total_records": 150,
                    "expires_at": "2024-01-15T10:30:00Z"
                },
                "filters_applied": {"min_quality_score": 3},
                "fields_exported": ["company_name", "email", "phone"]
            }
        }


# Import/Export Schemas
class LeadImportRequest(BaseModel):
    mapping: Dict[str, str] = Field(..., description="Field mapping configuration")
    skip_duplicates: bool = True
    validate_emails: bool = True
    validate_phones: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "mapping": {
                    "company_name": "Nombre Empresa",
                    "email": "Email",
                    "phone": "Teléfono",
                    "activity": "Actividad"
                },
                "skip_duplicates": True,
                "validate_emails": True
            }
        }


class ImportJobSchema(BaseModel):
    id: UUID
    status: str
    total_rows: int
    processed_rows: int
    imported_leads: int
    skipped_duplicates: int
    validation_errors: int
    error_details: List[str] = []
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ImportJobResponse(BaseModel):
    import_job: ImportJobSchema  # Renamed from import (reserved keyword)
    message: str


# Validation Schemas
class ValidateLeadsRequest(BaseModel):
    lead_ids: List[UUID] = Field(..., description="List of lead IDs to validate")
    validation_types: List[str] = Field(default=["email"], description="Types of validation to perform")
    update_records: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "lead_ids": ["123e4567-e89b-12d3-a456-426614174000"],
                "validation_types": ["email", "phone", "website"],
                "update_records": True
            }
        }


class ValidationJobSchema(BaseModel):
    id: UUID
    status: str
    progress: float = 0.0
    total_leads: int
    processed_leads: int
    validation_types: List[str]
    results: Dict[str, int] = {}
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ValidationJobResponse(BaseModel):
    validation: ValidationJobSchema
    message: str


# Deduplication Schemas
class DeduplicateLeadsRequest(BaseModel):
    strategy: str = Field(default="email", description="Deduplication strategy")
    auto_merge: bool = False
    keep_highest_quality: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "strategy": "fuzzy_match",
                "auto_merge": False,
                "keep_highest_quality": True
            }
        }


class DeduplicationJobSchema(BaseModel):
    id: UUID
    status: str
    strategy: str
    duplicates_found: int = 0
    leads_merged: int = 0
    leads_removed: int = 0
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DeduplicationJobResponse(BaseModel):
    deduplication: DeduplicationJobSchema
    message: str


# Search and Filter Schemas
class LeadSearchResponse(BaseModel):
    search_results: List[Dict[str, Any]]
    pagination: Dict[str, Any]
    search_info: Dict[str, Any]


class FilterOption(BaseModel):
    value: str
    label: str
    count: int


class QualityScoreOption(BaseModel):
    score: int
    count: int
    percentage: float


class LeadFilterOptionsResponse(BaseModel):
    filter_options: Dict[str, List[FilterOption]]
    summary: Dict[str, Any]


# Bulk Operation Responses
class BulkOperationResponse(BaseModel):
    updated_count: Optional[int] = None
    deleted_count: Optional[int] = None
    message: str