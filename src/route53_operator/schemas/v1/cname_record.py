from pydantic import Field
from pydantic import validator

from .._base import is_valid_hostname
from .._base import Record


class CNAMERecord(Record):
    """A CNAME Record"""

    value: str = Field(description="Hostname to setup for the cname")

    @validator("value")
    def validate_value(cls, v):
        if not is_valid_hostname(v):
            raise ValueError("Invalid hostname")
        return v
