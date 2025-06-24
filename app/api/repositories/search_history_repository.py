from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, and_, or_, func
from datetime import datetime, timedelta
from uuid import UUID

from app.api.repositories.base import BaseRepository
from app.api.models.search_history import SearchHistory, SearchStatus
from app.api.models.search_configuration import SearchConfiguration
from app.api.models.user import UserProfile


class SearchHistoryRepository(BaseRepository[SearchHistory, dict, dict]):
    def __init__(self, db: Session):
        super().__init__(db, SearchHistory)


    def create_search_history(
        self,
        user_id: UUID,
        search_parameters: dict,
        query_name: str = None,
        search_config_id: UUID = None,
        filters_applied: dict = None
    ) -> SearchHistory:
        search_data = {
            "user_id": user_id,
            "search_config_id": search_config_id,
            "query_name": query_name,
            "search_parameters": search_parameters,
            "filters_applied": filters_applied or {},
            "status": SearchStatus.PENDING,
            "started_at": datetime.utcnow()
        }
        
        return self.create(search_data)


    def get_user_search_history(
        self,
        user_id: UUID,
        status: SearchStatus = None,
        start_date: datetime = None,
        end_date: datetime = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[SearchHistory]:
        query = self.db.query(SearchHistory).options(
            joinedload(SearchHistory.user),
            joinedload(SearchHistory.search_config)
        ).filter(SearchHistory.user_id == user_id)
        
        if status:
            query = query.filter(SearchHistory.status == status)
        
        if start_date:
            query = query.filter(SearchHistory.started_at >= start_date)
        
        if end_date:
            query = query.filter(SearchHistory.started_at <= end_date)
        
        return query.order_by(desc(SearchHistory.started_at)).offset(skip).limit(limit).all()


    def get_with_details(self, search_id: UUID) -> Optional[SearchHistory]:
        """Get search history with user and config details"""
        return self.db.query(SearchHistory).options(
            joinedload(SearchHistory.user),
            joinedload(SearchHistory.search_config)
        ).filter(SearchHistory.id == search_id).first()


    def update_search_status(
        self,
        search_id: UUID,
        status: SearchStatus,
        total_results: int = None,
        valid_results: int = None,
        duplicate_results: int = None,
        execution_time_ms: int = None,
        pages_scraped: int = None,
        websites_searched: List[str] = None,
        error_message: str = None,
        results_file_url: str = None,
        results_summary: dict = None
    ) -> Optional[SearchHistory]:
        search = self.get(search_id)
        if not search:
            return None
        
        update_data = {"status": status}
        
        if total_results is not None:
            update_data["total_results"] = total_results
        
        if valid_results is not None:
            update_data["valid_results"] = valid_results
        
        if duplicate_results is not None:
            update_data["duplicate_results"] = duplicate_results
        
        if execution_time_ms is not None:
            update_data["execution_time_ms"] = execution_time_ms
        
        if pages_scraped is not None:
            update_data["pages_scraped"] = pages_scraped
        
        if websites_searched is not None:
            update_data["websites_searched"] = websites_searched
        
        if error_message is not None:
            update_data["error_message"] = error_message
        
        if results_file_url is not None:
            update_data["results_file_url"] = results_file_url
        
        if results_summary is not None:
            update_data["results_summary"] = results_summary
        
        if status in [SearchStatus.COMPLETED, SearchStatus.FAILED, SearchStatus.CANCELLED]:
            update_data["completed_at"] = datetime.utcnow()
        
        return self.update(search, update_data)


    def get_search_statistics(self, user_id: UUID = None, days_back: int = 30) -> Dict[str, Any]:
        query = self.db.query(SearchHistory)
        
        if user_id:
            query = query.filter(SearchHistory.user_id == user_id)
        
        if days_back:
            since_date = datetime.utcnow() - timedelta(days=days_back)
            query = query.filter(SearchHistory.started_at >= since_date)

        total_searches = query.count()
        successful_searches = query.filter(SearchHistory.status == SearchStatus.COMPLETED).count()
        failed_searches = query.filter(SearchHistory.status == SearchStatus.FAILED).count()

        results_stats = query.filter(SearchHistory.status == SearchStatus.COMPLETED).with_entities(
            func.sum(SearchHistory.total_results).label('total_results'),
            func.avg(SearchHistory.execution_time_ms).label('avg_execution_time'),
            func.sum(SearchHistory.pages_scraped).label('total_pages_scraped')
        ).first()
        
        return {
            "total_searches": total_searches,
            "successful_searches": successful_searches,
            "failed_searches": failed_searches,
            "success_rate": (successful_searches / total_searches * 100) if total_searches > 0 else 0,
            "total_results": results_stats.total_results or 0,
            "avg_execution_time_ms": round(results_stats.avg_execution_time or 0, 2),
            "total_pages_scraped": results_stats.total_pages_scraped or 0,
            "avg_results_per_search": round((results_stats.total_results or 0) / successful_searches, 2) if successful_searches > 0 else 0
        }


    def get_performance_trends(
        self,
        user_id: UUID = None,
        days_back: int = 30
    ) -> List[Dict[str, Any]]:
        since_date = datetime.utcnow() - timedelta(days=days_back)
        
        query = self.db.query(
            func.date(SearchHistory.started_at).label('search_date'),
            func.count(SearchHistory.id).label('total_searches'),
            func.count(SearchHistory.id).filter(SearchHistory.status == SearchStatus.COMPLETED).label('successful_searches'),
            func.sum(SearchHistory.total_results).label('total_results'),
            func.avg(SearchHistory.execution_time_ms).label('avg_execution_time')
        ).filter(SearchHistory.started_at >= since_date)
        
        if user_id:
            query = query.filter(SearchHistory.user_id == user_id)
        
        results = query.group_by(func.date(SearchHistory.started_at)).order_by(desc('search_date')).all()
        
        return [
            {
                "date": result.search_date.isoformat(),
                "total_searches": result.total_searches,
                "successful_searches": result.successful_searches,
                "total_results": result.total_results or 0,
                "avg_execution_time": round(result.avg_execution_time or 0, 2)
            }
            for result in results
        ]


    def get_recent_searches(self, limit: int = 50) -> List[SearchHistory]:
        return self.db.query(SearchHistory).options(
            joinedload(SearchHistory.user),
            joinedload(SearchHistory.search_config)
        ).order_by(desc(SearchHistory.started_at)).limit(limit).all()


    def cancel_search(self, search_id: UUID) -> Optional[SearchHistory]:
        search = self.get(search_id)
        if search and search.status in [SearchStatus.PENDING, SearchStatus.IN_PROGRESS]:
            return self.update_search_status(search_id, SearchStatus.CANCELLED)
        return search


    def cleanup_old_searches(self, days_to_keep: int = 90) -> int:
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        deleted_count = self.db.query(SearchHistory).filter(
            and_(
                SearchHistory.started_at < cutoff_date,
                SearchHistory.status.in_([SearchStatus.COMPLETED, SearchStatus.FAILED, SearchStatus.CANCELLED])
            )
        ).delete()
        
        self.db.commit()
        return deleted_count


    def get_website_performance(self, days_back: int = 30) -> List[Dict[str, Any]]:
        since_date = datetime.utcnow() - timedelta(days=days_back)

        searches = self.db.query(SearchHistory).filter(
            and_(
                SearchHistory.started_at >= since_date,
                SearchHistory.status == SearchStatus.COMPLETED
            )
        ).all()
        
        website_stats = {}
        for search in searches:
            for website in search.websites_searched or []:
                if website not in website_stats:
                    website_stats[website] = {
                        "website": website,
                        "searches": 0,
                        "total_results": 0,
                        "total_execution_time": 0
                    }
                
                website_stats[website]["searches"] += 1
                website_stats[website]["total_results"] += search.total_results or 0
                website_stats[website]["total_execution_time"] += search.execution_time_ms or 0

        result = []
        for stats in website_stats.values():
            if stats["searches"] > 0:
                result.append({
                    "website": stats["website"],
                    "searches": stats["searches"],
                    "success_rate": 100.0, 
                    "avg_results": round(stats["total_results"] / stats["searches"], 2),
                    "avg_response_time": round(stats["total_execution_time"] / stats["searches"], 2)
                })
        
        return sorted(result, key=lambda x: x["searches"], reverse=True)


    def get_most_used_config(self, user_id: UUID = None) -> Optional[str]:
        query = self.db.query(
            SearchHistory.search_config_id,
            func.count(SearchHistory.id).label('usage_count')
        ).filter(SearchHistory.search_config_id.isnot(None))
        
        if user_id:
            query = query.filter(SearchHistory.user_id == user_id)
        
        result = query.group_by(SearchHistory.search_config_id).order_by(desc('usage_count')).first()
        
        if result and result.search_config_id:
            config = self.db.query(SearchConfiguration).filter(
                SearchConfiguration.id == result.search_config_id
            ).first()
            return config.name if config else None
        
        return None