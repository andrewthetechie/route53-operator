from .a import ARecordCRD  # noqa: F401
from .cname import CNAMERecordCRD  # noqa: F401
from .txt import TXTRecordCRD  # noqa: F401

CRDS = [ARecordCRD, CNAMERecordCRD, TXTRecordCRD]
