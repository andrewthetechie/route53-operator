from ipaddress import IPv4Address
from typing import Any

from pydantic import Field

from ...lib.partial import make_optional
from .._base import RecordBase
from .._base import RecordMutable


class ARecordMutable(RecordMutable):
    value: list[IPv4Address] = Field(description="List of IP addresses for the record")


class ARecord(RecordBase, ARecordMutable):
    """An A Record"""

    _record_type: str = "A"
    _namespace: tuple[str] = ("route53", "v1", "a")

    @classmethod
    def from_recordset(
        cls, hosted_zone_id: str, record_set: dict[str, Any]
    ) -> "ARecord":
        return cls(
            hosted_zone_id=hosted_zone_id,
            ttl=record_set["TTL"],
            name=record_set["Name"],
            value=[ip["Value"] for ip in record_set["ResourceRecords"]],
        )


@make_optional
class ARecordUpdate(ARecordMutable):
    pass
