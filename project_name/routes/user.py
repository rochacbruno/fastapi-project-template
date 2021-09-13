from typing import List

from fastapi import APIRouter
from sqlmodel import Session, select

from ..db import engine
from ..models.user import User, UserResponse


router = APIRouter()


@router.get("/list/", response_model=List[UserResponse])
async def list_users():
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        return users


@router.post("/", response_model=User)
async def create_user(user: User):
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    with Session(engine) as session:
        user = session.query(User).get(user_id)
        return user
