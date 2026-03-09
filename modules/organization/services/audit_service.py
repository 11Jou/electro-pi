from modules.organization.repository import IAuditLogRepository, get_audit_log_repository
from modules.organization.models import AuditLog
from typing import List
from fastapi import Depends


def get_audit_service(
    audit_log_repository: IAuditLogRepository = Depends(get_audit_log_repository),
) -> "AuditService":
    return AuditService(audit_log_repository)


class AuditService:
    def __init__(self, audit_log_repository: IAuditLogRepository):
        self.audit_log_repository = audit_log_repository

    async def create_audit_log(self, audit_log: AuditLog) -> AuditLog:
        return await self.audit_log_repository.create_audit_log(audit_log)

    async def log_action(
        self, organization_id: int, user_id: int, action: str
    ) -> AuditLog:
        audit_log = AuditLog(
            user_id=user_id,
            organization_id=organization_id,
            action=action,
        )
        return await self.create_audit_log(audit_log)

    async def get_audit_logs(
        self, organization_id: int, limit: int = 20, offset: int = 0
    ) -> List[AuditLog]:
        return await self.audit_log_repository.get_audit_logs(
            organization_id, limit, offset
        )