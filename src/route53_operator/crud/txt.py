from logging import Logger

from ..lib.config import Config
from ..schemas.v1 import TXTRecord
from ._base import CRUDBase


class TXTCrud(CRUDBase):
    """A CRUD for TXT Records"""

    def __init__(self, config: Config, logger: Logger):
        super().__init__(schema=TXTRecord, config=config, logger=logger)
