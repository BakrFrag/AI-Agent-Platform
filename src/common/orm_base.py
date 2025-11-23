import datetime
from sqlalchemy import Column, Integer, DateTime, func, event
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, declared_attr

class Base(AsyncAttrs, DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models, providing common async features.
    """
    @declared_attr
    def __tablename__(cls):
        # Automatically generate table name from class name
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, nullable=True)
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"
    
@event.listens_for(Base, 'before_update', propagate=True)
def receive_before_update(mapper, connection, target):
    """Automatically set updated_at before any update"""
    target.updated_at = datetime.utcnow()