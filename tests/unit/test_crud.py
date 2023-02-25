"""Test the CRUDs from src/route53_operator/crud"""
import pytest
from route53_operator.schemas.v1 import ARecord
from logging import getLogger


LOGGER = getLogger(__name__)


@pytest.mark.asyncio
async def test_a_crud_create(ls_zone):
    """Test the A CRUD create method"""
    from route53_operator.crud.a import ACrud

    this_crud = ACrud(aws_session=ls_zone["session"], config=ls_zone["config"], logger=LOGGER)
    this_record = ARecord(hosted_zone_id=ls_zone["zone_id"], name=f"test.{ls_zone['name']}", value=["10.10.0.1"])
    result = await this_crud.create(record_in=this_record)
    assert result.hosted_zone_id == ls_zone["zone_id"]
    assert result.name == f"test.{ls_zone['name']}"
    assert str(result.value[0]) == "10.10.0.1"
