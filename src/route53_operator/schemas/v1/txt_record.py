from pydantic import constr
from pydantic import Field

from ...lib.partial import make_optional
from .._base import RecordBase
from .._base import RecordMutable


class TXTRecordMutable(RecordMutable):
    value: constr(strip_whitespace=True, max_length=255) = Field(
        description="TXT to setup for the record"
    )


class TXTRecord(RecordBase, TXTRecordMutable):
    """A TXT Record"""

    _record_type: str = "TXT"
    _namespace: tuple[str] = ("route53", "v1", "txt")


@make_optional
class TXTRecordUpdate(TXTRecordMutable):
    pass
