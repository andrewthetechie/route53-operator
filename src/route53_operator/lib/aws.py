"""Methods related to AWS"""
from functools import lru_cache

from aiobotocore.session import AioSession
from aiobotocore.session import get_session as aiobotocore_get_session


@lru_cache
def get_session() -> AioSession:
    """Get an aiobotocore session, used with an LRU Cache to return the same session every time its called"""
    return aiobotocore_get_session()
