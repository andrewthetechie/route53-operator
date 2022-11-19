"""
CRUDs are objects that can create, update, delete and get Route53 record objects from the AWS API

CRUDs are used by handlers to translate k8s requests into AWS API changes.
"""
from .a import ACrud
from .cname import CNAMECrud
from .txt import TXTCrud

__all__ = ["ACrud", "CNAMECrud", "TXTCrud"]
