from typing import List, Optional
from core.database import AsyncSession, get_db
from fastapi import Depends
from modules.auth.models import User
from modules.organization.models import Organization, Membership, Role
from sqlalchemy import select


def get_organization_repository(db: AsyncSession = Depends(get_db)) -> "OrganizationRepository":
    return OrganizationRepository(db)


def get_membership_repository(db: AsyncSession = Depends(get_db)) -> "MembershipRepository":
    return MembershipRepository(db)


class OrganizationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

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


class MembershipRepository:
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

    async def get_membership_by_org_and_user(
        self, organization_id: int, user_id: int
    ) -> Optional[Membership]:
        result = await self.db.execute(
            select(Membership).where(
                Membership.organization_id == organization_id,
                Membership.user_id == user_id,
            )
        )
        return result.scalars().first()

    async def get_memberships(self, organization_id: int, limit: int = 20, offset: int = 0) -> List[Membership]:
        result = await self.db.execute(select(Membership)
        .where(Membership.organization_id == organization_id)
        .limit(limit)
        .offset(offset))
        return result.scalars().all()


    async def search_memberships(self, organization_id: int, query: str) -> List[Membership]:
        result = await self.db.execute(
            select(Membership)
            .join(Membership.user)
            .where(Membership.organization_id == organization_id)
            .where(User.full_name.ilike(f"%{query}%"))
        )
        return result.scalars().all()
