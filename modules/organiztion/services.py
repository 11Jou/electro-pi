from abc import ABC, abstractmethod
from modules.organiztion.schemas import OrganizationCreate, OrganizationResponse
from modules.organiztion.repository import IOrganizationRepository, IMembershipRepository
from modules.organiztion.models import Organization

class OrganizationService:
    def __init__(self, organization_repository: IOrganizationRepository):
        self.organization_repository = organization_repository

    async def create_organization(self, organization: OrganizationCreate) -> OrganizationResponse:
        organization = Organization(name=organization.name)
        return await self.organization_repository.create_organization(organization)

    async def get_organization_by_id(self, id: int) -> OrganizationResponse:
        organization = await self.organization_repository.get_organization_by_id(id)
        return OrganizationResponse(id=organization.id, name=organization.name, created_at=organization.created_at, updated_at=organization.updated_at)

    async def get_user_organizations(self, user_id: int) -> List[MembershipResponse]:
        memberships = await self.organization_repository.get_user_organizations(user_id)
        return [MembershipResponse(
        id=membership.id, 
        organization_id=membership.organization_id, 
        user_id=membership.user_id, 
        role=membership.role, 
        created_at=membership.created_at, 
        updated_at=membership.updated_at) 
        for membership in memberships]


class MembershipService:
    def __init__(self, membership_repository: IMembershipRepository):
        self.membership_repository = membership_repository

    async def create_membership(self, membership: MembershipCreate) -> MembershipResponse:
        membership = Membership(organization_id=membership.organization_id, 
        user_id=membership.user_id, 
        role=membership.role)

    async def get_membership_by_id(self, id: int) -> MembershipResponse:
        membership = await self.membership_repository.get_membership_by_id(id)
        return MembershipResponse(id=membership.id, 
        organization_id=membership.organization_id, 
        user_id=membership.user_id, 
        role=membership.role, 
        created_at=membership.created_at, 
        updated_at=membership.updated_at)