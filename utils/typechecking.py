from beartype import beartype

from config import settings


def typechecked(func):
    if settings.ENV_FOR_DYNACONF in [
        "production"
        # settings.DJANGO_ENV_BETA,
        # TODO verify deployments
    ]:
        # disabled for PROD and BETA environments
        return func

    return beartype(func)
