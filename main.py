from fastapi import FastAPI, Depends
from core.database import Base, engine
from modules.auth.controller import router as auth_router
from modules.organization.controller import router as organization_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(organization_router)
