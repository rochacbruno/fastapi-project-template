from fastapi import APIRouter

from ..security import AuthenticatedUser, User, UserResponse

router = APIRouter()


@router.get("/profile", response_model=UserResponse)
async def my_profile(current_user: User = AuthenticatedUser):
    return current_user
