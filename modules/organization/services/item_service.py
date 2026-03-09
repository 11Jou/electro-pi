from modules.organization.repository import IItemRepository, get_item_repository
from modules.organization.models import Item
from modules.organization.schemas import ItemCreate, ItemResponse
from modules.organization.services.audit_service import AuditService, get_audit_service
from modules.auth.models import User
from typing import List, Optional
from fastapi import Depends


def get_item_service(
    item_repository: IItemRepository = Depends(get_item_repository),
    audit_service: AuditService = Depends(get_audit_service),
) -> ItemService:
    return ItemService(item_repository, audit_service)


class ItemService:
    def __init__(self, item_repository: IItemRepository, audit_service: AuditService):
        self.item_repository = item_repository
        self.audit_service = audit_service

    async def create_item(self, organization_id: int, item: ItemCreate, user: User) -> ItemResponse:
        item = Item(
            organization_id=organization_id,
            user_id=user.id,
            details=item.details,
        )
        item = await self.item_repository.create_item(item)
        await self.audit_service.log_action(
            organization_id=organization_id,
            user_id=user.id,
            action=f"Item created for user {user.id} in organization {organization_id}",
        )
        return ItemResponse(id=item.id, created_at=item.created_at, updated_at=item.updated_at)

    async def get_item_by_id(self, id: int) -> ItemResponse:
        item = await self.item_repository.get_item_by_id(id)
        return ItemResponse(id=item.id, created_at=item.created_at, updated_at=item.updated_at)

    async def get_items(self, organization_id: int, user_id: Optional[int] = None,limit: int = 20, offset: int = 0
    ) -> List[ItemResponse]:
        items = await self.item_repository.get_items(
            organization_id, created_by_user_id=user_id, limit=limit, offset=offset
        )
        return [
            ItemResponse(id=item.id, created_at=item.created_at, updated_at=item.updated_at)
            for item in items
        ]
