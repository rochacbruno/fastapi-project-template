from typing import List, Union

from fastapi import APIRouter, Request
from fastapi.exceptions import HTTPException
from sqlmodel import Session, or_, select

from ..db import ActiveSession
from ..security import (
    AdminUser,
    AuthenticatedFreshUser,
    AuthenticatedUser,
    User,
    UserCreate,
    UserPasswordPatch,
    UserResponse,
    get_current_user,
    get_password_hash,
)

router = APIRouter()


@router.get("/", response_model=List[UserResponse], dependencies=[AdminUser])
async def list_users(*, session: Session = ActiveSession):
    users = session.exec(select(User)).all()
    return users


@router.post("/", response_model=UserResponse, dependencies=[AdminUser])
async def create_user(*, session: Session = ActiveSession, user: UserCreate):

    # verify user with username doesn't already exist
    try:
        await query_user(session=session, user_id_or_username=user.username)
    except HTTPException:
        pass
    else:
        raise HTTPException(status_code=422, detail="Username already exists")

    db_user = User.from_orm(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.patch(
    "/{user_id}/password/",
    response_model=UserResponse,
    dependencies=[AuthenticatedFreshUser],
)
async def update_user_password(
    *,
    user_id: int,
    session: Session = ActiveSession,
    request: Request,
    patch: UserPasswordPatch,
):
    # Query the content
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check the user can update the password
    current_user: User = get_current_user(request=request)
    if user.id != current_user.id and not current_user.superuser:
        raise HTTPException(
            status_code=403, detail="You can't update this user password"
        )

    if not patch.password == patch.password_confirm:
        raise HTTPException(status_code=400, detail="Passwords don't match")

    # Update the password
    user.password = get_password_hash(patch.password)

    # Commit the session
    session.commit()
    session.refresh(user)
    return user


@router.get(
    "/{user_id_or_username}/",
    response_model=UserResponse,
    dependencies=[AuthenticatedUser],
)
async def query_user(
    *, session: Session = ActiveSession, user_id_or_username: Union[str, int]
):
    user = session.query(User).where(
        or_(
            User.id == user_id_or_username,
            User.username == user_id_or_username,
        )
    )

    if not user.first():
        raise HTTPException(status_code=404, detail="User not found")
    return user.first()


@router.delete("/{user_id}/", dependencies=[AdminUser])
def delete_user(
    *, session: Session = ActiveSession, request: Request, user_id: int
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Content not found")
    # Check the user is not deleting himself
    current_user = get_current_user(request=request)
    if user.id == current_user.id:
        raise HTTPException(
            status_code=403, detail="You can't delete yourself"
        )
    session.delete(user)
    session.commit()
    return {"ok": True}
