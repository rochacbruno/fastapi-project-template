from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import BaseModel
from ..security import HashedPassword


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(sa_column_kwargs={"unique": True})
    password: HashedPassword
    superuser: bool = False


class UserResponse(BaseModel):
    id: int
    username: str
