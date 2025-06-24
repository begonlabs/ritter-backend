from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID

from app.core.security import get_current_user
from app.api.dependencies import get_database
from app.api.services.lead_service import LeadService
from app.api.services.user_service import UserProfileService
from app.api.schemas.lead import (
    LeadsListResponse, LeadDetailResponse, LeadSchema, UpdateLeadRequest,
    BulkUpdateLeadsRequest, BulkDeleteLeadsRequest, BulkOperationResponse,
    LeadStatisticsResponse, LeadQualityAnalysisResponse, LeadExportResponse,
    LeadImportRequest, ImportJobResponse, ValidateLeadsRequest, ValidationJobResponse,
    DeduplicateLeadsRequest, DeduplicationJobResponse, LeadSearchResponse,
    LeadFilterOptionsResponse
)

router = APIRouter()


# Lead Management
@router.get("/leads", response_model=LeadsListResponse)
async def get_leads(
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
    search: Optional[str] = Query(None),
    min_quality_score: int = Query(1, ge=1, le=5),
    verified_email: Optional[bool] = Query(None),
    verified_phone: Optional[bool] = Query(None),
    verified_website: Optional[bool] = Query(None),
    categories: Optional[List[str]] = Query(None),
    states: Optional[List[str]] = Query(None),
    countries: Optional[List[str]] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get leads with advanced filtering and search"""
    try:
        lead_service = LeadService(db)
        
        result = await lead_service.get_leads(
            page=page,
            limit=limit,
            search=search,
            min_quality_score=min_quality_score,
            verified_email=verified_email,
            verified_phone=verified_phone,
            verified_website=verified_website,
            categories=categories,
            states=states,
            countries=countries,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return LeadsListResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving leads: {str(e)}")


@router.get("/leads/{lead_id}", response_model=LeadDetailResponse)
async def get_lead_by_id(
    lead_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get specific lead details"""
    try:
        lead_service = LeadService(db)
        
        result = await lead_service.get_lead_by_id(lead_id)
        
        return LeadDetailResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving lead: {str(e)}")


@router.put("/leads/{lead_id}", response_model=LeadSchema)
async def update_lead(
    lead_id: UUID,
    update_data: UpdateLeadRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Update lead information"""
    try:
        lead_service = LeadService(db)
        
        lead = await lead_service.update_lead(lead_id, update_data)
        
        return lead
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating lead: {str(e)}")


@router.delete("/leads/{lead_id}")
async def delete_lead(
    lead_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Delete lead"""
    try:
        lead_service = LeadService(db)
        
        success = await lead_service.delete_lead(lead_id)
        
        if success:
            return {"message": "Lead deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete lead")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting lead: {str(e)}")


@router.post("/leads/bulk-update", response_model=BulkOperationResponse)
async def bulk_update_leads(
    request: BulkUpdateLeadsRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Bulk update multiple leads"""
    try:
        lead_service = LeadService(db)
        
        result = await lead_service.bulk_update_leads(request)
        
        return BulkOperationResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error bulk updating leads: {str(e)}")


@router.delete("/leads/bulk-delete", response_model=BulkOperationResponse)
async def bulk_delete_leads(
    request: BulkDeleteLeadsRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Bulk delete multiple leads"""
    try:
        lead_service = LeadService(db)
        
        result = await lead_service.bulk_delete_leads(request)
        
        return BulkOperationResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error bulk deleting leads: {str(e)}")


# Lead Statistics & Analytics
@router.get("/statistics", response_model=LeadStatisticsResponse)
async def get_lead_statistics(
    period: str = Query("all", regex="^(all|30d|7d|1d)$"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get lead statistics and distribution"""
    try:
        lead_service = LeadService(db)
        
        result = await lead_service.get_lead_statistics(period=period)
        
        return LeadStatisticsResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")


@router.get("/quality-analysis", response_model=LeadQualityAnalysisResponse)
async def get_quality_analysis(
    category: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get detailed lead quality analysis"""
    try:
        lead_service = LeadService(db)
        
        result = await lead_service.get_quality_analysis(category=category, state=state)
        
        return LeadQualityAnalysisResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving quality analysis: {str(e)}")


# Lead Export & Data Management
@router.get("/export", response_model=LeadExportResponse)
async def export_leads(
    format: str = Query("csv", regex="^(csv|xlsx|json|vcf)$"),
    filters: Optional[str] = Query(None, description="JSON string of filters"),
    fields: Optional[List[str]] = Query(None),
    include_contact_history: bool = Query(False),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Export leads to various formats"""
    try:
        lead_service = LeadService(db)
        
        # Parse filters if provided
        filters_dict = {}
        if filters:
            import json
            try:
                filters_dict = json.loads(filters)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid filters JSON format")
        
        result = await lead_service.export_leads(
            format=format,
            filters=filters_dict,
            fields=fields,
            include_contact_history=include_contact_history
        )
        
        return LeadExportResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting leads: {str(e)}")


@router.post("/import", response_model=ImportJobResponse)
async def import_leads(
    file: UploadFile = File(...),
    mapping: str = Query(..., description="JSON string of field mapping"),
    skip_duplicates: bool = Query(True),
    validate_emails: bool = Query(True),
    validate_phones: bool = Query(False),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Import leads from CSV/Excel file"""
    try:
        lead_service = LeadService(db)
        
        # Parse mapping
        import json
        try:
            mapping_dict = json.loads(mapping)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid mapping JSON format")
        
        result = await lead_service.import_leads(
            file=file,
            mapping=mapping_dict,
            skip_duplicates=skip_duplicates,
            validate_emails=validate_emails,
            validate_phones=validate_phones
        )
        
        return ImportJobResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error importing leads: {str(e)}")


@router.get("/import/{import_id}/status", response_model=ImportJobResponse)
async def get_import_status(
    import_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get import job status"""
    try:
        # In production, this would retrieve actual import job status
        # For now, return placeholder structure
        return {
            "import": {
                "id": str(import_id),
                "status": "completed",
                "total_rows": 100,
                "processed_rows": 100,
                "imported_leads": 95,
                "skipped_duplicates": 3,
                "validation_errors": 2,
                "error_details": ["Invalid email format in row 5", "Missing company name in row 12"],
                "started_at": "2024-01-15T10:00:00Z",
                "completed_at": "2024-01-15T10:05:00Z"
            },
            "message": "Import completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving import status: {str(e)}")


# Lead Validation & Data Quality
@router.post("/validate", response_model=ValidationJobResponse)
async def validate_leads(
    request: ValidateLeadsRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Validate lead data (emails, phones, websites)"""
    try:
        lead_service = LeadService(db)
        
        result = await lead_service.validate_leads(request)
        
        return ValidationJobResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating leads: {str(e)}")


@router.get("/validate/{validation_id}/status", response_model=ValidationJobResponse)
async def get_validation_status(
    validation_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get validation job status"""
    try:
        # In production, this would retrieve actual validation job status
        # For now, return placeholder structure
        return {
            "validation": {
                "id": str(validation_id),
                "status": "completed",
                "progress": 100.0,
                "total_leads": 50,
                "processed_leads": 50,
                "validation_types": ["email", "phone"],
                "results": {
                    "valid_emails": 45,
                    "invalid_emails": 5,
                    "valid_phones": 42,
                    "invalid_phones": 8,
                    "valid_websites": 0,
                    "invalid_websites": 0
                },
                "started_at": "2024-01-15T10:00:00Z",
                "completed_at": "2024-01-15T10:02:00Z"
            },
            "message": "Validation completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving validation status: {str(e)}")


@router.post("/deduplicate", response_model=DeduplicationJobResponse)
async def deduplicate_leads(
    request: DeduplicateLeadsRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Find and remove duplicate leads"""
    try:
        lead_service = LeadService(db)
        
        result = await lead_service.deduplicate_leads(request)
        
        return DeduplicationJobResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deduplicating leads: {str(e)}")


# Lead Search & Filtering
@router.get("/search", response_model=LeadSearchResponse)
async def search_leads(
    q: str = Query(..., description="Search query"),
    fields: Optional[List[str]] = Query(None, description="Fields to search in"),
    exact_match: bool = Query(False),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Advanced lead search with full-text search"""
    try:
        lead_service = LeadService(db)
        
        result = await lead_service.search_leads(
            query=q,
            fields=fields,
            exact_match=exact_match,
            page=page,
            limit=limit
        )
        
        return LeadSearchResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching leads: {str(e)}")


@router.get("/filters/options", response_model=LeadFilterOptionsResponse)
async def get_filter_options(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get available filter options for leads"""
    try:
        lead_service = LeadService(db)
        
        result = await lead_service.get_filter_options()
        
        return LeadFilterOptionsResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving filter options: {str(e)}")