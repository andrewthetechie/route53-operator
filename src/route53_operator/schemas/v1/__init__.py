from .a_record import ARecord
from .a_record import ARecordUpdate
from .cname_record import CNAMERecord
from .cname_record import CNAMERecordUpdate
from .txt_record import TXTRecord
from .txt_record import TXTRecordUpdate

__all__ = [
    "ARecord",
    "CNAMERecord",
    "TXTRecord",
    "ARecordUpdate",
    "CNAMERecordUpdate",
    "TXTRecordUpdate",
]
