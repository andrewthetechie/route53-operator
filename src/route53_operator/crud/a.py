from logging import Logger

from aiobotocore.session import AioSession
from aiobotocore.session import get_session

from ..lib.config import Config
from ..schemas.v1 import ARecord
from ..schemas.v1 import ARecordUpdate
from ._base import CRUDBase


class ACrud(CRUDBase):
    def __init__(self, config: Config, logger: Logger):
        super().__init__(schema=ARecord, config=config, logger=logger)

    async def create(
        self,
        *,
        obj_in: ARecord,
        aws_session: AioSession | None = None,
    ) -> ARecord:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53.html#Route53.Client.change_resource_record_sets
        if aws_session is None:
            aws_session = get_session()
        change_type = "CREATE"
        self._logger.debug(
            "Creating record %s type %s in %s",
            obj_in.name,
            self.schema._record_type,
            obj_in.hosted_zone_id,
        )
        comment = f"route53-operator creating {obj_in.name} {self.schema._record_type} in {obj_in.hosted_zone_id}"
        resource_record_set = {
            "Name": obj_in.name,
            "Type": self.schema._record_type,
            "TTL": obj_in.ttl,
            "ResourceRecords": [{"Value": value} for value in obj_in.value],
        }
        result = await self._change_record_set(
            aws_session=aws_session,
            hosted_zone_id=obj_in.hosted_zone_id,
            change_type=change_type,
            resource_record_set=resource_record_set,
            comment=comment,
        )
        self._logger.debug(result)
        return await self.get(
            hosted_zone_id=obj_in.hosted_zone_id,
            name=obj_in.name,
            aws_session=aws_session,
        )

    async def update(
        self,
        *,
        obj_current: ARecord,
        obj_new: ARecordUpdate,
        aws_session: AioSession | None = None,
    ) -> ARecord:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53.html#Route53.Client.change_resource_record_sets
        if aws_session is None:
            aws_session = get_session()
        change_type = "UPSERT"
        self._logger.debug(
            "Upserting record %s type %s in %s",
            obj_current.name,
            self.schema._record_type,
            obj_current.hosted_zone_id,
        )
        comment = f"route53-operator upserting {obj_current.name} {self.schema._record_type} in {obj_current.hosted_zone_id}"
        resource_record_set = {
            "Name": obj_current.name,
            "Type": self.schema._record_type,
        }
        new_ttl = getattr(obj_new, "ttl", None)
        if new_ttl is not None:
            resource_record_set["TTL"] = new_ttl
        new_value = getattr(obj_new, "value", None)
        if new_value is not None:
            resource_record_set["ResourceRecords"] = [
                {"Value": value} for value in new_value
            ]
        result = await self._change_record_set(
            aws_session=aws_session,
            hosted_zone_id=obj_current.hosted_zone_id,
            change_type=change_type,
            resource_record_set=resource_record_set,
            comment=comment,
        )
        self._logger.debug(result)
        return await self.get(
            hosted_zone_id=obj_current.hosted_zone_id,
            name=obj_current.name,
            aws_session=aws_session,
        )
