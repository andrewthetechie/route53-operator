import asyncio

import uvloop

from . import kopf


def cli(args=None):
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    kopf.run()
