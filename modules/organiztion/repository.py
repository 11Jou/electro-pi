from abc import ABC, abstractmethod
from typing import List
from core.database import AsyncSession
from modules.organiztion.models import Organization, Membership
from sqlalchemy import select

class IOrganizationRepository(ABC):
    @abstractmethod
    async def create_organization(self, organization: Organization) -> Organization:
        pass

    @abstractmethod
    async def get_organization_by_id(self, id: int) -> Organization:
        pass

    @abstractmethod
    async def get_user_organizations(self, user_id: int) -> List[Membership]:



class OrganizationRepository(IOrganizationRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_organization(self, organization: Organization) -> Organization:
        self.db.add(organization)
        await self.db.commit()
        await self.db.refresh(organization)
        return organization


    async def get_organization_by_id(self, id: int) -> Organization:
        result = await self.db.execute(select(Organization).where(Organization.id == id))
        return result.scalars().first()

    async def get_user_organizations(self, user_id: int) -> List[Membership]:
        result = await self.db.execute(select(Membership).where(Membership.user_id == user_id))
        return result.scalars().all()

class IMembershipRepository(ABC):
    @abstractmethod
    async def create_membership(self, membership: Membership) -> Membership:
        pass

    @abstractmethod
    async def get_membership_by_id(self, id: int) -> Membership:
        pass


class MembershipRepository(IMembershipRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_membership(self, membership: Membership) -> Membership:
        self.db.add(membership)
        await self.db.commit()
        await self.db.refresh(membership)
        return membership

    async def get_membership_by_id(self, id: int) -> Membership:
        result = await self.db.execute(select(Membership).where(Membership.id == id))
        return result.scalars().first()