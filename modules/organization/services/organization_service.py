from modules.organization.models import Organization
from modules.organization.schemas import OrganizationCreate, OrganizationResponse
from modules.organization.repository import get_organization_repository, IOrganizationRepository
from modules.organization.services.audit_service import AuditService, get_audit_service
from fastapi import Depends


def get_organization_service(
    organization_repository: IOrganizationRepository = Depends(get_organization_repository),
    audit_service: AuditService = Depends(get_audit_service),
) -> OrganizationService:
    return OrganizationService(organization_repository, audit_service)


class OrganizationService:
    def __init__(
        self,
        organization_repository: IOrganizationRepository,
        audit_service: AuditService,
    ):
        self.organization_repository = organization_repository
        self.audit_service = audit_service

    async def create_organization(self, organization: OrganizationCreate, user_id: int) -> OrganizationResponse:
        org = Organization(name=organization.name)
        org = await self.organization_repository.create_organization(org, user_id=user_id)
        await self.audit_service.log_action(
            organization_id=org.id,
            user_id=user_id,
            action=f"Organization created by user {user_id}",
        )
        return OrganizationResponse(id=org.id, name=org.name, created_at=org.created_at, updated_at=org.updated_at)

    async def get_organization_by_id(self, id: int) -> OrganizationResponse:
        organization = await self.organization_repository.get_organization_by_id(id)
        return OrganizationResponse(id=organization.id, name=organization.name, created_at=organization.created_at, updated_at=organization.updated_at)

