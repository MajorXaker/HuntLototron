from ipaddress import IPv4Address, IPv6Address, ip_address

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse


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
