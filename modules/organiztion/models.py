from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum as SQLAlchemyEnum
from enum import Enum
from datetime import datetime

from core.database import Base

class Role(Enum):
    ADMIN = "admin"
    MEMBER = "member"

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)



class Membership(Base):
    __tablename__ = "memberships"
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(SQLAlchemyEnum(Role), nullable=False, default=Role.MEMBER)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)