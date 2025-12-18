from fastapi import APIRouter

api_router = APIRouter()


@api_router.get("/status")
async def api_status():
    return {"status": "API v1 is running"}
