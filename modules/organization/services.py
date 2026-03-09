from abc import ABC, abstractmethod
from typing import List, Optional
from fastapi import Depends, HTTPException
from modules.organization.schemas import *
from modules.organization.repository import *
from modules.organization.models import Organization, Membership, Item
from modules.auth.models import User
from modules.auth.services import AuthService, get_auth_service

def get_organization_service(
    organization_repository: OrganizationRepository = Depends(get_organization_repository),
) -> "OrganizationService":
    return OrganizationService(organization_repository)


def get_membership_service(
    membership_repository: MembershipRepository = Depends(get_membership_repository),
    auth_service: AuthService = Depends(get_auth_service),
) -> "MembershipService":
    return MembershipService(membership_repository, auth_service)


def get_item_service(
    item_repository: ItemRepository = Depends(get_item_repository),
) -> "ItemService":
    return ItemService(item_repository)


class OrganizationService:
    def __init__(self, organization_repository: OrganizationRepository):
        self.organization_repository = organization_repository

    async def create_organization(self, organization: OrganizationCreate, user_id: int) -> OrganizationResponse:
        org = Organization(name=organization.name)
        org = await self.organization_repository.create_organization(org, user_id=user_id)
        return OrganizationResponse(id=org.id, name=org.name, created_at=org.created_at, updated_at=org.updated_at)

    async def get_organization_by_id(self, id: int) -> OrganizationResponse:
        organization = await self.organization_repository.get_organization_by_id(id)
        return OrganizationResponse(id=organization.id, name=organization.name, created_at=organization.created_at, updated_at=organization.updated_at)



class MembershipService:
    def __init__(self, membership_repository: MembershipRepository, auth_service: AuthService):
        self.membership_repository = membership_repository
        self.auth_service = auth_service

    async def create_membership(self, organization_id: int, membership: MembershipCreateWithUserEmail) -> MembershipResponse:


        user = await self.auth_service.user_repository.get_user_by_email(membership.user_email)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        existing_membership = await self.membership_repository.get_membership_by_org_and_user(
            organization_id, 
            user.id)

        if existing_membership:
            raise HTTPException(status_code=400, detail="User already a member of this organization")

        membership = Membership(organization_id=organization_id, user_id=user.id, role=membership.role)
        membership = await self.membership_repository.create_membership(membership)


        return MembershipResponse( 
        organization_id=membership.organization_id, 
        user_id=membership.user_id, 
        role=membership.role, 
        created_at=membership.created_at, 
        updated_at=membership.updated_at)

    async def get_membership_by_id(self, id: int) -> MembershipResponse:
        membership = await self.membership_repository.get_membership_by_id(id)
        return MembershipResponse(id=membership.id, 
        organization_id=membership.organization_id, 
        user_id=membership.user_id, 
        role=membership.role, 
        created_at=membership.created_at, 
        updated_at=membership.updated_at)

    async def get_memberships(self, organization_id: int, limit: int = 20, offset: int = 0) -> List[UserResponse]:
        memberships = await self.membership_repository.get_memberships(organization_id, limit, offset)
        return [UserMembershipResponse(
        id=membership.user_id, 
        full_name=membership.user.full_name, 
        email=membership.user.email, 
        role=membership.role,
        created_at=membership.user.created_at, 
        updated_at=membership.user.updated_at) 
        for membership in memberships]


    async def search_memberships(self, organization_id: int, query: str) -> List[UserMembershipResponse]:
        memberships = await self.membership_repository.search_memberships(organization_id, query)
        return [UserMembershipResponse(
        id=membership.user_id, 
        full_name=membership.user.full_name, 
        email=membership.user.email, 
        role=membership.role,
        created_at=membership.user.created_at, 
        updated_at=membership.user.updated_at) 
        for membership in memberships]

class ItemService:
    def __init__(self, item_repository: ItemRepository):
        self.item_repository = item_repository

    async def create_item(
        self, organization_id: int, item: ItemCreate, user: User
    ) -> ItemResponse:
        item = Item(
            organization_id=organization_id,
            user_id=user.id,
            details=item.details,
        )
        item = await self.item_repository.create_item(item)
        return ItemResponse(id=item.id, created_at=item.created_at, updated_at=item.updated_at)

    async def get_item_by_id(self, id: int) -> ItemResponse:
        item = await self.item_repository.get_item_by_id(id)
        return ItemResponse(id=item.id, created_at=item.created_at, updated_at=item.updated_at)

    async def get_items(
        self, organization_id: int, user_id: Optional[int] = None
    ) -> List[ItemResponse]:
        items = await self.item_repository.get_items(
            organization_id, created_by_user_id=user_id
        )
        return [
            ItemResponse(id=item.id, created_at=item.created_at, updated_at=item.updated_at)
            for item in items
        ]
