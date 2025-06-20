from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from uuid import UUID


ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")



class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType], ABC):
    def __init__(self, db: Session, model: type[ModelType]):
        self.db = db
        self.model = model


    def get(self, id: Any) -> Optional[ModelType]:
        """Get a single record by ID"""
        return self.db.query(self.model).filter(self.model.id == id).first()


    def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> List[ModelType]:
        """Get multiple records with filtering, pagination and ordering"""
        query = self.db.query(self.model)
        
        if filters:
            filter_conditions = []
            for key, value in filters.items():
                if hasattr(self.model, key):
                    if isinstance(value, list):
                        filter_conditions.append(getattr(self.model, key).in_(value))
                    elif isinstance(value, dict) and 'like' in value:
                        filter_conditions.append(getattr(self.model, key).like(f"%{value['like']}%"))
                    else:
                        filter_conditions.append(getattr(self.model, key) == value)
            
            if filter_conditions:
                query = query.filter(and_(*filter_conditions))
        
        if order_by and hasattr(self.model, order_by):
            if order_desc:
                query = query.order_by(desc(getattr(self.model, order_by)))
            else:
                query = query.order_by(asc(getattr(self.model, order_by)))
        
        return query.offset(skip).limit(limit).all()


    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        query = self.db.query(self.model)
        
        if filters:
            filter_conditions = []
            for key, value in filters.items():
                if hasattr(self.model, key):
                    if isinstance(value, list):
                        filter_conditions.append(getattr(self.model, key).in_(value))
                    elif isinstance(value, dict) and 'like' in value:
                        filter_conditions.append(getattr(self.model, key).like(f"%{value['like']}%"))
                    else:
                        filter_conditions.append(getattr(self.model, key) == value)
            
            if filter_conditions:
                query = query.filter(and_(*filter_conditions))
        
        return query.count()


    def create(self, obj_in: CreateSchemaType) -> ModelType:
        if hasattr(obj_in, 'dict'):
            obj_in_data = obj_in.dict()
        else:
            obj_in_data = obj_in
            
        db_obj = self.model(**obj_in_data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj


    def update(self, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        if hasattr(obj_in, 'dict'):
            update_data = obj_in.dict(exclude_unset=True)
        else:
            update_data = obj_in

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj


    def delete(self, id: Any) -> Optional[ModelType]:
        obj = self.db.query(self.model).filter(self.model.id == id).first()
        if obj:
            self.db.delete(obj)
            self.db.commit()
        return obj


    def soft_delete(self, id: Any) -> Optional[ModelType]:
        obj = self.db.query(self.model).filter(self.model.id == id).first()
        if obj and hasattr(obj, 'is_active'):
            obj.is_active = False
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
        return obj


    def exists(self, id: Any) -> bool:
        return self.db.query(self.model).filter(self.model.id == id).first() is not None


    def get_by_field(self, field_name: str, field_value: Any) -> Optional[ModelType]:
        if hasattr(self.model, field_name):
            return self.db.query(self.model).filter(
                getattr(self.model, field_name) == field_value
            ).first()
        return None


    def get_multi_by_field(self, field_name: str, field_value: Any) -> List[ModelType]:
        if hasattr(self.model, field_name):
            return self.db.query(self.model).filter(
                getattr(self.model, field_name) == field_value
            ).all()
        return []


    def search(self, search_term: str, search_fields: List[str]) -> List[ModelType]:
        if not search_term or not search_fields:
            return []
        
        search_conditions = []
        for field in search_fields:
            if hasattr(self.model, field):
                search_conditions.append(
                    getattr(self.model, field).like(f"%{search_term}%")
                )
        
        if search_conditions:
            return self.db.query(self.model).filter(or_(*search_conditions)).all()
        return []