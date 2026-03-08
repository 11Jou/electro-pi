from fastapi import FastAPI, Depends
from core.database import Base, engine
from modules.auth.controller import router as auth_router

app = FastAPI()


Base.metadata.create_all(bind=engine)
app.include_router(auth_router)