from logging import Logger

from ..lib.config import Config
from ..schemas.v1 import CNAMERecord
from ._base import CRUDBase


class CNAMECrud(CRUDBase):
    def __init__(self, config: Config, logger: Logger):
        super().__init__(schema=CNAMERecord, config=config, logger=logger)
