
from uuid_utils import uuid7
from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import event
from .utils import get_cairo_time

class Base(AsyncAttrs, DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models, providing common async features.
    """

    id = Column(String(36), primary_key=True, default=lambda: str(uuid7()), index=True)
    created_at = Column(DateTime, default=None, nullable=True)
    updated_at = Column(DateTime, default=None, nullable=True)

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.created_at is None:
            self.created_at = get_cairo_time()

# Add event listener for all models that inherit from Base
@event.listens_for(Base, 'before_update', propagate=True)
def update_updated_at(mapper, connection, target):
    """Automatically update updated_at timestamp with local time before any update"""
    target.updated_at = get_cairo_time()