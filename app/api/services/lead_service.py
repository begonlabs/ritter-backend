from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
import uuid

from app.api.models.lead import Lead
from app.api.repositories.lead_repository import LeadRepository
from app.api.schemas.lead import (
    UpdateLeadRequest, BulkUpdateLeadsRequest, BulkDeleteLeadsRequest,
    ValidateLeadsRequest, DeduplicateLeadsRequest, LeadImportRequest
)
from fastapi import HTTPException, UploadFile
try:
    import polars as pl
    import io
except ImportError:
    pl = None
    io = None


class LeadService:
    def __init__(self, db: Session):
        self.db = db
        self.lead_repo = LeadRepository(db)

    # Lead Management Methods
    async def get_leads(
        self,
        page: int = 1,
        limit: int = 25,
        search: str = None,
        min_quality_score: int = 1,
        verified_email: bool = None,
        verified_phone: bool = None,
        verified_website: bool = None,
        categories: List[str] = None,
        states: List[str] = None,
        countries: List[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Dict[str, Any]:
        """Get leads with advanced filtering"""
        skip = (page - 1) * limit
        
        leads = self.lead_repo.search_leads(
            search_term=search,
            min_quality_score=min_quality_score,
            verified_email=verified_email,
            verified_phone=verified_phone,
            verified_website=verified_website,
            categories=categories,
            states=states,
            countries=countries,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        total = self.lead_repo.count_leads_with_filters(
            search_term=search,
            min_quality_score=min_quality_score,
            verified_email=verified_email,
            verified_phone=verified_phone,
            verified_website=verified_website,
            categories=categories,
            states=states,
            countries=countries
        )
        
        # Get summary data
        high_quality_count = self.lead_repo.get_high_quality_leads_count()
        contactable_count = self.lead_repo.get_contactable_leads_count()
        
        return {
            "leads": leads,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit if limit > 0 else 1
            },
            "filters_applied": {
                "search": search,
                "min_quality_score": min_quality_score,
                "verified_email": verified_email,
                "verified_phone": verified_phone,
                "verified_website": verified_website,
                "categories": categories,
                "states": states
            },
            "summary": {
                "total_leads": total,
                "high_quality_leads": high_quality_count,
                "contactable_leads": contactable_count
            }
        }

    async def get_lead_by_id(self, lead_id: UUID) -> Dict[str, Any]:
        """Get specific lead with details"""
        lead = self.lead_repo.get(lead_id)
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Get contact history (placeholder - would need campaign integration)
        contact_history = []
        
        # Get related leads (simplified similarity based on category)
        related_leads = []
        if lead.category:
            similar_leads = self.lead_repo.get_multi_by_field("category", lead.category)
            related_leads = [
                {
                    "id": similar_lead.id,
                    "company_name": similar_lead.company_name,
                    "similarity_score": 0.8  # Placeholder
                }
                for similar_lead in similar_leads[:5]
                if similar_lead.id != lead.id
            ]
        
        return {
            "lead": {
                **lead.__dict__,
                "contact_history": contact_history,
                "related_leads": related_leads
            }
        }

    async def update_lead(self, lead_id: UUID, update_data: UpdateLeadRequest) -> Lead:
        """Update lead information"""
        lead = self.lead_repo.get(lead_id)
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        update_dict = update_data.dict(exclude_unset=True)
        if update_dict:
            return self.lead_repo.update(lead, update_dict)
        
        return lead

    async def delete_lead(self, lead_id: UUID) -> bool:
        """Delete lead"""
        lead = self.lead_repo.get(lead_id)
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        deleted = self.lead_repo.delete(lead_id)
        return deleted is not None

    async def bulk_update_leads(self, request: BulkUpdateLeadsRequest) -> Dict[str, Any]:
        """Bulk update multiple leads"""
        if not request.lead_ids:
            raise HTTPException(status_code=400, detail="No lead IDs provided")
        
        updated_count = self.lead_repo.bulk_update_leads(
            lead_ids=request.lead_ids,
            updates=request.updates
        )
        
        return {
            "updated_count": updated_count,
            "message": f"Successfully updated {updated_count} leads"
        }

    async def bulk_delete_leads(self, request: BulkDeleteLeadsRequest) -> Dict[str, Any]:
        """Bulk delete multiple leads"""
        if not request.lead_ids:
            raise HTTPException(status_code=400, detail="No lead IDs provided")
        
        deleted_count = self.lead_repo.bulk_delete_leads(request.lead_ids)
        
        return {
            "deleted_count": deleted_count,
            "message": f"Successfully deleted {deleted_count} leads"
        }

    # Statistics & Analytics Methods
    async def get_lead_statistics(self, period: str = "all") -> Dict[str, Any]:
        """Get lead statistics and distribution"""
        period_days = None
        if period == "30d":
            period_days = 30
        elif period == "7d":
            period_days = 7
        elif period == "1d":
            period_days = 1
        
        statistics = self.lead_repo.get_lead_statistics(period_days=period_days)
        top_categories = self.lead_repo.get_top_categories(limit=10)
        top_states = self.lead_repo.get_top_states(limit=10)
        daily_trends = self.lead_repo.get_daily_trends(days_back=30)
        
        return {
            "statistics": statistics,
            "top_categories": top_categories,
            "top_states": top_states,
            "trends": {
                "daily_leads": daily_trends
            }
        }

    async def get_quality_analysis(
        self,
        category: str = None,
        state: str = None
    ) -> Dict[str, Any]:
        """Get detailed lead quality analysis"""
        quality_analysis = self.lead_repo.get_quality_analysis(
            category=category,
            state=state
        )
        
        # Get quality by source (placeholder - would need source tracking)
        quality_by_source = [
            {"source": "Manual Import", "avg_quality": 3.2, "lead_count": 150},
            {"source": "Web Scraping", "avg_quality": 2.8, "lead_count": 450},
            {"source": "API Integration", "avg_quality": 4.1, "lead_count": 75}
        ]
        
        return {
            "quality_analysis": quality_analysis,
            "quality_by_source": quality_by_source
        }

    # Search & Filtering Methods
    async def search_leads(
        self,
        query: str,
        fields: List[str] = None,
        exact_match: bool = False,
        page: int = 1,
        limit: int = 25
    ) -> Dict[str, Any]:
        """Advanced lead search with full-text search"""
        if not query.strip():
            raise HTTPException(status_code=400, detail="Search query cannot be empty")
        
        skip = (page - 1) * limit
        
        start_time = datetime.utcnow()
        search_results = self.lead_repo.full_text_search(
            query=query,
            fields=fields,
            exact_match=exact_match,
            skip=skip,
            limit=limit
        )
        end_time = datetime.utcnow()
        
        execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        # Count total matches (simplified)
        total_matches = len(search_results)  # This should be improved with proper counting
        
        return {
            "search_results": search_results,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_matches,
                "total_pages": (total_matches + limit - 1) // limit if limit > 0 else 1
            },
            "search_info": {
                "query": query,
                "execution_time_ms": execution_time_ms,
                "total_matches": total_matches
            }
        }

    async def get_filter_options(self) -> Dict[str, Any]:
        """Get available filter options for leads"""
        filter_options = self.lead_repo.get_filter_options()
        
        # Get summary information
        total_leads = self.lead_repo.count()
        oldest_lead = self.lead_repo.get_multi(limit=1, order_by="created_at", order_desc=False)
        newest_lead = self.lead_repo.get_multi(limit=1, order_by="created_at", order_desc=True)
        
        return {
            "filter_options": filter_options,
            "summary": {
                "total_categories": len(filter_options.get("categories", [])),
                "total_states": len(filter_options.get("states", [])),
                "total_countries": len(filter_options.get("countries", [])),
                "date_range": {
                    "oldest_lead": oldest_lead[0].created_at.date() if oldest_lead else None,
                    "newest_lead": newest_lead[0].created_at.date() if newest_lead else None
                }
            }
        }

    # Export & Import Methods
    async def export_leads(
        self,
        format: str = "csv",
        filters: Dict[str, Any] = None,
        fields: List[str] = None,
        include_contact_history: bool = False
    ) -> Dict[str, Any]:
        """Export leads to various formats"""
        # Apply filters to get leads
        search_params = filters or {}
        leads = self.lead_repo.search_leads(**search_params)
        
        if not leads:
            raise HTTPException(status_code=404, detail="No leads found with specified filters")
        
        # Prepare data for export
        export_data = []
        for lead in leads:
            lead_data = {
                "id": str(lead.id),
                "company_name": lead.company_name,
                "email": lead.email,
                "verified_email": lead.verified_email,
                "phone": lead.phone,
                "verified_phone": lead.verified_phone,
                "company_website": lead.company_website,
                "verified_website": lead.verified_website,
                "address": lead.address,
                "state": lead.state,
                "country": lead.country,
                "activity": lead.activity,
                "description": lead.description,
                "category": lead.category,
                "data_quality_score": lead.data_quality_score,
                "created_at": lead.created_at.isoformat(),
                "updated_at": lead.updated_at.isoformat(),
                "last_contacted_at": lead.last_contacted_at.isoformat() if lead.last_contacted_at else None
            }
            
            # Filter fields if specified
            if fields:
                lead_data = {k: v for k, v in lead_data.items() if k in fields}
            
            export_data.append(lead_data)
        
        # Generate file name
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        file_name = f"leads_export_{timestamp}.{format}"
        
        # For JSON format, return the data directly
        if format == "json":
            import json
            json_content = json.dumps(export_data, indent=2, ensure_ascii=False)
            file_size = len(json_content.encode('utf-8'))
            
            return {
                "export": {
                    "data": export_data,  # Return actual data for JSON
                    "file_name": file_name,
                    "file_size": file_size,
                    "format": format,
                    "total_records": len(export_data),
                    "expires_at": (datetime.utcnow()).isoformat()
                },
                "filters_applied": filters or {},
                "fields_exported": fields or list(export_data[0].keys()) if export_data else []
            }
        
        # For other formats (CSV, Excel), generate file content
        elif format in ["csv", "xlsx"] and pl is not None:
            try:
                # Create polars DataFrame
                df = pl.DataFrame(export_data)
                
                if format == "csv":
                    # Generate CSV content
                    csv_content = df.write_csv()
                    file_size = len(csv_content.encode('utf-8'))
                    
                    return {
                        "export": {
                            "content": csv_content,  # Return actual CSV content
                            "file_name": file_name,
                            "file_size": file_size,
                            "format": format,
                            "total_records": len(export_data),
                            "expires_at": (datetime.utcnow()).isoformat()
                        },
                        "filters_applied": filters or {},
                        "fields_exported": fields or list(export_data[0].keys()) if export_data else []
                    }
                
                elif format == "xlsx":
                    # For Excel, we'd need to save to a temporary file or use BytesIO
                    # For now, convert to CSV as fallback
                    csv_content = df.write_csv()
                    file_size = len(csv_content.encode('utf-8'))
                    
                    return {
                        "export": {
                            "content": csv_content,
                            "file_name": file_name.replace('.xlsx', '.csv'),
                            "file_size": file_size,
                            "format": "csv",  # Fallback to CSV
                            "total_records": len(export_data),
                            "expires_at": (datetime.utcnow()).isoformat()
                        },
                        "filters_applied": filters or {},
                        "fields_exported": fields or list(export_data[0].keys()) if export_data else []
                    }
                    
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error generating file: {str(e)}")
        
        else:
            # Fallback: return JSON data
            return {
                "export": {
                    "data": export_data,
                    "file_name": file_name.replace(f'.{format}', '.json'),
                    "file_size": len(str(export_data)),
                    "format": "json",
                    "total_records": len(export_data),
                    "expires_at": (datetime.utcnow()).isoformat()
                },
                "filters_applied": filters or {},
                "fields_exported": fields or list(export_data[0].keys()) if export_data else []
            }

    async def import_leads(
        self,
        file: UploadFile,
        mapping: Dict[str, str],
        skip_duplicates: bool = True,
        validate_emails: bool = True,
        validate_phones: bool = False
    ) -> Dict[str, Any]:
        """Import leads from CSV/Excel file"""
        if pl is None:
            raise HTTPException(status_code=500, detail="Polars not available for file processing")
            
        if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")
        
        # Create import job
        import_job_id = uuid.uuid4()
        
        try:
            # Read file content
            content = await file.read()
            
            # Parse file based on extension
            if file.filename.endswith('.csv'):
                # Read CSV with polars
                df = pl.read_csv(io.StringIO(content.decode('utf-8')))
            else:
                # For Excel files, we still need to use a compatible method
                # Polars can read Excel but might need different approach
                try:
                    df = pl.read_excel(io.BytesIO(content))
                except:
                    # Fallback: read with openpyxl and convert to polars
                    import openpyxl
                    workbook = openpyxl.load_workbook(io.BytesIO(content))
                    worksheet = workbook.active
                    
                    # Extract data to list of dictionaries
                    data = []
                    headers = [cell.value for cell in worksheet[1]]
                    
                    for row in worksheet.iter_rows(min_row=2, values_only=True):
                        row_dict = {headers[i]: row[i] for i in range(len(headers)) if i < len(row)}
                        data.append(row_dict)
                    
                    df = pl.DataFrame(data)
            
            # Validate mapping
            missing_columns = [col for col in mapping.values() if col not in df.columns]
            if missing_columns:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing columns in file: {missing_columns}"
                )
            
            # Process leads (this would be done asynchronously in production)
            total_rows = len(df)
            processed_rows = 0
            imported_leads = 0
            skipped_duplicates = 0
            validation_errors = 0
            
            # Convert to list of dictionaries for processing
            rows = df.to_dicts()
            
            for row_data in rows:
                processed_rows += 1
                
                try:
                    # Map columns to lead fields
                    lead_data = {}
                    for lead_field, csv_column in mapping.items():
                        if csv_column in row_data and row_data[csv_column] is not None:
                            # Handle different data types
                            value = row_data[csv_column]
                            if isinstance(value, (int, float)):
                                lead_data[lead_field] = str(value).strip()
                            else:
                                lead_data[lead_field] = str(value).strip()
                    
                    # Validate required fields
                    if not lead_data.get('company_name') or not lead_data.get('activity'):
                        validation_errors += 1
                        continue
                    
                    # Check for duplicates if enabled
                    if skip_duplicates and lead_data.get('email'):
                        existing = self.lead_repo.get_by_field('email', lead_data['email'])
                        if existing:
                            skipped_duplicates += 1
                            continue
                    
                    # Create lead
                    self.lead_repo.create(lead_data)
                    imported_leads += 1
                    
                except Exception as e:
                    validation_errors += 1
                    continue
            
            return {
                "import": {
                    "id": str(import_job_id),
                    "status": "completed",
                    "total_rows": total_rows,
                    "processed_rows": processed_rows,
                    "imported_leads": imported_leads,
                    "skipped_duplicates": skipped_duplicates,
                    "validation_errors": validation_errors,
                    "started_at": datetime.utcnow()
                },
                "message": "Import completed successfully"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

    # Validation & Data Quality Methods
    async def validate_leads(self, request: ValidateLeadsRequest) -> Dict[str, Any]:
        """Validate lead data (emails, phones, websites)"""
        if not request.lead_ids:
            raise HTTPException(status_code=400, detail="No lead IDs provided")
        
        validation_job_id = uuid.uuid4()
        
        # In production, this would be done asynchronously
        total_leads = len(request.lead_ids)
        processed_leads = 0
        results = {
            "valid_emails": 0,
            "invalid_emails": 0,
            "valid_phones": 0,
            "invalid_phones": 0,
            "valid_websites": 0,
            "invalid_websites": 0
        }
        
        for lead_id in request.lead_ids:
            lead = self.lead_repo.get(lead_id)
            if not lead:
                continue
            
            processed_leads += 1
            
            # Simulate validation (in production, use actual validation services)
            update_data = {}
            
            if "email" in request.validation_types and lead.email:
                # Simple email validation
                if "@" in lead.email and "." in lead.email.split("@")[-1]:
                    update_data["verified_email"] = True
                    results["valid_emails"] += 1
                else:
                    update_data["verified_email"] = False
                    results["invalid_emails"] += 1
            
            if "phone" in request.validation_types and lead.phone:
                # Simple phone validation
                clean_phone = ''.join(filter(str.isdigit, lead.phone))
                if len(clean_phone) >= 9:
                    update_data["verified_phone"] = True
                    results["valid_phones"] += 1
                else:
                    update_data["verified_phone"] = False
                    results["invalid_phones"] += 1
            
            if "website" in request.validation_types and lead.company_website:
                # Simple website validation
                if lead.company_website.startswith(("http://", "https://", "www.")):
                    update_data["verified_website"] = True
                    results["valid_websites"] += 1
                else:
                    update_data["verified_website"] = False
                    results["invalid_websites"] += 1
            
            if update_data and request.update_records:
                self.lead_repo.update(lead, update_data)
        
        return {
            "validation": {
                "id": str(validation_job_id),
                "status": "completed",
                "progress": 100.0,
                "total_leads": total_leads,
                "processed_leads": processed_leads,
                "validation_types": request.validation_types,
                "results": results,
                "started_at": datetime.utcnow(),
                "completed_at": datetime.utcnow()
            },
            "message": "Validation completed successfully"
        }

    async def deduplicate_leads(self, request: DeduplicateLeadsRequest) -> Dict[str, Any]:
        """Find and remove duplicate leads"""
        deduplication_job_id = uuid.uuid4()
        
        # Find duplicates based on strategy
        duplicates = self.lead_repo.find_duplicates(
            strategy=request.strategy,
            threshold=0.8
        )
        
        duplicates_found = len(duplicates)
        leads_merged = 0
        leads_removed = 0
        
        if request.auto_merge:
            for duplicate_group in duplicates:
                lead_ids = duplicate_group["lead_ids"]
                if len(lead_ids) > 1:
                    # Keep the highest quality lead if requested
                    if request.keep_highest_quality:
                        leads = [self.lead_repo.get(lid) for lid in lead_ids]
                        leads = [l for l in leads if l is not None]
                        
                        if leads:
                            # Sort by quality score and created date
                            leads.sort(key=lambda x: (x.data_quality_score, x.created_at), reverse=True)
                            keep_lead = leads[0]
                            remove_leads = leads[1:]
                            
                            # Remove duplicates
                            for lead in remove_leads:
                                self.lead_repo.delete(lead.id)
                                leads_removed += 1
                            
                            leads_merged += 1
        
        return {
            "deduplication": {
                "id": str(deduplication_job_id),
                "status": "completed",
                "strategy": request.strategy,
                "duplicates_found": duplicates_found,
                "leads_merged": leads_merged,
                "leads_removed": leads_removed,
                "started_at": datetime.utcnow(),
                "completed_at": datetime.utcnow()
            },
            "message": f"Deduplication completed. Found {duplicates_found} duplicate groups."
        }