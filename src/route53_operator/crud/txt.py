from logging import Logger

from ..lib.config import Config
from ..schemas.v1 import TXTRecord
from ._base import CRUDBase

from aiobotocore.session import AioSession


class TXTCrud(CRUDBase):
    """A CRUD for TXT Records"""

    def __init__(self, config: Config, logger: Logger, aws_session: AioSession | None = None):
        super().__init__(schema=TXTRecord, config=config, logger=logger, aws_session=aws_session)
