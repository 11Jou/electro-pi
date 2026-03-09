from fastapi import Depends, HTTPException
from modules.auth.services import AuthService, get_auth_service
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from modules.auth.models import User
from modules.organization.repository import MembershipRepository, get_membership_repository
from modules.organization.models import Role


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    auth_service: AuthService = Depends(get_auth_service)):

    token = credentials.credentials
    payload = auth_service.security_service.decode_token(token)
    email = payload.get("sub")

    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await auth_service.user_repository.get_user_by_email(email)
    return user




async def require_org_admin(
    organization_id: int,
    current_user: User = Depends(get_current_user),
    membership_repository: MembershipRepository = Depends(get_membership_repository),
) -> None:
    """Ensure the current user is an admin of the given organization. Raises 403 otherwise."""
    membership = await membership_repository.get_membership_by_org_and_user(
        organization_id, current_user.id
    )
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this organization")
    if membership.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Only organization admins can use this endpoint")


async def get_org_membership(
    organization_id: int,
    current_user: User = Depends(get_current_user),
    membership_repository: MembershipRepository = Depends(get_membership_repository),
):
    """Return the current user's membership in the given organization, or raise 403 if not a member."""
    membership = await membership_repository.get_membership_by_org_and_user(
        organization_id, current_user.id
    )
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this organization")
    return membership