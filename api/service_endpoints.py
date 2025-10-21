from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio.session import AsyncSession


service_router = APIRouter()


@service_router.post(
    "/",
)
async def process_request(
    request: Request,
    ip: str,
    username: str = Depends(verify_credentials),
    db: AsyncSession = get_session_dep,
):
    pass
