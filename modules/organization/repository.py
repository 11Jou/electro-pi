from typing import List, Optional
from core.database import AsyncSession, get_db
from fastapi import Depends
from modules.auth.models import User
from modules.organization.models import *
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload


def get_organization_repository(db: AsyncSession = Depends(get_db)) -> "OrganizationRepository":
    return OrganizationRepository(db)


def get_membership_repository(db: AsyncSession = Depends(get_db)) -> "MembershipRepository":
    return MembershipRepository(db)


def get_item_repository(db: AsyncSession = Depends(get_db)) -> "ItemRepository":
    return ItemRepository(db)

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
        audit_log = AuditLog(user_id=user_id, organization_id=organization.id,
            action=f"Organization created by user {user_id}",
        )
        self.db.add(audit_log)
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
        await self.db.flush()
        audit_log = AuditLog(user_id=membership.user_id, organization_id=membership.organization_id,
            action=f"Membership created by user {membership.user_id} for organization {membership.organization_id}",
        )
        self.db.add(audit_log)
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



class ItemRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_item(self, item: Item) -> Item:
        self.db.add(item)
        self.db.flush()
        audit_log = AuditLog(user_id=item.user_id, organization_id=item.organization_id,
            action=f"Item created for user {item.user_id} in organization {item.organization_id}",
        )
        self.db.add(audit_log)
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




class AuditLogRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_audit_logs(self, organization_id: int, limit: int = 20, offset: int = 0) -> List[AuditLog]:
        result = await self.db.execute(
            select(AuditLog)
            .where(AuditLog.organization_id == organization_id)
            .options(selectinload(AuditLog.user))
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
