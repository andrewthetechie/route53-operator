"""This is our poetry entrypoint, run with r53operator. It loads the kopf handlers and registry and starts the kopf operator"""
import asyncio
import logging

import uvloop

from . import handlers  # noqa: F401
from . import kopf
from . import kopf_registry


def cli(args=None):
    # TODO: Figure out how we can pass sysargv or env vars in to configure kopf
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    settings = kopf.OperatorSettings()
    settings.posting.level = logging.DEBUG
    kopf.run(registry=kopf_registry, namespace="default", settings=settings)


if __name__ == "__main__":
    cli()
