from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from uuid import UUID

from app.api.models.system_settings import SystemSettings
from app.api.repositories.system_settings_repository import SystemSettingsRepository
from app.api.schemas.system_settings import CreateSystemSettingRequest, UpdateSystemSettingRequest
from fastapi import HTTPException


class SystemSettingsService:
    def __init__(self, db: Session):
        self.db = db
        self.settings_repo = SystemSettingsRepository(db)

    async def get_all_settings(
        self,
        include_private: bool = True,
        category: str = None,
        is_public: bool = None
    ) -> Dict[str, List[SystemSettings]]:
        """Get all settings grouped by category"""
        categories = [category] if category else None
        
        if is_public is not None and not is_public:
            # If specifically requesting private settings, include_private should be True
            include_private = True
        elif is_public is not None and is_public:
            # If specifically requesting public settings, include_private should be False
            include_private = False
        
        grouped_settings = self.settings_repo.get_all_grouped_by_category(
            include_private=include_private,
            categories=categories
        )
        
        # Filter by is_public if specified
        if is_public is not None:
            filtered_settings = {}
            for cat, settings in grouped_settings.items():
                filtered_list = [s for s in settings if s.is_public == is_public]
                if filtered_list:
                    filtered_settings[cat] = filtered_list
            return filtered_settings
        
        return grouped_settings

    async def get_setting_by_id(self, setting_id: UUID) -> Optional[SystemSettings]:
        """Get setting by ID"""
        setting = self.settings_repo.get(setting_id)
        if not setting:
            raise HTTPException(status_code=404, detail="Setting not found")
        return setting

    async def get_setting_by_category_key(
        self,
        category: str,
        key: str
    ) -> Optional[SystemSettings]:
        """Get setting by category and key"""
        return self.settings_repo.get_by_category_key(category, key)

    async def get_setting_value(
        self,
        category: str,
        key: str,
        default: str = None
    ) -> Optional[str]:
        """Get setting value by category and key"""
        return self.settings_repo.get_setting_value(category, key, default)

    async def create_setting(
        self,
        setting_data: CreateSystemSettingRequest,
        updated_by: UUID
    ) -> SystemSettings:
        """Create new system setting"""
        existing = self.settings_repo.get_by_category_key(
            setting_data.category,
            setting_data.key
        )
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Setting '{setting_data.key}' already exists in category '{setting_data.category}'"
            )
        
        return self.settings_repo.create_or_update_setting(
            category=setting_data.category,
            key=setting_data.key,
            value=setting_data.value,
            value_type=setting_data.value_type,
            description=setting_data.description,
            is_public=setting_data.is_public,
            is_encrypted=setting_data.is_encrypted,
            validation_rules=setting_data.validation_rules,
            default_value=setting_data.default_value,
            updated_by=updated_by
        )

    async def update_setting(
        self,
        setting_id: UUID,
        update_data: UpdateSystemSettingRequest,
        updated_by: UUID
    ) -> SystemSettings:
        """Update system setting"""
        setting = self.settings_repo.get(setting_id)
        if not setting:
            raise HTTPException(status_code=404, detail="Setting not found")
        
        updated_setting = self.settings_repo.update_setting_value(
            setting_id=setting_id,
            value=update_data.value,
            updated_by=updated_by,
            description=update_data.description
        )
        
        if not updated_setting:
            raise HTTPException(status_code=500, detail="Failed to update setting")
        
        return updated_setting

    async def delete_setting(self, setting_id: UUID) -> bool:
        """Delete system setting"""
        setting = self.settings_repo.get(setting_id)
        if not setting:
            raise HTTPException(status_code=404, detail="Setting not found")
        
        deleted_setting = self.settings_repo.delete(setting_id)
        return deleted_setting is not None

    async def get_categories(self) -> List[str]:
        """Get all setting categories"""
        return self.settings_repo.get_categories()

    async def get_public_settings(self) -> List[SystemSettings]:
        """Get all public settings"""
        return self.settings_repo.get_public_settings()

    async def initialize_default_settings(self):
        """Initialize default system settings"""
        self.settings_repo.initialize_default_settings()

    async def validate_setting_value(
        self,
        setting: SystemSettings,
        value: str
    ) -> bool:
        """Validate setting value against rules"""
        if not setting.validation_rules:
            return True
        
        rules = setting.validation_rules
        
        # Basic validation based on value_type
        if setting.value_type == "number":
            try:
                num_value = float(value)
                if "min" in rules and num_value < rules["min"]:
                    return False
                if "max" in rules and num_value > rules["max"]:
                    return False
            except ValueError:
                return False
        
        elif setting.value_type == "boolean":
            if value.lower() not in ["true", "false", "1", "0"]:
                return False
        
        elif setting.value_type == "email":
            import re
            email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
            if not re.match(email_pattern, value):
                return False
        
        # Custom validation rules
        if "allowed_values" in rules:
            if value not in rules["allowed_values"]:
                return False
        
        if "regex" in rules:
            import re
            if not re.match(rules["regex"], value):
                return False
        
        return True