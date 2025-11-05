from fastapi import APIRouter, FastAPI

router = APIRouter()

@router.get("/auth/")
async def get_user():
    return {"user": "authenticated"}