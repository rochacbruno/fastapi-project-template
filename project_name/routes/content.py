from typing import List, Union

from fastapi import APIRouter, Request
from fastapi.exceptions import HTTPException
from sqlmodel import Session, or_, select

from ..db import ActiveSession
from ..models.content import Content, ContentIncoming, ContentResponse
from ..security import AuthenticatedUser, User, get_current_user

router = APIRouter()


@router.get("/", response_model=List[ContentResponse])
async def list_contents(*, session: Session = ActiveSession):
    contents = session.exec(select(Content)).all()
    return contents


@router.get("/{id_or_slug}/", response_model=ContentResponse)
async def query_content(
    *, id_or_slug: Union[str, int], session: Session = ActiveSession
):
    content = session.query(Content).where(
        or_(
            Content.id == id_or_slug,
            Content.slug == id_or_slug,
        )
    )
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content.first()


@router.post(
    "/", response_model=ContentResponse, dependencies=[AuthenticatedUser]
)
async def create_content(
    *,
    session: Session = ActiveSession,
    request: Request,
    content: ContentIncoming,
):
    # set the ownsership of the content to the current user
    db_content = Content.from_orm(content)
    user: User = get_current_user(request=request)
    db_content.user_id = user.id
    session.add(db_content)
    session.commit()
    session.refresh(db_content)
    return db_content


@router.patch(
    "/{content_id}/",
    response_model=ContentResponse,
    dependencies=[AuthenticatedUser],
)
async def update_content(
    *,
    content_id: int,
    session: Session = ActiveSession,
    request: Request,
    patch: ContentIncoming,
):
    # Query the content
    content = session.get(Content, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # Check the user owns the content
    current_user: User = get_current_user(request=request)
    if content.user_id != current_user.id and not current_user.superuser:
        raise HTTPException(
            status_code=403, detail="You don't own this content"
        )

    # Update the content
    patch_data = patch.dict(exclude_unset=True)
    for key, value in patch_data.items():
        setattr(content, key, value)

    # Commit the session
    session.commit()
    session.refresh(content)
    return content


@router.delete("/{content_id}/", dependencies=[AuthenticatedUser])
def delete_content(
    *, session: Session = ActiveSession, request: Request, content_id: int
):

    content = session.get(Content, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    # Check the user owns the content
    current_user = get_current_user(request=request)
    if content.user_id != current_user.id and not current_user.superuser:
        raise HTTPException(
            status_code=403, detail="You don't own this content"
        )
    session.delete(content)
    session.commit()
    return {"ok": True}
