from abc import ABC, abstractmethod
from typing import List
from fastapi import Depends, HTTPException
from modules.organization.schemas import *
from modules.organization.repository import *
from modules.organization.models import Organization, Membership
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