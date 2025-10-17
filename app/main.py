import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator, metrics
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse
from starlette_admin.contrib.sqla import Admin
from tracing_fastapi import setup_fastapi_tracing
from tracing_python import ForceSampleASGIMiddleware

import models.db_models as m
from api.admin.auth import AdminAuthProvider
from api.admin.ip_data_admin import IpDataAdmin
from api.admin.third_party_key_admin import ThirdPartyKeyAdmin
from api.admin.user_admin import UserAdmin
from api.ip_check import ip_check_router
from config import log, settings
from heartbeat import heartbeat_router
from infra.db.connection import persistent_engine
from infra.redis_connector import redis_client
from prometheus.custom_metrics import ip2location_response_metric, ip_info_cache_metrics



app = FastAPI(
    title=settings.APPNAME,
    version="0.0.1",
    docs_url="/openapi/swagger",
    redoc_url="/openapi/redoc",
    lifespan=lifespan,
)

app.add_middleware(ForceSampleASGIMiddleware)


app.include_router(heartbeat_router, prefix="")
app.include_router(ip_check_router, prefix="/api")

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
metrics_instrumentator.add(ip_info_cache_metrics())
metrics_instrumentator.add(lambda _: ip2location_response_metric)
metrics_instrumentator.instrument(app)
metrics_instrumentator.expose(app)

if "main.py" in sys.argv:
    # avoiding duplicate tracing launch
    setup_fastapi_tracing(app)

if settings.ENV_FOR_DYNACONF in ["default", "development"]:

    @app.get("/", include_in_schema=False)
    async def redirect_to_redoc():
        return RedirectResponse(url="/openapi/swagger", status_code=302)




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
