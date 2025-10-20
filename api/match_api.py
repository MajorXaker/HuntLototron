from ipaddress import IPv4Address, IPv6Address, ip_address

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse


match_router = APIRouter()


@ip_check_router.post(
    "/v1/internal/ip-info",
    response_model=IpData,
    responses={
        400: {
            "model": ErrorResponseSchema,
            "description": "Bad Request – Invalid IP address format.",
            "content": {
                "application/json": {"example": {"detail": "Invalid IP address format"}}
            },
        },
        401: {
            "model": ErrorResponseSchema,
            "description": "Unauthorized – Invalid authentication credentials.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid authentication credentials",
                    }
                }
            },
        },
        502: {
            "model": ErrorResponseSchema,
            "description": "Error on external resource (IP2Location, etc.).",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "External resource unavailable",
                    }
                }
            },
        },
    },
    summary="Process IP with Basic Auth",
    description="Accepts an IP string as a query param, checks it against internal "
    "database and external data providers, returns data of the IP address.\n"
    "This endpoint requires Basic Auth, and returns 200 or 400/401 for errors.",
)
async def process_request(
    request: Request,
    ip: str,
    username: str = Depends(verify_credentials),
    db: AsyncSession = get_session_dep,
):
    log.info(f"Received ip check request for '{ip}'")
    try:
        full_ip_address = _get_valid_ip(ip).exploded
    except InvalidIPAddressError:
        log.error("Incorrect IP address provided", extra={"ip": ip})
        return JSONResponse(status_code=400, content={"detail": "Invalid IP address"})

    stored_ip_data = await get_ip_data(session=db, ip_address=full_ip_address)

    if stored_ip_data:
        request.state.cache_hit = "hit"  # monitoring of cache rate
        return stored_ip_data

    try:
        raw_data = await fetch_raw_data(session=db, ip_address=full_ip_address)
    except InvalidIPAddressError:
        log.error("Incorrect IP address provided", extra={"ip": ip})
        return JSONResponse(status_code=400, content={"detail": "Invalid IP address"})
    except Missing3rdPartyKeyError:
        return JSONResponse(
            status_code=400,
            content={"detail": "API keys for 3rd party services are missing"},
        )

    if len(raw_data) == 0:
        log.error(
            "Failed to fetch data",
            extra={
                "ip": ip,
                "providers": [
                    provider.provider_name
                    for provider in await get_ip_data_provider_clients(session=db)
                ],
            },
        )
        return JSONResponse(
            status_code=502, content={"detail": "External resource unavailable"}
        )

    await store_raw_data(session=db, ip_address=full_ip_address, raw_data=raw_data)

    aggregated_data = await create_ip_data(session=db, raw_data=raw_data)

    log.info(f"Parsing '{ip}' success")
    request.state.cache_hit = "miss"  # monitoring of cache rate
    return aggregated_data


@typechecked
def _get_valid_ip(ip: str) -> IPv4Address | IPv6Address:
    try:
        validated_ip = ip_address(ip)
    except ValueError:  # incorrect IP address
        raise InvalidIPAddressError

    incorrect_ip_flags = [
        validated_ip.is_loopback,  # 127.0.0.1 ::1/128
        validated_ip.is_link_local,  # fe80::1 169.254.0.0
        validated_ip.is_multicast,  # ff00::/8
        validated_ip.is_private,  # fc00::5 192.168.0.100
        getattr(validated_ip, "is_site_local", False),  # non-existent for IPV4
    ]

    if any(incorrect_ip_flags):
        raise InvalidIPAddressError

    return validated_ip
