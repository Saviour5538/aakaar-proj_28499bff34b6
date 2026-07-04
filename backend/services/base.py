from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

class BaseService:
    def __init__(self, model):
        self.model = model

    def create(self, db: Session, obj_data: dict):
        try:
            obj = self.model(**obj_data)
            db.add(obj)
            db.commit()
            db.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            db.rollback()
            raise RuntimeError(f"Error creating {self.model.__name__}: {str(e)}")

    def read(self, db: Session, obj_id):
        obj = db.query(self.model).filter(self.model.id == obj_id).first()
        if not obj:
            raise RuntimeError(f"{self.model.__name__} with ID {obj_id} not found")
        return obj

    def update(self, db: Session, obj_id, update_data: dict):
        obj = db.query(self.model).filter(self.model.id == obj_id).first()
        if not obj:
            raise RuntimeError(f"{self.model.__name__} with ID {obj_id} not found")
        try:
            for key, value in update_data.items():
                setattr(obj, key, value)
            db.commit()
            db.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            db.rollback()
            raise RuntimeError(f"Error updating {self.model.__name__}: {str(e)}")

    def delete(self, db: Session, obj_id):
        obj = db.query(self.model).filter(self.model.id == obj_id).first()
        if not obj:
            raise RuntimeError(f"{self.model.__name__} with ID {obj_id} not found")
        try:
            db.delete(obj)
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            raise RuntimeError(f"Error deleting {self.model.__name__}: {str(e)}")