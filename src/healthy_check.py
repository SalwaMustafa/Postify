from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

health_router = APIRouter()

@health_router.get("/health")
async def welcome():
    
    return JSONResponse(
            status_code = status.HTTP_200_OK,
            content = {"signal": "api is healthy"}
        )