from modules.organization.repository import IMembershipRepository, get_membership_repository
from modules.organization.models import Membership
from modules.organization.schemas import MembershipCreateWithUserEmail, MembershipResponse, UserMembershipResponse
from modules.organization.services.audit_service import AuditService, get_audit_service
from modules.auth.services import AuthService, get_auth_service
from fastapi import HTTPException, Depends
from typing import List
from modules.auth.models import User



class MembershipService:
    def __init__(
        self,
        membership_repository: IMembershipRepository,
        auth_service: AuthService,
        audit_service: AuditService,
    ):
        self.membership_repository = membership_repository
        self.auth_service = auth_service
        self.audit_service = audit_service

    async def create_membership(self, organization_id: int, membership: MembershipCreateWithUserEmail) -> MembershipResponse:
        user = await self.auth_service.user_repository.get_user_by_email(membership.user_email)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        existing_membership = await self.membership_repository.get_membership_by_org_and_user(
            organization_id,
            user.id,
        )

        if existing_membership:
            raise HTTPException(status_code=400, detail="User already a member of this organization")

        membership = Membership(organization_id=organization_id, user_id=user.id, role=membership.role)
        membership = await self.membership_repository.create_membership(membership)

        await self.audit_service.log_action(
            organization_id=organization_id,
            user_id=user.id,
            action=f"Membership created by user {user.id} for organization {organization_id}",
        )

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

    async def get_memberships(self, organization_id: int, limit: int = 20, offset: int = 0) -> List[UserMembershipResponse]:
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


def get_membership_service(
    membership_repository: IMembershipRepository = Depends(get_membership_repository),
    auth_service: AuthService = Depends(get_auth_service),
    audit_service: AuditService = Depends(get_audit_service),
) -> MembershipService:
    return MembershipService(membership_repository, auth_service, audit_service)