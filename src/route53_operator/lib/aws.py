from functools import lru_cache

from aiobotocore.session import AioSession
from botocore.session import get_session as aiobotocore_get_session


@lru_cache
def get_session() -> AioSession:
    return aiobotocore_get_session()
