import re
from typing import Any

from pydantic import BaseModel
from pydantic import Field
from pydantic import validator


def is_valid_hostname(hostname):
    if len(hostname) > 255:
        return False
    if hostname[-1] == ".":
        hostname = hostname[:-1]  # strip exactly one dot from the right, if present
    allowed = re.compile(r"(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


class RecordMutable(BaseModel):
    ttl: int = Field(default=60, description="TTL for the record")
    value: str = Field(description="Value for this record")


class RecordBase(RecordMutable):
    _record_type: str = Field(None, description="The type of record")
    _namespace: list[str] = Field(
        None, description="The namespace for this record, used with the handlers"
    )

    hosted_zone_id: str = Field(description="Route53 Hosted zone ID")
    name: str = Field(description="Name of the record")

    @validator("name")
    def validate_name(cls, v):
        if not is_valid_hostname(v):
            raise ValueError("Invalid hostname")
        return v

    @classmethod
    def from_recordset(
        cls, hosted_zone_id: str, record_set: dict[str, Any]
    ) -> "RecordBase":
        return cls(
            hosted_zone_id=hosted_zone_id,
            ttl=record_set["TTL"],
            name=record_set["Name"],
            value=record_set["ResourceRecords"][0]["Value"],
        )
