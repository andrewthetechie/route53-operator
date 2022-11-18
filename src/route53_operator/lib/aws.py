from functools import lru_cache

from aiobotocore.session import AioSession
from botocore.session import get_session as aiobotocore_get_session

from .config import Config
from .config import get_config


@lru_cache
def get_session(config: Config = None) -> AioSession:
    if config is None:
        config = get_config()
    return aiobotocore_get_session(**config.aws_session_kwargs)
