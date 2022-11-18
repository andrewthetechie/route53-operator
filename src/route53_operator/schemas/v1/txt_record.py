from pydantic import constr
from pydantic import Field

from ...lib.partial import make_optional
from ._base import V1RecordBase
from ._base import V1RecordMutable


class TXTRecordMutable(V1RecordMutable):
    value: constr(strip_whitespace=True, max_length=255) = Field(
        description="TXT to setup for the record"
    )


class TXTRecord(V1RecordBase, TXTRecordMutable):
    """A TXT Record"""

    _record_type: str = "TXT"
    _namespace: tuple[str] = ("dns", "route53", "txt-records")
    _plural: str = "txt-records"
    _singular: str = "txt-record"
    _kind: str = "TXTRecord"
    _shortnames: list[str] = ["txt"]
    _served: bool = True
    _storage: bool = True
    value: constr(strip_whitespace=True, max_length=255) = Field(
        description="TXT to setup for the record"
    )


@make_optional
class TXTRecordUpdate(TXTRecordMutable):
    pass
