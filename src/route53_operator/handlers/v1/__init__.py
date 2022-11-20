"""
v1 handlers handle the v1 schema objects

All V1 handlers need to be imported into this module and added to __all__ so that they are loaded by the main module
when the operator starts up

"""
from .a import create_a_record

__all__ = ["create_a_record"]
