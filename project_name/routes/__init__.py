from fastapi import APIRouter

from .user import router as user_router

main_router = APIRouter()

main_router.include_router(user_router, prefix="/user", tags=["user"])


@main_router.get("/")
async def index():
    return {"message": "Hello World!"}
