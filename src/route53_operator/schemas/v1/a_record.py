from ipaddress import IPv4Address
from ipaddress import IPv6Address

from pydantic import Field

from .._base import Record


class ARecord(Record):
    """An A Record"""

    values: list[IPv4Address | IPv6Address] = Field(
        description="List of IP addresses for the record"
    )
