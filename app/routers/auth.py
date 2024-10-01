from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from passlib.context import CryptContext
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db_depends import get_db
from app.models.user import User
from app.schemas import CreateUser

from fastapi.security import HTTPBasic, HTTPBasicCredentials

router = APIRouter(prefix="/auth", tags=['auth'])
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
security = HTTPBasic()


@router.post("/")
async def create_user(db: Annotated[AsyncSession, Depends(get_db)],
                      create_user: CreateUser):
    await db.execute(insert(User).values(first_name=create_user.first_name,
                                         last_name=create_user.last_name,
                                         username=create_user.username,
                                         email=create_user.email,
                                         hashed_password=bcrypt_context.hash(create_user.password)
                                         ))
    await db.commit()
    return {
        "status": status.HTTP_201_CREATED,
        "transaction": "Successful"
    }


async def get_current_username(db: Annotated[AsyncSession, Depends(get_db)],
                               credentials: HTTPBasicCredentials = Depends(security)):
    user = await db.scalar(select(User).where(User.username == credentials.username))
    if not user or not bcrypt_context.verify(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    return user


@router.get("/user/me")
async def read_current_user(user: dict = Depends(get_current_username)):
    return {"user": user}
