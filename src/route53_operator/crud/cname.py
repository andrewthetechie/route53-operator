from logging import Logger

from ..lib.config import Config
from ..schemas.v1 import CNAMERecord
from ._base import CRUDBase

from aiobotocore.session import AioSession


class CNAMECrud(CRUDBase):
    """
    A CRUD for CNAME Records
    """

    def __init__(self, config: Config, logger: Logger, aws_session: AioSession | None = None):
        super().__init__(schema=CNAMERecord, config=config, logger=logger, aws_session=aws_session)
