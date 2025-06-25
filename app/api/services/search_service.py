from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from app.api.models.search_configuration import SearchConfiguration
from app.api.models.search_history import SearchHistory, SearchStatus
from app.api.repositories.search_configuration_repository import SearchConfigurationRepository
from app.api.repositories.search_history_repository import SearchHistoryRepository
from app.api.repositories.user_repository import UserRepository
from app.api.schemas.search import (
    CreateSearchConfigurationRequest, UpdateSearchConfigurationRequest,
    ExecuteSearchRequest, DuplicateConfigurationRequest
)
from fastapi import HTTPException


class SearchService:
    def __init__(self, db: Session):
        self.db = db
        self.config_repo = SearchConfigurationRepository(db)
        self.history_repo = SearchHistoryRepository(db)
        self.user_repo = UserRepository(db)

    # Search Configuration Methods
    async def get_configurations(
        self,
        user_id: UUID,
        is_template: bool = None,
        is_public: bool = None,
        created_by: UUID = None,
        search: str = None,
        skip: int = 0,
        limit: int = 25
    ) -> Dict[str, Any]:
        """Get search configurations with filtering"""
        configurations = self.config_repo.search_configurations(
            user_id=user_id,
            search_term=search,
            is_template=is_template,
            is_public=is_public,
            created_by=created_by,
            skip=skip,
            limit=limit
        )
        
        # Get creator names
        for config in configurations:
            if config.creator:
                config.created_by_name = config.creator.full_name
        
        total = self.config_repo.count({"created_by": user_id} if not is_public and not is_template else {})
        
        return {
            "configurations": configurations,
            "pagination": {
                "page": (skip // limit) + 1 if limit > 0 else 1,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit if limit > 0 else 1
            }
        }

    async def get_configuration_by_id(self, config_id: UUID, user_id: UUID) -> SearchConfiguration:
        """Get configuration by ID with access control"""
        config = self.config_repo.get_with_creator(config_id)
        
        if not config:
            raise HTTPException(status_code=404, detail="Search configuration not found")
        
        # Check access permissions
        if (config.created_by != user_id and 
            not config.is_public and 
            not config.is_template):
            raise HTTPException(status_code=403, detail="Access denied to this configuration")
        
        return config

    async def create_configuration(
        self,
        user_id: UUID,
        config_data: CreateSearchConfigurationRequest
    ) -> SearchConfiguration:
        """Create new search configuration"""
        # Check if name already exists for user
        existing = self.config_repo.get_by_field("name", config_data.name)
        if existing and any(c.created_by == user_id for c in (existing if isinstance(existing, list) else [existing])):
            raise HTTPException(
                status_code=400,
                detail="A configuration with this name already exists"
            )
        
        config_dict = config_data.dict()
        config_dict["created_by"] = user_id
        config_dict["created_at"] = datetime.utcnow()
        config_dict["updated_at"] = datetime.utcnow()
        
        return self.config_repo.create(config_dict)

    async def update_configuration(
        self,
        config_id: UUID,
        user_id: UUID,
        update_data: UpdateSearchConfigurationRequest
    ) -> SearchConfiguration:
        """Update search configuration"""
        config = await self.get_configuration_by_id(config_id, user_id)
        
        # Only creator can update (unless it's admin)
        if config.created_by != user_id:
            raise HTTPException(status_code=403, detail="Only the creator can update this configuration")
        
        update_dict = update_data.dict(exclude_unset=True)
        if update_dict:
            update_dict["updated_at"] = datetime.utcnow()
            return self.config_repo.update(config, update_dict)
        
        return config

    async def delete_configuration(self, config_id: UUID, user_id: UUID) -> bool:
        """Delete search configuration"""
        config = await self.get_configuration_by_id(config_id, user_id)
        
        # Only creator can delete
        if config.created_by != user_id:
            raise HTTPException(status_code=403, detail="Only the creator can delete this configuration")
        
        # Check if configuration has been used
        if config.usage_count > 0:
            # You might want to soft delete or ask for confirmation
            pass
        
        deleted = self.config_repo.delete(config_id)
        return deleted is not None

    async def duplicate_configuration(
        self,
        config_id: UUID,
        user_id: UUID,
        duplicate_data: DuplicateConfigurationRequest
    ) -> SearchConfiguration:
        """Duplicate an existing configuration"""
        # Check if original exists and is accessible
        await self.get_configuration_by_id(config_id, user_id)
        
        duplicated = self.config_repo.duplicate_configuration(
            config_id=config_id,
            new_name=duplicate_data.name,
            new_description=duplicate_data.description,
            user_id=user_id
        )
        
        if not duplicated:
            raise HTTPException(status_code=500, detail="Failed to duplicate configuration")
        
        return duplicated

    async def get_templates(self, category: str = None) -> List[SearchConfiguration]:
        """Get configuration templates"""
        return self.config_repo.get_templates(category=category)

    async def get_popular_configurations(self, limit: int = 10) -> List[SearchConfiguration]:
        """Get popular public configurations"""
        return self.config_repo.get_popular_configurations(limit=limit)

    # Search Execution Methods
    async def execute_search(
        self,
        user_id: UUID,
        search_data: ExecuteSearchRequest
    ) -> SearchHistory:
        """Execute a search"""
        # Validate search configuration if provided
        if search_data.search_config_id:
            config = await self.get_configuration_by_id(search_data.search_config_id, user_id)
            # Increment usage count
            self.config_repo.increment_usage_count(search_data.search_config_id)
        
        # Create search history entry
        search_history = self.history_repo.create_search_history(
            user_id=user_id,
            search_parameters=search_data.search_parameters,
            query_name=search_data.query_name,
            search_config_id=search_data.search_config_id,
            filters_applied=search_data.filters_applied
        )
        
        # Here you would trigger the actual search process
        # For now, we'll just update status to in_progress
        self.history_repo.update_search_status(
            search_id=search_history.id,
            status=SearchStatus.IN_PROGRESS
        )
        
        # TODO: Implement actual search execution logic
        # This would typically involve:
        # 1. Sending search parameters to scraping service
        # 2. Monitoring progress
        # 3. Processing results
        # 4. Updating status and results
        
        return search_history

    async def get_search_status(self, search_id: UUID, user_id: UUID) -> SearchHistory:
        """Get search execution status"""
        search = self.history_repo.get_with_details(search_id)
        
        if not search:
            raise HTTPException(status_code=404, detail="Search not found")
        
        if search.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied to this search")
        
        return search

    async def cancel_search(self, search_id: UUID, user_id: UUID) -> SearchHistory:
        """Cancel a running search"""
        search = await self.get_search_status(search_id, user_id)
        
        if search.status not in [SearchStatus.PENDING, SearchStatus.IN_PROGRESS]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot cancel search with status: {search.status}"
            )
        
        cancelled_search = self.history_repo.cancel_search(search_id)
        if not cancelled_search:
            raise HTTPException(status_code=500, detail="Failed to cancel search")
        
        return cancelled_search

    # Search History Methods
    async def get_search_history(
        self,
        user_id: UUID,
        status: SearchStatus = None,
        start_date: datetime = None,
        end_date: datetime = None,
        skip: int = 0,
        limit: int = 25
    ) -> Dict[str, Any]:
        """Get user's search history"""
        history = self.history_repo.get_user_search_history(
            user_id=user_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit
        )
        
        # Add user and config names
        for search in history:
            if search.user:
                search.user_name = search.user.full_name
            if search.search_config:
                search.config_name = search.search_config.name
        
        # Get statistics
        statistics = self.history_repo.get_search_statistics(user_id=user_id)
        most_used_config = self.history_repo.get_most_used_config(user_id=user_id)
        
        statistics["most_productive_config"] = most_used_config
        
        total = self.history_repo.count({"user_id": user_id})
        
        return {
            "history": history,
            "pagination": {
                "page": (skip // limit) + 1 if limit > 0 else 1,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit if limit > 0 else 1
            },
            "statistics": statistics
        }

    async def get_search_history_detail(self, search_id: UUID, user_id: UUID) -> SearchHistory:
        """Get detailed search history"""
        search = await self.get_search_status(search_id, user_id)
        
        # Add performance details if needed
        # This could include more detailed metrics about the search execution
        
        return search

    async def delete_search_history(self, search_id: UUID, user_id: UUID) -> bool:
        """Delete search history entry"""
        search = await self.get_search_status(search_id, user_id)
        
        deleted = self.history_repo.delete(search_id)
        return deleted is not None

    # Analytics Methods
    async def get_search_statistics(self, user_id: UUID, period: str = "30d") -> Dict[str, Any]:
        """Get search statistics for user"""
        days_back = {"7d": 7, "30d": 30, "90d": 90}.get(period, 30)
        
        statistics = self.history_repo.get_search_statistics(user_id=user_id, days_back=days_back)
        most_used_config = self.history_repo.get_most_used_config(user_id=user_id)
        
        # Get monthly breakdown
        monthly_trends = self.history_repo.get_performance_trends(user_id=user_id, days_back=days_back)
        
        # Get favorite locations and client types (would need to analyze search parameters)
        favorite_locations = []  # TODO: Implement based on search_parameters analysis
        favorite_client_types = []  # TODO: Implement based on search_parameters analysis
        
        return {
            "statistics": {
                **statistics,
                "most_used_config": most_used_config,
                "favorite_locations": favorite_locations,
                "favorite_client_types": favorite_client_types
            },
            "monthly_breakdown": [
                {
                    "month": trend["date"][:7],  # Extract YYYY-MM
                    "searches": trend["total_searches"],
                    "results": trend["total_results"],
                    "success_rate": round((trend["successful_searches"] / trend["total_searches"] * 100), 2) if trend["total_searches"] > 0 else 0
                }
                for trend in monthly_trends
            ],
            "quality_distribution": {
                "high_quality": 0,  # TODO: Implement based on results analysis
                "medium_quality": 0,
                "low_quality": 0
            }
        }

    async def get_performance_analytics(
        self,
        user_id: UUID = None,
        days: int = 30,
        config_id: UUID = None
    ) -> Dict[str, Any]:
        """Get search performance analytics"""
        performance_stats = self.history_repo.get_search_statistics(
            user_id=user_id,
            days_back=days
        )
        
        trends = self.history_repo.get_performance_trends(
            user_id=user_id,
            days_back=days
        )
        
        website_performance = self.history_repo.get_website_performance(days_back=days)
        
        return {
            "performance": performance_stats,
            "trends": {
                "daily_performance": trends
            },
            "website_performance": website_performance
        }

    async def get_search_options(self) -> Dict[str, Any]:
        """Get available search options and parameters"""
        # This would typically come from configuration or database
        # For now, returning static options
        return {
            "options": {
                "client_types": [
                    {"value": "empresas", "label": "Empresas", "description": "Empresas en general"},
                    {"value": "pymes", "label": "PYMES", "description": "Pequeñas y medianas empresas"},
                    {"value": "autonomos", "label": "Autónomos", "description": "Trabajadores autónomos"},
                    {"value": "startups", "label": "Startups", "description": "Empresas emergentes"}
                ],
                "locations": [
                    {"value": "madrid", "label": "Madrid", "country": "España", "region": "Madrid"},
                    {"value": "barcelona", "label": "Barcelona", "country": "España", "region": "Cataluña"},
                    {"value": "valencia", "label": "Valencia", "country": "España", "region": "Valencia"},
                    {"value": "sevilla", "label": "Sevilla", "country": "España", "region": "Andalucía"}
                ],
                "websites": [
                    {"domain": "paginas-amarillas.es", "name": "Páginas Amarillas", "description": "Directorio empresarial", "is_active": True, "success_rate": 85.5},
                    {"domain": "11870.com", "name": "11870", "description": "Guía de empresas", "is_active": True, "success_rate": 78.2},
                    {"domain": "cylex.es", "name": "Cylex", "description": "Directorio de negocios", "is_active": True, "success_rate": 72.8}
                ],
                "industries": [
                    {"value": "energia", "label": "Energía", "parent_category": "Servicios"},
                    {"value": "construccion", "label": "Construcción", "parent_category": "Industria"},
                    {"value": "tecnologia", "label": "Tecnología", "parent_category": "Servicios"},
                    {"value": "comercio", "label": "Comercio", "parent_category": "Comercial"}
                ],
                "company_sizes": [
                    {"range": "1-10", "min": 1, "max": 10},
                    {"range": "11-50", "min": 11, "max": 50},
                    {"range": "51-200", "min": 51, "max": 200},
                    {"range": "200+", "min": 200, "max": None}
                ]
            },
            "validation_options": {
                "email_validation": {
                    "available": True,
                    "cost_per_validation": 0.001,
                    "accuracy": 95.0
                },
                "phone_validation": {
                    "available": True,
                    "cost_per_validation": 0.002,
                    "accuracy": 90.0
                },
                "website_validation": {
                    "available": True,
                    "cost_per_validation": 0.001,
                    "accuracy": 92.0
                }
            }
        }