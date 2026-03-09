from abc import ABC, abstractmethod
from modules.organization.models import Organization
from core.database import AsyncSession
from modules.organization.models import Membership, Role
from sqlalchemy import select
from fastapi import Depends
from core.database import get_db



class IOrganizationRepository(ABC):

    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def create_organization(self, organization: Organization, user_id: int) -> Organization:
        pass

    @abstractmethod
    async def get_organization_by_id(self, id: int) -> Organization:
        pass

class OrganizationRepository(IOrganizationRepository):

    async def create_organization(self, organization: Organization, user_id: int) -> Organization:
        self.db.add(organization)
        await self.db.flush()
        membership = Membership(
            organization_id=organization.id,
            user_id=user_id,
            role=Role.ADMIN,
        )
        self.db.add(membership)
        await self.db.commit()
        await self.db.refresh(organization)
        return organization

    async def get_organization_by_id(self, id: int) -> Organization:
        result = await self.db.execute(select(Organization).where(Organization.id == id))
        return result.scalars().first()



def get_organization_repository(db: AsyncSession = Depends(get_db)) -> "OrganizationRepository":
    return OrganizationRepository(db)