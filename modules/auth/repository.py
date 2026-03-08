from abc import ABC, abstractmethod
from modules.auth.models import User
from core.database import AsyncSession, get_db
from fastapi import Depends
from sqlalchemy import select

def get_user_repository(db: AsyncSession = Depends(get_db)) -> IUserRepository:
    return UserRepository(db)

class IUserRepository(ABC):

    @abstractmethod
    async def create_user(self, user: User) -> User:
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> User:
        pass

    @abstractmethod
    async def get_user_by_id(self, id: int) -> User:
        pass



class UserRepository(IUserRepository):


    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_user_by_email(self, email: str) -> User:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()


    async def get_user_by_id(self, id: int) -> User:
        result = await self.db.execute(select(User).where(User.id == id))
        return result.scalars().first()        