from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, Sequence, Any

from sqlalchemy.ext.asyncio import AsyncSession
from src.common.orm_base import Base

M = TypeVar('M', bound=Base)
K = TypeVar('K', bound=Any)

class AbstractRepository(ABC, Generic[M, K]):
    """
    Abstract base class defining the contract for all async repository implementations.
    """
    def __init__(self, session: AsyncSession, model: type[M]):
        self.session = session
        self.model = model

    @abstractmethod
    async def create(self, entity: M) -> M:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, entity_id: K) -> Optional[M]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, entity_id: K, update_data: dict) -> Optional[M]:
        # Accepts raw dictionary data for update statements
        raise NotImplementedError

    @abstractmethod
    async def delete_by_id(self, entity_id: K) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[M]:
        raise NotImplementedError