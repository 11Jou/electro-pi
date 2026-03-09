from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from modules.organization.schemas import *
from modules.organization.services import *
from modules.organization.repository import MembershipRepository, get_membership_repository
from modules.organization.models import Role
from modules.auth.check_auth import get_current_user, require_org_admin, get_org_membership
from modules.auth.models import User
from modules.auth.services import *


router = APIRouter(prefix="/organization", tags=["organization"])



@router.post("", response_model=OrganizationResponse)
async def create_organization(
    body: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    organization_service: OrganizationService = Depends(get_organization_service),
) -> OrganizationResponse:
    return await organization_service.create_organization(body, user_id=current_user.id)


@router.post("/{organization_id}/user", response_model=MembershipResponse)
async def create_membership(
    body: MembershipCreateWithUserEmail,
    organization_id: int,
    _: None = Depends(require_org_admin),
    membership_service: MembershipService = Depends(get_membership_service),
) -> MembershipResponse:
    return await membership_service.create_membership(organization_id=organization_id, membership=body)



@router.get("/{organization_id}/users", response_model=List[UserMembershipResponse])
async def get_memberships(
    organization_id: int,
    limit: int = Query(10,ge=1, le=100),
    offset: int = Query(0, ge=0),
    _: None = Depends(require_org_admin),
    membership_service: MembershipService = Depends(get_membership_service),
) -> List[UserMembershipResponse]:
    return await membership_service.get_memberships(organization_id=organization_id, limit=limit, offset=offset)




@router.get("/{organization_id}/users/search", response_model=List[UserMembershipResponse])
async def search_memberships(
    organization_id: int,
    query: str,
    _: None = Depends(require_org_admin),
    membership_service: MembershipService = Depends(get_membership_service),
) -> List[UserMembershipResponse]:
    return await membership_service.search_memberships(organization_id=organization_id, query=query)


@router.post("/{organization_id}/item", response_model=ItemResponse)
async def create_item(
    organization_id: int,
    body: ItemCreate,
    current_user: User = Depends(get_current_user),
    membership: Membership = Depends(get_org_membership),
    item_service: ItemService = Depends(get_item_service),
) -> ItemResponse:
    return await item_service.create_item(
        organization_id=organization_id, item=body, user=current_user
    )


@router.get("/{organization_id}/item", response_model=List[ItemResponse])
async def get_items(
    organization_id: int,
    limit: int = Query(10,ge=1, le=100),
    offset: int = Query(0, ge=0),
    membership=Depends(get_org_membership),
    current_user: User = Depends(get_current_user),
    item_service: ItemService = Depends(get_item_service),
) -> List[ItemResponse]:
    if membership.role == Role.ADMIN:
        return await item_service.get_items(organization_id=organization_id, user_id=current_user.id, limit=limit, offset=offset)
    return await item_service.get_item_user(
        organization_id=organization_id, user_id=current_user.id, limit=limit, offset=offset
    )


@router.get("/{organization_id}/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    organization_id: int,
    limit: int = Query(10,ge=1, le=100),
    offset: int = Query(0, ge=0),
    _: None = Depends(require_org_admin),
    audit_service: AuditService = Depends(get_audit_service),
) -> List[AuditLogResponse]:
    return await audit_service.get_audit_logs(organization_id=organization_id, limit=limit, offset=offset)



