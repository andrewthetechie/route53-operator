import os
from functools import lru_cache

from pydantic import BaseSettings


class Config(BaseSettings):
    """Configuration for the operator."""

    ...

    class Config:
        """Pydantic base setting config"""

        env_prefix = os.environ.get("CONFIG_PREFIX", "")

    def __hash__(self):
        return hash(self.json())


@lru_cache
def get_config() -> Config:
    """Gets a config object from the env and returns it
    LRU cached so subsequent calls don't have to do the env lookups

    Returns:
        Config -- config object
    """
    return Config()
