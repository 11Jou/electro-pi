from pydantic import BaseModel
from datetime import datetime
from modules.organiztion.models import Role

class OrganizationCreate(BaseModel):
    name: str

class OrganizationResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

class MembershipCreate(BaseModel):
    organization_id: int
    user_id: int
    role: Role

class MembershipResponse(BaseModel):
    id: int
    organization_id: int
    user_id: int
    role: Role
    created_at: datetime
    updated_at: datetime