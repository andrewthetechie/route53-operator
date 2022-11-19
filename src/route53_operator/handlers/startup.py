from .. import kopf
from .. import kopf_registry


@kopf.on.startup(registry=kopf_registry)
async def startup_fn(logger, **kwargs):
    logger.info("Starting up")
    print("Starting up")
