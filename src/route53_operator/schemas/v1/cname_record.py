from pydantic import Field
from pydantic import validator

from ...lib.partial import make_optional
from .._base import is_valid_hostname
from ._base import V1RecordBase
from ._base import V1RecordMutable


class CNAMERecordMutable(V1RecordMutable):
    value: str = Field(description="CNAME to setup for the record")

    @validator("value")
    def validate_value(cls, v):
        if not is_valid_hostname(v):
            raise ValueError("Invalid hostname")
        return v


class CNAMERecord(V1RecordBase, CNAMERecordMutable):
    """A CNAME Record"""

    _record_type: str = "CNAME"
    _namespace: tuple[str] = ("dns", "route53", "cname-records")
    _plural: str = "cname-records"
    _singular: str = "cname-record"
    _kind: str = "CNAMERecord"
    _shortnames: list[str] = ["cname"]
    _served: bool = True
    _storage: bool = True
    value: str = Field(description="CNAME to setup for the record")

    @validator("value")
    def validate_value(cls, v):
        if not is_valid_hostname(v):
            raise ValueError("Invalid hostname")
        return v


@make_optional
class CNAMERecordUpdate(CNAMERecordMutable):
    pass
