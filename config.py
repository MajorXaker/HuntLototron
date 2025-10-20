import logging
import os
import pathlib

import sentry_sdk
from dynaconf import Dynaconf

_configs_path = pathlib.Path(os.getcwd())
if not _configs_path.joinpath("settings.toml").exists():
    # launch from root directory (not app)
    _configs_path = _configs_path.joinpath("app")

settings = Dynaconf(
    env="default",
    environments=True,
    settings_files=["settings.toml", ".secrets.toml"],
    ROOT_PATH_FOR_DYNACONF=os.getcwd(),
)

log = logging.getLogger(__name__)


# if settings.LOG_TO_SENTRY:
#     sentry_sdk.init(
#         dsn=settings.SENTRY_DSN,
#         sample_rate=1.0,
#         traces_sample_rate=0.0,
#         send_default_pii=True,
#         release=settings.VERSION,
#     )
