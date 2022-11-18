from ... import kopf
from ... import kopf_registry
from ...crud.a import ACrud
from ...lib.config import get_config
from ...schemas.v1 import ARecord


@kopf.on.create(ARecord._plural, registry=kopf_registry)
async def create_a_record(body, logger, patch, **kwargs):
    crud = ACrud(config=get_config(), logger=logger)
    obj = await crud.create(obj_in=ARecord(**body))
    patch.obj = obj.dict()
    return "Success"
