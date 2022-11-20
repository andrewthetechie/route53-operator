"""Handlers for A Records"""
from typing import Any
from typing import Logger

from ... import kopf
from ... import kopf_registry
from ...crud.a import ACrud
from ...lib.config import get_config
from ...schemas.v1 import ARecord


@kopf.on.create(ARecord._plural, registry=kopf_registry)
async def create_a_record(
    spec: dict[str, Any], name: str, namespace: str, logger: Logger, **kwargs
) -> dict[str, Any]:
    """
    Handle an A record object being created

    Args:
        spec (dict[str, Any]): The spec of the A record
        name (str): Name of the A record
        namespace (str): Namespace of the A record
        logger (Logger): Python Logger

    Returns:
        dict[str, Any]: _description_
    """
    crud = ACrud(config=get_config(), logger=logger)
    print("Creating a record")
    print(spec)
    obj = await crud.create(obj_in=ARecord(**spec))
    print("Done with Create")
    return {"status": "Success", "obj": obj}
