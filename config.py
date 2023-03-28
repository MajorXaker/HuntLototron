import os

from dynaconf import Dynaconf

settings = Dynaconf(
    env="development",
    environments=True,
    default_settings_paths=["settings.toml", ".secrets.toml", ".secrets.py"],
    ROOT_PATH_FOR_DYNACONF=os.path.abspath(os.getcwd()),
)
