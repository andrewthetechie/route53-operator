"""Parent classes for V1 Record schemas

Set version, served, and storage on the BaseRecord class.

V1 is our current served schema. If we ever build a v2, we can change storage and stored
"""
from .._base import RecordBase
from .._base import RecordMutable


class V1RecordBase(RecordBase):
    """Base class for all V1 records"""

    _version: str = "v1"
    _served: bool = True
    _storage: bool = True


class V1RecordMutable(RecordMutable):
    """Base class for all Mutable V1 Record Schemas"""

    pass
