from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException
from modules.auth.models import User
from modules.auth.schemas import *
from modules.auth.repository import UserRepository, get_user_repository
from fastapi import Depends

class SecurityService:

    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = "mG/xJYdH/b3bR9K2FJqaVUTAvrie2dQxdytkDQPUfGo="
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(password, hashed_password)


    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")


def get_security_service() -> SecurityService:
    return SecurityService()



class AuthService:

    def __init__(self, user_repository: UserRepository, security_service: SecurityService):
        self.user_repository = user_repository
        self.security_service = security_service

    async def register_user(self, user: UserCreate) -> UserResponse:
        if await self.user_repository.get_user_by_email(user.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        hashed_password = self.security_service.hash_password(user.password)
        user = User(full_name=user.full_name, email=user.email, password=hashed_password)
        return await self.user_repository.create_user(user)

    async def login_user(self, email: str, password: str) -> str:
        user = await self.user_repository.get_user_by_email(email)
        if not user or not self.security_service.verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = self.security_service.create_access_token({"sub": user.email})
        return Token(access_token=access_token, token_type="bearer")


def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository), 
    security_service: SecurityService = Depends(get_security_service)
) -> AuthService:
    return AuthService(user_repository, security_service)