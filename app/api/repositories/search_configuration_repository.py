from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, and_, or_, func
from datetime import datetime
from uuid import UUID

from app.api.repositories.base import BaseRepository
from app.api.models.search_configuration import SearchConfiguration
from app.api.models.user import UserProfile


class SearchConfigurationRepository(BaseRepository[SearchConfiguration, dict, dict]):
    def __init__(self, db: Session):
        super().__init__(db, SearchConfiguration)


    def get_with_creator(self, config_id: UUID) -> Optional[SearchConfiguration]:
        return self.db.query(SearchConfiguration).options(
            joinedload(SearchConfiguration.creator)
        ).filter(SearchConfiguration.id == config_id).first()


    def get_user_configurations(
        self,
        user_id: UUID,
        include_public: bool = True,
        include_templates: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> List[SearchConfiguration]:
        query = self.db.query(SearchConfiguration).options(
            joinedload(SearchConfiguration.creator)
        )
        
        filter_conditions = [SearchConfiguration.created_by == user_id]
        
        if include_public:
            filter_conditions.append(SearchConfiguration.is_public == True)
        
        if include_templates:
            filter_conditions.append(SearchConfiguration.is_template == True)
        
        query = query.filter(or_(*filter_conditions))
        
        return query.order_by(desc(SearchConfiguration.last_used_at), desc(SearchConfiguration.created_at)).offset(skip).limit(limit).all()


    def search_configurations(
        self,
        user_id: UUID,
        search_term: str = None,
        is_template: bool = None,
        is_public: bool = None,
        created_by: UUID = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[SearchConfiguration]:
        query = self.db.query(SearchConfiguration).options(
            joinedload(SearchConfiguration.creator)
        )
        
        base_filters = [
            SearchConfiguration.created_by == user_id,
            SearchConfiguration.is_public == True,
            SearchConfiguration.is_template == True
        ]
        query = query.filter(or_(*base_filters))
        

        if search_term:
            query = query.filter(
                or_(
                    SearchConfiguration.name.ilike(f"%{search_term}%"),
                    SearchConfiguration.description.ilike(f"%{search_term}%")
                )
            )
        
        if is_template is not None:
            query = query.filter(SearchConfiguration.is_template == is_template)
        
        if is_public is not None:
            query = query.filter(SearchConfiguration.is_public == is_public)
        
        if created_by:
            query = query.filter(SearchConfiguration.created_by == created_by)
        
        return query.order_by(desc(SearchConfiguration.usage_count), desc(SearchConfiguration.last_used_at)).offset(skip).limit(limit).all()


    def get_popular_configurations(self, limit: int = 10) -> List[SearchConfiguration]:
        return self.db.query(SearchConfiguration).options(
            joinedload(SearchConfiguration.creator)
        ).filter(
            or_(
                SearchConfiguration.is_public == True,
                SearchConfiguration.is_template == True
            )
        ).order_by(desc(SearchConfiguration.usage_count), desc(SearchConfiguration.last_used_at)).limit(limit).all()


    def get_templates(self, category: str = None) -> List[SearchConfiguration]:
        query = self.db.query(SearchConfiguration).options(
            joinedload(SearchConfiguration.creator)
        ).filter(SearchConfiguration.is_template == True)
        
        if category:
            pass
        
        return query.order_by(desc(SearchConfiguration.usage_count), SearchConfiguration.name).all()


    def increment_usage_count(self, config_id: UUID) -> Optional[SearchConfiguration]:
        config = self.get(config_id)
        if config:
            config.usage_count += 1
            config.last_used_at = datetime.utcnow()
            config.updated_at = datetime.utcnow()
            self.db.add(config)
            self.db.commit()
            self.db.refresh(config)
        return config


    def duplicate_configuration(
        self,
        config_id: UUID,
        new_name: str,
        new_description: str = None,
        user_id: UUID = None
    ) -> Optional[SearchConfiguration]:
        original = self.get(config_id)
        if not original:
            return None
        
        new_config = SearchConfiguration(
            name=new_name,
            description=new_description or original.description,
            client_types=original.client_types,
            locations=original.locations,
            websites=original.websites,
            validate_emails=original.validate_emails,
            validate_websites=original.validate_websites,
            validate_phones=original.validate_phones,
            company_size_min=original.company_size_min,
            company_size_max=original.company_size_max,
            industries=original.industries,
            job_titles=original.job_titles,
            keywords=original.keywords,
            exclude_keywords=original.exclude_keywords,
            created_by=user_id or original.created_by,
            is_template=False,
            is_public=False,  
            metadata=original.metadata.copy() if original.metadata else {},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.db.add(new_config)
        self.db.commit()
        self.db.refresh(new_config)
        return new_config


    def get_configurations_by_user(self, user_id: UUID) -> List[SearchConfiguration]:
        return self.db.query(SearchConfiguration).filter(
            SearchConfiguration.created_by == user_id
        ).order_by(desc(SearchConfiguration.created_at)).all()


    def get_usage_statistics(self, config_id: UUID) -> Dict[str, Any]:
        from app.api.models.search_history import SearchHistory
        
        config = self.get(config_id)
        if not config:
            return {}
        
        search_stats = self.db.query(
            func.count(SearchHistory.id).label('total_searches'),
            func.avg(SearchHistory.total_results).label('avg_results'),
            func.count(SearchHistory.id).filter(SearchHistory.status == 'completed').label('successful_searches')
        ).filter(SearchHistory.search_config_id == config_id).first()
        
        total_searches = search_stats.total_searches or 0
        success_rate = 0
        if total_searches > 0:
            success_rate = (search_stats.successful_searches / total_searches) * 100
        
        return {
            "total_searches": total_searches,
            "avg_results_per_search": round(search_stats.avg_results or 0, 2),
            "success_rate": round(success_rate, 2),
            "usage_count": config.usage_count,
            "last_used_at": config.last_used_at
        }


    def cleanup_old_configurations(self, days_unused: int = 180) -> int:
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_unused)
        
        deleted_count = self.db.query(SearchConfiguration).filter(
            and_(
                SearchConfiguration.is_template == False,
                SearchConfiguration.is_public == False,
                SearchConfiguration.usage_count == 0,
                SearchConfiguration.created_at < cutoff_date
            )
        ).delete()
        
        self.db.commit()
        return deleted_count