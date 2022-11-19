from .._base import RecordBase
from .._base import RecordMutable


class V1RecordBase(RecordBase):
    _version: str = "v1"
    _served: bool = True
    _storage: bool = True


class V1RecordMutable(RecordMutable):
    pass
