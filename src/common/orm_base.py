from sqlalchemy import Column, Integer, DateTime, func
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

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"