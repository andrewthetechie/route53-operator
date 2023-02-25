"""Base schemas are parent classes for other Record schemas"""
import re
from typing import Any

from pydantic import BaseModel
from pydantic import conint
from pydantic import Field
from pydantic import validator


def is_valid_hostname(hostname):
    """Uses regex to validate a hostname"""
    if len(hostname) > 255:
        return False
    if hostname[-1] == ".":
        hostname = hostname[:-1]  # strip exactly one dot from the right, if present
    allowed = re.compile(r"(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


class RecordMutable(BaseModel):
    """Mutable fields for a record

    These are the fields that can be changed after a record is created.
    """

    ttl: conint(ge=0, le=2147483647) = Field(default=60, description="TTL for the record")
    value: str = Field(description="Value for this record")


class RecordBase(RecordMutable):
    """
    Base class for all record schemas
    """

    _record_type: str = Field(None, description="The type of record")
    _version: str = Field(None, description="The version of the record")
    _namespace: list[str] = Field(None, description="The namespace for this record, used with the handlers")
    _served: bool = Field(False, description="Whether this record is served by the operator")
    _storage: bool = Field(
        False,
        description="One and only one version must be marked as the storage version.",
    )
    _plural: str = Field(..., description="The plural name for this record")
    _singular: str = Field(..., description="The singular name for this record")
    _kind: str = Field(..., description="The kind for this record")
    _shortnames: list[str] = Field(..., description="The shortnames for this record")

    hosted_zone_id: str = Field(description="Route53 Hosted zone ID")
    name: str = Field(description="Name of the record")

    @validator("name")
    def validate_name(cls, v):
        """Validates that the record name is a valid hostname"""
        if not is_valid_hostname(v):
            raise ValueError("Invalid hostname")
        return v

    @classmethod
    def from_recordset(cls, hosted_zone_id: str, record_set: dict[str, Any]) -> "RecordBase":
        """Convert a record set from the AWS API to a RecordObject"""
        return cls(
            hosted_zone_id=hosted_zone_id,
            ttl=record_set["TTL"],
            name=record_set["Name"],
            value=record_set["ResourceRecords"][0]["Value"],
        )

    @property
    def recordset(self) -> dict[str, str | int | list[dict[str, str]]]:
        """Express this Record object as an AWS Recordset dictionary"""
        return {
            "Name": self.name,
            "Type": self._record_type,
            "TTL": self.ttl,
            "ResourceRecords": self.resource_records,
        }

    @property
    def resource_records(self) -> list[dict[str, str]]:
        """The ResourceRecords (from RecordSet) for this record"""
        return [{"Value": self.value}]
