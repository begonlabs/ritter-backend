from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from uuid import UUID

from app.api.repositories.base import BaseRepository
from app.api.models.system_settings import SystemSettings


class SystemSettingsRepository(BaseRepository[SystemSettings, dict, dict]):
    def __init__(self, db: Session):
        super().__init__(db, SystemSettings)

    def get_by_category_key(self, category: str, key: str) -> Optional[SystemSettings]:
        """Get setting by category and key"""
        return self.db.query(SystemSettings).filter(
            and_(
                SystemSettings.category == category,
                SystemSettings.key == key
            )
        ).first()

    def get_by_category(self, category: str) -> List[SystemSettings]:
        """Get all settings for a category"""
        return self.db.query(SystemSettings).filter(
            SystemSettings.category == category
        ).order_by(SystemSettings.key).all()

    def get_public_settings(self) -> List[SystemSettings]:
        """Get all public settings"""
        return self.db.query(SystemSettings).filter(
            SystemSettings.is_public == True
        ).order_by(SystemSettings.category, SystemSettings.key).all()

    def get_all_grouped_by_category(
        self,
        include_private: bool = True,
        categories: List[str] = None
    ) -> Dict[str, List[SystemSettings]]:
        """Get all settings grouped by category"""
        query = self.db.query(SystemSettings)
        
        if not include_private:
            query = query.filter(SystemSettings.is_public == True)
        
        if categories:
            query = query.filter(SystemSettings.category.in_(categories))
        
        settings = query.order_by(SystemSettings.category, SystemSettings.key).all()
        
        grouped = {}
        for setting in settings:
            if setting.category not in grouped:
                grouped[setting.category] = []
            grouped[setting.category].append(setting)
        
        return grouped

    def update_setting_value(
        self,
        setting_id: UUID,
        value: str,
        updated_by: UUID,
        description: str = None
    ) -> Optional[SystemSettings]:
        """Update setting value"""
        setting = self.get(setting_id)
        if setting:
            update_data = {
                "value": value,
                "updated_by": updated_by,
                "updated_at": datetime.utcnow()
            }
            if description is not None:
                update_data["description"] = description
            
            return self.update(setting, update_data)
        return None

    def create_or_update_setting(
        self,
        category: str,
        key: str,
        value: str,
        value_type: str = "string",
        description: str = None,
        is_public: bool = False,
        is_encrypted: bool = False,
        validation_rules: dict = None,
        default_value: str = None,
        updated_by: UUID = None
    ) -> SystemSettings:
        """Create new setting or update existing one"""
        existing = self.get_by_category_key(category, key)
        
        if existing:
            update_data = {
                "value": value,
                "updated_by": updated_by,
                "updated_at": datetime.utcnow()
            }
            if description is not None:
                update_data["description"] = description
            
            return self.update(existing, update_data)
        else:
            setting_data = {
                "category": category,
                "key": key,
                "value": value,
                "value_type": value_type,
                "description": description,
                "is_public": is_public,
                "is_encrypted": is_encrypted,
                "validation_rules": validation_rules or {},
                "default_value": default_value,
                "updated_by": updated_by,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            return self.create(setting_data)

    def get_setting_value(self, category: str, key: str, default: str = None) -> Optional[str]:
        """Get setting value by category and key"""
        setting = self.get_by_category_key(category, key)
        if setting and setting.value:
            return setting.value
        return default

    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        return [category[0] for category in self.db.query(SystemSettings.category).distinct().all()]

    def initialize_default_settings(self):
        """Initialize default system settings"""
        default_settings = [
            # Email settings
            ("email", "from_email", "noreply@ritterfinder.com", "string", "Default from email address", True),
            ("email", "from_name", "RitterFinder", "string", "Default from name", True),
            
            # Scraping settings
            ("scraping", "max_concurrent_requests", "10", "number", "Maximum concurrent scraping requests", False),
            ("scraping", "request_delay_ms", "1000", "number", "Delay between requests in milliseconds", False),
            ("scraping", "max_results_per_search", "1000", "number", "Maximum results per search session", True),
            
            # System settings
            ("system", "maintenance_mode", "false", "boolean", "Enable maintenance mode", False),
            ("system", "registration_enabled", "false", "boolean", "Allow new user registration", True),
            ("system", "max_users", "100", "number", "Maximum number of users", False),
            
            # Security settings
            ("security", "session_timeout_hours", "24", "number", "Session timeout in hours", False),
            ("security", "max_login_attempts", "5", "number", "Maximum login attempts before lockout", False),
            ("security", "lockout_duration_minutes", "30", "number", "Account lockout duration in minutes", False),
        ]
        
        for category, key, value, value_type, description, is_public in default_settings:
            if not self.get_by_category_key(category, key):
                self.create_or_update_setting(
                    category=category,
                    key=key,
                    value=value,
                    value_type=value_type,
                    description=description,
                    is_public=is_public
                )