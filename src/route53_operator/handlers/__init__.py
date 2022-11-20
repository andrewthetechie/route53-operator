"""
Handlers have to be registered with the kopf registry and imported into the main module

# https://kopf.readthedocs.io/en/stable/handlers/
"""
from . import v1
from .login import login_fn
from .startup import startup_fn

__all__ = ["startup_fn", "v1", "login_fn"]
