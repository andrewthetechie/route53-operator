from pydantic import Field
from pydantic import validator

from ...lib.partial import make_optional
from .._base import is_valid_hostname
from .._base import RecordBase
from .._base import RecordMutable


class CNAMERecordMutable(RecordMutable):
    value: str = Field(description="CNAME to setup for the record")

    @validator("value")
    def validate_value(cls, v):
        if not is_valid_hostname(v):
            raise ValueError("Invalid hostname")
        return v


class CNAMERecord(RecordBase, CNAMERecordMutable):
    """A CNAME Record"""

    _record_type: str = "CNAME"
    _namespace: tuple[str] = ("route53", "v1", "cname")


@make_optional
class CNAMERecordUpdate(CNAMERecordMutable):
    pass
