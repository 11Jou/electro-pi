from abc import ABC, abstractmethod
from core.database import AsyncSession
from modules.organization.models import Item
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from fastapi import Depends
from core.database import get_db



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
    async def get_items(self, organization_id: int, limit: int = 20, offset: int = 0) -> List[Item]:
        pass

    @abstractmethod
    async def get_item_user(self, organization_id: int, user_id: int, limit: int = 20, offset: int = 0) -> List[Item]:
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

    async def get_items(self, organization_id: int, limit: int = 20, offset: int = 0) -> List[Item]:
        result = await self.db.execute(select(Item).where(Item.organization_id == organization_id).limit(limit).offset(offset))
        return result.scalars().all()

    async def get_item_user(self, organization_id: int, user_id: int, limit: int = 20, offset: int = 0) -> List[Item]:
        result = await self.db.execute(select(Item).where(Item.organization_id == organization_id).where(Item.user_id == user_id).limit(limit).offset(offset))
        return result.scalars().all()


def get_item_repository(db: AsyncSession = Depends(get_db)) -> "ItemRepository":
    return ItemRepository(db)