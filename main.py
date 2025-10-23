import uvicorn
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator, metrics
from starlette.responses import RedirectResponse

from api.router_ammo_types import ammo_type_router
from api.router_compounds import compound_router
from api.router_maps import map_router
from api.router_match import match_router
from api.router_players import player_router
from api.router_weapon_types import weapon_types_router
from api.router_weapons import weapons_router
from api.service_endpoints import service_router
from config import settings
from heartbeat import heartbeat_router


app = FastAPI(
    title=settings.APPNAME,
    version="0.0.1",
    docs_url="/openapi/swagger",
    redoc_url="/openapi/redoc",
)


app.include_router(heartbeat_router, prefix="")
app.include_router(match_router)
app.include_router(ammo_type_router)
app.include_router(weapon_types_router)
app.include_router(weapons_router)
app.include_router(map_router)
app.include_router(compound_router)
app.include_router(player_router)
app.include_router(service_router)

metrics_instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=[
        "/__heartbeat__",
        "/admin/*",
        "/metrics",
        "/openapi/*",
    ],
)
metrics_instrumentator.add(metrics.default())

metrics_instrumentator.instrument(app)
metrics_instrumentator.expose(app)


if settings.ENV_FOR_DYNACONF in ["default", "development"]:

    @app.get("/", include_in_schema=False)
    async def redirect_to_redoc():
        return RedirectResponse(url="/openapi/swagger", status_code=302)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
