from abc import ABC
from modules.auth.models import User

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
        return await self.db.query(User).filter(User.email == email).first()

    async def get_user_by_id(self, id: int) -> User:
        return await self.db.query(User).filter(User.id == id).first()        