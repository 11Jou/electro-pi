from abc import ABC, abstractmethod
from typing import List, Optional
from core.database import AsyncSession
from modules.organization.models import Membership
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from fastapi import Depends
from core.database import get_db


class IMembershipRepository(ABC):

    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def create_membership(self, membership: Membership) -> Membership:
        pass

    @abstractmethod
    async def get_membership_by_id(self, id: int) -> Membership:
        pass

    @abstractmethod
    async def get_membership_by_org_and_user(self, organization_id: int, user_id: int) -> Optional[Membership]:
        pass

    @abstractmethod
    async def get_memberships(self, organization_id: int, limit: int = 20, offset: int = 0) -> List[Membership]:
        pass

    @abstractmethod
    async def search_memberships(self, organization_id: int, query: str) -> List[Membership]:
        pass

        

class MembershipRepository(IMembershipRepository):

    async def create_membership(self, membership: Membership) -> Membership:
        self.db.add(membership)
        await self.db.commit()
        await self.db.refresh(membership)
        return membership

    async def get_membership_by_id(self, id: int) -> Membership:
        result = await self.db.execute(select(Membership).where(Membership.id == id))
        return result.scalars().first()

    async def get_membership_by_org_and_user(self, organization_id: int, user_id: int) -> Optional[Membership]:
        result = await self.db.execute(
            select(Membership).where(
                Membership.organization_id == organization_id,
                Membership.user_id == user_id,
            )
        )
        return result.scalars().first()

    async def get_memberships(self, organization_id: int, limit: int = 20, offset: int = 0) -> List[Membership]:
        result = await self.db.execute(
            select(Membership)
            .where(Membership.organization_id == organization_id)
            .options(selectinload(Membership.user))
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()


    async def search_memberships(self, organization_id: int, query: str) -> List[Membership]:
        ts_query = func.plainto_tsquery("english", query)
        match_full_name = func.to_tsvector("english", User.full_name).op("@@")(ts_query)
        match_org_name = func.to_tsvector("english", Organization.name).op("@@")(ts_query)
        result = await self.db.execute(
            select(Membership)
            .join(Membership.user)
            .join(Membership.organization)
            .where(Membership.organization_id == organization_id)
            .where(or_(match_full_name, match_org_name))
            .options(selectinload(Membership.user))
        )
        return result.scalars().all()

def get_membership_repository(db: AsyncSession = Depends(get_db)) -> "MembershipRepository":
    return MembershipRepository(db)