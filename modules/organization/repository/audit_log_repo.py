from abc import ABC, abstractmethod
from typing import List
from core.database import AsyncSession
from modules.organization.models import AuditLog
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import Depends
from core.database import get_db

def get_audit_log_repository(db: AsyncSession = Depends(get_db)) -> "AuditLogRepository":
    return AuditLogRepository(db)

class IAuditLogRepository(ABC):

    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def create_audit_log(self, audit_log: AuditLog) -> AuditLog:
        pass

    @abstractmethod
    async def get_audit_logs(self, organization_id: int, limit: int = 20, offset: int = 0) -> List[AuditLog]:
        pass



class AuditLogRepository(IAuditLogRepository):


    async def create_audit_log(self, audit_log: AuditLog) -> AuditLog:
        self.db.add(audit_log)
        await self.db.commit()
        await self.db.refresh(audit_log)
        return audit_log

    async def get_audit_logs(self, organization_id: int, limit: int = 20, offset: int = 0) -> List[AuditLog]:
        result = await self.db.execute(
            select(AuditLog)
            .where(AuditLog.organization_id == organization_id)
            .options(selectinload(AuditLog.user))
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

        