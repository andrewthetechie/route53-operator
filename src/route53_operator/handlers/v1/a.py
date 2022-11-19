from ... import kopf
from ... import kopf_registry
from ...crud.a import ACrud
from ...lib.config import get_config
from ...schemas.v1 import ARecord


@kopf.on.create(ARecord._plural, registry=kopf_registry)
async def create_a_record(spec, name, namespace, logger, **kwargs):
    crud = ACrud(config=get_config(), logger=logger)
    print("Creating a record")
    print(spec)
    obj = await crud.create(obj_in=ARecord(**spec))
    print("Done with Create")
    return {"status": "Success", "obj": obj}
