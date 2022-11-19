"""Schemas for A Records"""
from ipaddress import IPv4Address
from typing import Any

from pydantic import Field

from ...lib.partial import make_optional
from ._base import V1RecordBase
from ._base import V1RecordMutable


class ARecordMutable(V1RecordMutable):
    """The mutable fields for an A Record"""

    value: list[IPv4Address] = Field(description="List of IP addresses for the record")


class ARecord(V1RecordBase, ARecordMutable):
    """An A Record"""

    _record_type: str = "A"
    _namespace: tuple[str] = ("dns", "route53", "a-records")
    _plural: str = "a-records"
    _singular: str = "a-record"
    _kind: str = "ARecord"
    _shortnames: list[str] = ["a"]
    value: list[IPv4Address] = Field(description="List of IP addresses for the record")

    @classmethod
    def from_recordset(
        cls, hosted_zone_id: str, record_set: dict[str, Any]
    ) -> "ARecord":
        """Convert a record set from the AWS API to aa A Record"""
        return cls(
            hosted_zone_id=hosted_zone_id,
            ttl=record_set["TTL"],
            name=record_set["Name"],
            value=[ip["Value"] for ip in record_set["ResourceRecords"]],
        )

    @property
    def resource_records(self) -> list[dict[str, str]]:
        """The ResourceRecords (from RecordSet) for this A record"""
        return [{"Value": str(value)} for value in self.value]


@make_optional
class ARecordUpdate(ARecordMutable):
    """The schema used when updating an A Record, makes all Mutable fields optional"""

    pass
