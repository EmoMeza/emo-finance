from fastapi import APIRouter
from app.api.v1.endpoints import auth, users

api_router = APIRouter()

# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])


@api_router.get("/status")
async def api_status():
    return {"status": "API v1 is running"}
