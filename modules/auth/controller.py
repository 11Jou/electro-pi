from fastapi import APIRouter, Depends
from modules.auth.services import AuthService, get_auth_service
from modules.auth.schemas import *



router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, auth_service: AuthService = Depends(get_auth_service)) -> UserResponse:
    new_user = await auth_service.register_user(user)
    return UserResponse(
    id=new_user.id, 
    full_name=new_user.full_name, 
    email=new_user.email, 
    created_at=new_user.created_at, 
    updated_at=new_user.updated_at)


@router.post("/login", response_model=Token)
async def login_user(email: str, password: str, auth_service: AuthService = Depends(get_auth_service)) -> Token:
    return await auth_service.login_user(email, password)