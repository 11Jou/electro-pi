from fastapi import APIRouter, Depends, HTTPException

from modules.organization.schemas import *
from modules.organization.services import *
from modules.organization.repository import MembershipRepository, get_membership_repository
from modules.organization.models import Role
from modules.auth.check_auth import get_current_user, require_org_admin
from modules.auth.models import User
from modules.auth.services import AuthService, get_auth_service


router = APIRouter(prefix="/organization", tags=["organization"])



@router.post("", response_model=OrganizationResponse)
async def create_organization(
    body: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    organization_service: OrganizationService = Depends(get_organization_service),
) -> OrganizationResponse:
    return await organization_service.create_organization(body, user=current_user)


@router.post("/{organization_id}/user", response_model=MembershipResponse)
async def create_membership(
    body: MembershipCreateWithUserEmail,
    organization_id: int,
    _: None = Depends(require_org_admin),
    membership_service: MembershipService = Depends(get_membership_service),
) -> MembershipResponse:
    return await membership_service.create_membership(organization_id=organization_id, membership=body)