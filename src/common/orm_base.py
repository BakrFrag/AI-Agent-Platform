
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
    created_at = Column(DateTime, default=get_cairo_time())
    updated_at = Column(DateTime, default=None, nullable=True)

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"

