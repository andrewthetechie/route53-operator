from pydantic import constr
from pydantic import Field

from .._base import Record


class TXTRecord(Record):
    """A TXT Record"""

    value: constr(strip_whitespace=True, max_length=255) = Field(
        description="TXT to setup for the record"
    )
