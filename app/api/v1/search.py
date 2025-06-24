from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from app.core.security import get_current_user
from app.api.dependencies import get_database
from app.api.services.search_service import SearchService
from app.api.services.user_service import UserProfileService
from app.api.schemas.search import (
    SearchConfigurationsListResponse, SearchConfigurationSchema, SearchConfigurationDetailSchema,
    CreateSearchConfigurationRequest, UpdateSearchConfigurationRequest, DuplicateConfigurationRequest,
    ExecuteSearchRequest, SearchExecutionResponse, SearchStatusResponse,
    SearchHistoryListResponse, SearchOptionsResponse, SearchStatisticsResponse, SearchPerformanceResponse
)
from app.api.models.search_history import SearchStatus

router = APIRouter()


# Search Configurations
@router.get("/configurations", response_model=SearchConfigurationsListResponse)
async def get_search_configurations(
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
    is_template: Optional[bool] = Query(None),
    is_public: Optional[bool] = Query(None),
    created_by: Optional[UUID] = Query(None),
    search: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get list of search configurations with filtering"""
    try:
        user_service = UserProfileService(db)
        search_service = SearchService(db)
        
        # Get user profile
        profile = await user_service.get_or_create_user_profile(current_user)
        
        skip = (page - 1) * limit
        result = await search_service.get_configurations(
            user_id=UUID(profile.id),
            is_template=is_template,
            is_public=is_public,
            created_by=created_by,
            search=search,
            skip=skip,
            limit=limit
        )
        
        return SearchConfigurationsListResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving configurations: {str(e)}")


@router.get("/configurations/{config_id}", response_model=SearchConfigurationDetailSchema)
async def get_search_configuration(
    config_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get specific search configuration details"""
    try:
        user_service = UserProfileService(db)
        search_service = SearchService(db)
        
        profile = await user_service.get_or_create_user_profile(current_user)
        
        config = await search_service.get_configuration_by_id(config_id, UUID(profile.id))
        
        # Get usage statistics
        usage_stats = search_service.config_repo.get_usage_statistics(config_id)
        
        return {
            "configuration": {
                **config.__dict__,
                "created_by_name": config.creator.full_name if config.creator else None
            },
            "usage_stats": usage_stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving configuration: {str(e)}")


@router.post("/configurations", response_model=SearchConfigurationSchema)
async def create_search_configuration(
    config_data: CreateSearchConfigurationRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Create new search configuration"""
    try:
        user_service = UserProfileService(db)
        search_service = SearchService(db)
        
        profile = await user_service.get_or_create_user_profile(current_user)
        
        config = await search_service.create_configuration(UUID(profile.id), config_data)
        
        return config
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating configuration: {str(e)}")


@router.put("/configurations/{config_id}", response_model=SearchConfigurationSchema)
async def update_search_configuration(
    config_id: UUID,
    update_data: UpdateSearchConfigurationRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Update search configuration"""
    try:
        user_service = UserProfileService(db)
        search_service = SearchService(db)
        
        profile = await user_service.get_or_create_user_profile(current_user)
        
        config = await search_service.update_configuration(config_id, UUID(profile.id), update_data)
        
        return config
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating configuration: {str(e)}")


@router.delete("/configurations/{config_id}")
async def delete_search_configuration(
    config_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Delete search configuration"""
    try:
        user_service = UserProfileService(db)
        search_service = SearchService(db)
        
        profile = await user_service.get_or_create_user_profile(current_user)
        
        success = await search_service.delete_configuration(config_id, UUID(profile.id))
        
        if success:
            return {"message": "Search configuration deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete configuration")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting configuration: {str(e)}")


@router.post("/configurations/{config_id}/duplicate", response_model=SearchConfigurationSchema)
async def duplicate_search_configuration(
    config_id: UUID,
    duplicate_data: DuplicateConfigurationRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Duplicate search configuration"""
    try:
        user_service = UserProfileService(db)
        search_service = SearchService(db)
        
        profile = await user_service.get_or_create_user_profile(current_user)
        
        config = await search_service.duplicate_configuration(config_id, UUID(profile.id), duplicate_data)
        
        return config
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error duplicating configuration: {str(e)}")


# Search Execution
@router.post("/execute", response_model=SearchExecutionResponse)
async def execute_search(
    search_data: ExecuteSearchRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Execute search with configuration"""
    try:
        user_service = UserProfileService(db)
        search_service = SearchService(db)
        
        profile = await user_service.get_or_create_user_profile(current_user)
        
        search = await search_service.execute_search(UUID(profile.id), search_data)
        
        return SearchExecutionResponse(
            search={
                "id": str(search.id),
                "query_name": search.query_name,
                "status": search.status.value,
                "search_parameters": search.search_parameters,
                "filters_applied": search.filters_applied,
                "estimated_duration": 60,  # Placeholder
                "started_at": search.started_at
            },
            message="Search started successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing search: {str(e)}")


@router.get("/execute/{search_id}/status", response_model=SearchStatusResponse)
async def get_search_status(
    search_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get search execution status"""
    try:
        user_service = UserProfileService(db)
        search_service = SearchService(db)
        
        profile = await user_service.get_or_create_user_profile(current_user)
        
        search = await search_service.get_search_status(search_id, UUID(profile.id))
        
        return SearchStatusResponse(search=search)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving search status: {str(e)}")


@router.post("/execute/{search_id}/cancel")
async def cancel_search(
    search_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Cancel running search"""
    try:
        user_service = UserProfileService(db)
        search_service = SearchService(db)
        
        profile = await user_service.get_or_create_user_profile(current_user)
        
        search = await search_service.cancel_search(search_id, UUID(profile.id))
        
        return {
            "search": {
                "id": str(search.id),
                "status": search.status.value,
                "cancelled_at": search.completed_at
            },
            "message": "Search cancelled successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cancelling search: {str(e)}")


@router.get("/execute/{search_id}/results")
async def get_search_results(
    search_id: UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    quality_filter: Optional[int] = Query(None, ge=1, le=5),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get search results"""
    try:
        user_service = UserProfileService(db)
        search_service = SearchService(db)
        
        profile = await user_service.get_or_create_user_profile(current_user)
        
        search = await search_service.get_search_status(search_id, UUID(profile.id))
        
        if search.status != SearchStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Search is not completed yet")
        
        # In production, this would fetch actual results from storage
        # For now, return placeholder structure
        return {
            "results": [],  # Would contain actual lead results
            "pagination": {
                "page": page,
                "limit": limit,
                "total": search.total_results,
                "total_pages": (search.total_results + limit - 1) // limit if limit > 0 else 1
            },
            "search_info": {
                "id": str(search.id),
                "query_name": search.query_name,
                "status": search.status.value,
                "total_results": search.total_results,
                "completed_at": search.completed_at
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving search results: {str(e)}")


# Search History
@router.get("/history", response_model=SearchHistoryListResponse)
async def get_search_history(
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
    status: Optional[SearchStatus] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get user's search history"""
    try:
        user_service = UserProfileService(db)
        search_service = SearchService(db)
        
        profile = await user_service.get_or_create_user_profile(current_user)
        
        skip = (page - 1) * limit
        result = await search_service.get_search_history(
            user_id=UUID(profile.id),
            status=status,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit
        )
        
        return SearchHistoryListResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving search history: {str(e)}")


@router.get("/history/{search_id}")
async def get_search_history_detail(
    search_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get specific search history details"""
    try:
        user_service = UserProfileService(db)
        search_service = SearchService(db)
        
        profile = await user_service.get_or_create_user_profile(current_user)
        
        search = await search_service.get_search_history_detail(search_id, UUID(profile.id))
        
        # Add performance details
        performance_details = {
            "avg_page_load_time": 1500,  # Placeholder
            "requests_per_minute": 10,
            "success_rate_by_website": [
                {"website": "paginas-amarillas.es", "success_rate": 85.5, "results_found": 150},
                {"website": "11870.com", "success_rate": 78.2, "results_found": 120}
            ]
        }
        
        return {
            "search": {
                **search.__dict__,
                "user_name": search.user.full_name if search.user else None
            },
            "performance_details": performance_details
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving search details: {str(e)}")


@router.delete("/history/{search_id}")
async def delete_search_history(
    search_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Delete search history entry"""
    try:
        user_service = UserProfileService(db)
        search_service = SearchService(db)
        
        profile = await user_service.get_or_create_user_profile(current_user)
        
        success = await search_service.delete_search_history(search_id, UUID(profile.id))
        
        if success:
            return {"message": "Search history deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete search history")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting search history: {str(e)}")


# Templates & Popular Configurations
@router.get("/templates")
async def get_search_templates(
    category: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get search configuration templates"""
    try:
        search_service = SearchService(db)
        
        templates = await search_service.get_templates(category=category)
        
        # Group by category (simplified)
        categories = [
            {"name": "energia", "label": "Energía", "template_count": 3},
            {"name": "construccion", "label": "Construcción", "template_count": 2},
            {"name": "tecnologia", "label": "Tecnología", "template_count": 4}
        ]
        
        return {
            "templates": [
                {
                    **template.__dict__,
                    "created_by_name": template.creator.full_name if template.creator else None,
                    "success_rate": 85.0,  # Placeholder
                    "avg_results": 150     # Placeholder
                }
                for template in templates
            ],
            "categories": categories
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving templates: {str(e)}")


@router.get("/popular")
async def get_popular_configurations(
    limit: int = Query(10, ge=1, le=50),
    period: str = Query("30d", regex="^(7d|30d|90d)$"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get popular search configurations"""
    try:
        search_service = SearchService(db)
        
        popular_configs = await search_service.get_popular_configurations(limit=limit)
        
        # Placeholder data for trending keywords and locations
        trending_keywords = [
            {"keyword": "energia solar", "usage_count": 45, "growth_rate": 15.2},
            {"keyword": "construccion", "usage_count": 38, "growth_rate": 8.7},
            {"keyword": "tecnologia", "usage_count": 32, "growth_rate": 22.1}
        ]
        
        popular_locations = [
            {"location": "Madrid", "search_count": 156, "avg_results": 180},
            {"location": "Barcelona", "search_count": 124, "avg_results": 165},
            {"location": "Valencia", "search_count": 89, "avg_results": 142}
        ]
        
        return {
            "popular_configs": [
                {
                    **config.__dict__,
                    "created_by_name": config.creator.full_name if config.creator else None,
                    "success_rate": 85.0,  # Placeholder
                    "avg_results": 150     # Placeholder
                }
                for config in popular_configs
            ],
            "trending_keywords": trending_keywords,
            "popular_locations": popular_locations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving popular configurations: {str(e)}")


# Search Analytics & Performance
@router.get("/analytics/performance", response_model=SearchPerformanceResponse)
async def get_search_performance(
    user_id: Optional[UUID] = Query(None),
    days: int = Query(30, ge=1, le=365),
    config_id: Optional[UUID] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get search performance analytics"""
    try:
        user_service = UserProfileService(db)
        search_service = SearchService(db)
        
        profile = await user_service.get_or_create_user_profile(current_user)
        
        # If no user_id specified, use current user
        if not user_id:
            user_id = UUID(profile.id)
        
        result = await search_service.get_performance_analytics(
            user_id=user_id,
            days=days,
            config_id=config_id
        )
        
        return SearchPerformanceResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving performance analytics: {str(e)}")


@router.get("/analytics/statistics", response_model=SearchStatisticsResponse)
async def get_search_statistics(
    period: str = Query("30d", regex="^(7d|30d|90d)$"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get search statistics for user"""
    try:
        user_service = UserProfileService(db)
        search_service = SearchService(db)
        
        profile = await user_service.get_or_create_user_profile(current_user)
        
        result = await search_service.get_search_statistics(UUID(profile.id), period=period)
        
        return SearchStatisticsResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving search statistics: {str(e)}")


# Search Options & Configuration
@router.get("/options", response_model=SearchOptionsResponse)
async def get_search_options(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get available search options and parameters"""
    try:
        search_service = SearchService(db)
        
        options = await search_service.get_search_options()
        
        return SearchOptionsResponse(**options)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving search options: {str(e)}")