from abc import ABC, abstractmethod
from core.database import AsyncSession
from modules.organization.models import Item
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from fastapi import Depends
from core.database import get_db

def get_item_repository(db: AsyncSession = Depends(get_db)) -> "ItemRepository":
    return ItemRepository(db)

class IItemRepository(ABC):

    def __init__(self, db: AsyncSession):
        self.db = db


    @abstractmethod
    async def create_item(self, item: Item) -> Item:
        pass

    @abstractmethod
    async def get_item_by_id(self, id: int) -> Item:
        pass

    @abstractmethod
    async def get_items(self, organization_id: int, created_by_user_id: Optional[int] = None, limit: int = 20, offset: int = 0) -> List[Item]:
        pass


class ItemRepository(IItemRepository):


    async def create_item(self, item: Item) -> Item:
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def get_item_by_id(self, id: int) -> Item:
        result = await self.db.execute(select(Item).where(Item.id == id))
        return result.scalars().first()

    async def get_items(
        self, organization_id: int, created_by_user_id: Optional[int] = None,
        limit: int = 20, offset: int = 0
    ) -> List[Item]:
        stmt = select(Item).where(Item.organization_id == organization_id)
        if created_by_user_id is not None:
            stmt = stmt.where(Item.user_id == created_by_user_id)
        result = await self.db.execute(stmt.limit(limit).offset(offset))
        return list(result.scalars().all())