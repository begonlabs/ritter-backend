from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_, func, text
from datetime import datetime, timedelta
from uuid import UUID

from app.api.repositories.base import BaseRepository
from app.api.models.lead import Lead


class LeadRepository(BaseRepository[Lead, dict, dict]):
    def __init__(self, db: Session):
        super().__init__(db, Lead)


    def search_leads(
        self,
        search_term: str = None,
        min_quality_score: int = 1,
        verified_email: bool = None,
        verified_phone: bool = None,
        verified_website: bool = None,
        categories: List[str] = None,
        states: List[str] = None,
        countries: List[str] = None,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> List[Lead]:
        query = self.db.query(Lead)
        query = query.filter(Lead.data_quality_score >= min_quality_score)

        if search_term:
            query = query.filter(
                or_(
                    Lead.company_name.ilike(f"%{search_term}%"),
                    Lead.activity.ilike(f"%{search_term}%"),
                    Lead.description.ilike(f"%{search_term}%")
                )
            )
        
        if verified_email is not None:
            query = query.filter(Lead.verified_email == verified_email)
        
        if verified_phone is not None:
            query = query.filter(Lead.verified_phone == verified_phone)
        
        if verified_website is not None:
            query = query.filter(Lead.verified_website == verified_website)
        
        if categories:
            query = query.filter(Lead.category.in_(categories))
        
        if states:
            query = query.filter(Lead.state.in_(states))
        
        if countries:
            query = query.filter(Lead.country.in_(countries))

        if hasattr(Lead, sort_by):
            order_column = getattr(Lead, sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(desc(order_column))
            else:
                query = query.order_by(order_column)
        else:
            query = query.order_by(desc(Lead.created_at))
        
        return query.offset(skip).limit(limit).all()


    def count_leads_with_filters(
        self,
        search_term: str = None,
        min_quality_score: int = 1,
        verified_email: bool = None,
        verified_phone: bool = None,
        verified_website: bool = None,
        categories: List[str] = None,
        states: List[str] = None,
        countries: List[str] = None
    ) -> int:
        query = self.db.query(Lead)
        
        query = query.filter(Lead.data_quality_score >= min_quality_score)
        
        if search_term:
            query = query.filter(
                or_(
                    Lead.company_name.ilike(f"%{search_term}%"),
                    Lead.activity.ilike(f"%{search_term}%"),
                    Lead.description.ilike(f"%{search_term}%")
                )
            )
        
        if verified_email is not None:
            query = query.filter(Lead.verified_email == verified_email)
        
        if verified_phone is not None:
            query = query.filter(Lead.verified_phone == verified_phone)
        
        if verified_website is not None:
            query = query.filter(Lead.verified_website == verified_website)
        
        if categories:
            query = query.filter(Lead.category.in_(categories))
        
        if states:
            query = query.filter(Lead.state.in_(states))
        
        if countries:
            query = query.filter(Lead.country.in_(countries))
        
        return query.count()


    def get_lead_statistics(self, period_days: int = None) -> Dict[str, Any]:
        query = self.db.query(Lead)
        
        if period_days:
            since_date = datetime.utcnow() - timedelta(days=period_days)
            query = query.filter(Lead.created_at >= since_date)

        total_leads = query.count()
        verified_emails = query.filter(Lead.verified_email == True).count()
        verified_phones = query.filter(Lead.verified_phone == True).count()
        verified_websites = query.filter(Lead.verified_website == True).count()

        quality_dist = self.db.query(
            Lead.data_quality_score,
            func.count(Lead.id).label('count')
        ).group_by(Lead.data_quality_score).all()
        
        quality_distribution = {f"score_{score}": count for score, count in quality_dist}

        verification_rates = {
            "email_rate": (verified_emails / total_leads * 100) if total_leads > 0 else 0,
            "phone_rate": (verified_phones / total_leads * 100) if total_leads > 0 else 0,
            "website_rate": (verified_websites / total_leads * 100) if total_leads > 0 else 0
        }
        
        return {
            "total_leads": total_leads,
            "verified_emails": verified_emails,
            "verified_phones": verified_phones,
            "verified_websites": verified_websites,
            "quality_distribution": quality_distribution,
            "verification_rates": verification_rates
        }

    def get_top_categories(self, limit: int = 10) -> List[Dict[str, Any]]:
        results = self.db.query(
            Lead.category,
            func.count(Lead.id).label('count')
        ).filter(Lead.category.isnot(None)).group_by(Lead.category).order_by(desc('count')).limit(limit).all()
        
        total_leads = self.db.query(Lead).filter(Lead.category.isnot(None)).count()
        
        return [
            {
                "category": category,
                "count": count,
                "percentage": round((count / total_leads * 100), 2) if total_leads > 0 else 0
            }
            for category, count in results
        ]


    def get_top_states(self, limit: int = 10) -> List[Dict[str, Any]]:
        results = self.db.query(
            Lead.state,
            func.count(Lead.id).label('count')
        ).filter(Lead.state.isnot(None)).group_by(Lead.state).order_by(desc('count')).limit(limit).all()
        
        total_leads = self.db.query(Lead).filter(Lead.state.isnot(None)).count()
        
        return [
            {
                "state": state,
                "count": count,
                "percentage": round((count / total_leads * 100), 2) if total_leads > 0 else 0
            }
            for state, count in results
        ]


    def get_daily_trends(self, days_back: int = 30) -> List[Dict[str, Any]]:
        since_date = datetime.utcnow() - timedelta(days=days_back)
        
        results = self.db.query(
            func.date(Lead.created_at).label('date'),
            func.count(Lead.id).label('count'),
            func.avg(Lead.data_quality_score).label('quality_avg')
        ).filter(Lead.created_at >= since_date).group_by(func.date(Lead.created_at)).order_by(desc('date')).all()
        
        return [
            {
                "date": result.date.isoformat(),
                "count": result.count,
                "quality_avg": round(float(result.quality_avg), 2) if result.quality_avg else 0
            }
            for result in results
        ]


    def bulk_update_leads(self, lead_ids: List[UUID], updates: Dict[str, Any]) -> int:
        updates["updated_at"] = datetime.utcnow()
        
        updated_count = self.db.query(Lead).filter(Lead.id.in_(lead_ids)).update(
            updates, synchronize_session=False
        )
        
        self.db.commit()
        return updated_count


    def bulk_delete_leads(self, lead_ids: List[UUID]) -> int:
        deleted_count = self.db.query(Lead).filter(Lead.id.in_(lead_ids)).delete(
            synchronize_session=False
        )
        
        self.db.commit()
        return deleted_count


    def full_text_search(
        self,
        query: str,
        fields: List[str] = None,
        exact_match: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        if not fields:
            fields = ["company_name", "activity", "description"]

        search_conditions = []
        for field in fields:
            if hasattr(Lead, field):
                if exact_match:
                    search_conditions.append(getattr(Lead, field).ilike(f"%{query}%"))
                else:
                    search_conditions.append(getattr(Lead, field).ilike(f"%{query}%"))
        
        if not search_conditions:
            return []

        results = self.db.query(Lead).filter(or_(*search_conditions)).offset(skip).limit(limit).all()

        search_results = []
        for lead in results:
            relevance_score = 0.0
            matching_fields = []

            for field in fields:
                if hasattr(lead, field):
                    field_value = getattr(lead, field) or ""
                    if query.lower() in field_value.lower():
                        relevance_score += 1.0 / len(fields)
                        matching_fields.append(field)
            
            search_results.append({
                "id": lead.id,
                "company_name": lead.company_name,
                "activity": lead.activity,
                "description": lead.description,
                "category": lead.category,
                "data_quality_score": lead.data_quality_score,
                "relevance_score": relevance_score,
                "matching_fields": matching_fields,
                "created_at": lead.created_at
            })

        search_results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return search_results


    def get_filter_options(self) -> Dict[str, List[Dict[str, Any]]]:
        categories = self.db.query(
            Lead.category,
            func.count(Lead.id).label('count')
        ).filter(Lead.category.isnot(None)).group_by(Lead.category).order_by(Lead.category).all()

        states = self.db.query(
            Lead.state,
            func.count(Lead.id).label('count')
        ).filter(Lead.state.isnot(None)).group_by(Lead.state).order_by(Lead.state).all()

        countries = self.db.query(
            Lead.country,
            func.count(Lead.id).label('count')
        ).filter(Lead.country.isnot(None)).group_by(Lead.country).order_by(Lead.country).all()

        quality_scores = self.db.query(
            Lead.data_quality_score,
            func.count(Lead.id).label('count')
        ).group_by(Lead.data_quality_score).order_by(Lead.data_quality_score).all()
        
        total_leads = self.db.query(Lead).count()
        
        return {
            "categories": [
                {"value": cat, "label": cat, "count": count}
                for cat, count in categories
            ],
            "states": [
                {"value": state, "label": state, "count": count}
                for state, count in states
            ],
            "countries": [
                {"value": country, "label": country, "count": count}
                for country, count in countries
            ],
            "quality_scores": [
                {
                    "score": score,
                    "count": count,
                    "percentage": round((count / total_leads * 100), 2) if total_leads > 0 else 0
                }
                for score, count in quality_scores
            ]
        }


    def find_duplicates(
        self,
        strategy: str = "email",
        threshold: float = 0.8
    ) -> List[Dict[str, Any]]:
        duplicates = []
        
        if strategy == "email":
            email_duplicates = self.db.query(
                Lead.email,
                func.array_agg(Lead.id).label('lead_ids'),
                func.count(Lead.id).label('count')
            ).filter(
                and_(Lead.email.isnot(None), Lead.email != "")
            ).group_by(Lead.email).having(func.count(Lead.id) > 1).all()
            
            for email, lead_ids, count in email_duplicates:
                duplicates.append({
                    "match_type": "email",
                    "match_value": email,
                    "lead_ids": lead_ids,
                    "count": count
                })
        

        elif strategy == "company_name":
            company_duplicates = self.db.query(
                Lead.company_name,
                func.array_agg(Lead.id).label('lead_ids'),
                func.count(Lead.id).label('count')
            ).group_by(Lead.company_name).having(func.count(Lead.id) > 1).all()
            
            for company_name, lead_ids, count in company_duplicates:
                duplicates.append({
                    "match_type": "company_name",
                    "match_value": company_name,
                    "lead_ids": lead_ids,
                    "count": count
                })
        

        elif strategy == "phone":
            phone_duplicates = self.db.query(
                Lead.phone,
                func.array_agg(Lead.id).label('lead_ids'),
                func.count(Lead.id).label('count')
            ).filter(
                and_(Lead.phone.isnot(None), Lead.phone != "")
            ).group_by(Lead.phone).having(func.count(Lead.id) > 1).all()
            
            for phone, lead_ids, count in phone_duplicates:
                duplicates.append({
                    "match_type": "phone",
                    "match_value": phone,
                    "lead_ids": lead_ids,
                    "count": count
                })
        
        return duplicates


    def get_quality_analysis(
        self,
        category: str = None,
        state: str = None
    ) -> Dict[str, Any]:
        query = self.db.query(Lead)
        
        if category:
            query = query.filter(Lead.category == category)
        
        if state:
            query = query.filter(Lead.state == state)
        
        leads = query.all()
        
        if not leads:
            return {"overall_quality": 0, "quality_factors": {}, "recommendations": []}
        
        total_leads = len(leads)

        email_verified_count = sum(1 for lead in leads if lead.verified_email)
        phone_verified_count = sum(1 for lead in leads if lead.verified_phone)
        website_verified_count = sum(1 for lead in leads if lead.verified_website)
        
        quality_factors = {
            "email_verification_impact": round(email_verified_count / total_leads * 100, 2),
            "phone_verification_impact": round(phone_verified_count / total_leads * 100, 2),
            "website_verification_impact": round(website_verified_count / total_leads * 100, 2),
            "completeness_score": round(sum(lead.data_quality_score for lead in leads) / total_leads, 2)
        }