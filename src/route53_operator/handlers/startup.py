"""Handlers that are run on startup of the operator"""
from logging import Logger

from .. import kopf
from .. import kopf_registry


@kopf.on.startup(registry=kopf_registry)
async def startup_fn(logger: Logger, **kwargs) -> None:
    """
    This is a handler that is run on startup of the operator. It is used to
    log a message that the operator has started.

    Args:
        logger (Logger): python logger
    """
    logger.info("Starting up")
