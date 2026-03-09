from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import JSONB
from enum import Enum
from datetime import datetime

from core.database import Base
from sqlalchemy.orm import relationship

class Role(Enum):
    ADMIN = "admin"
    MEMBER = "member"

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


    memberships = relationship("Membership", back_populates="organization", cascade="all, delete-orphan")
    items = relationship("Item", back_populates="organization", cascade="all, delete-orphan")



class Membership(Base):
    __tablename__ = "memberships"
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, primary_key=True)
    role = Column(SQLAlchemyEnum(Role), nullable=False, default=Role.MEMBER)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", lazy="joined", back_populates="memberships")
    user = relationship("User", lazy="joined", back_populates="memberships")


class Item(Base):
    __tablename__ = "items"


    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    details = Column(JSONB, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", lazy="joined", back_populates="items")
