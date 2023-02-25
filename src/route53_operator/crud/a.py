from logging import Logger

from aiobotocore.session import AioSession

from ..lib.config import Config
from ..schemas.v1 import ARecord
from ..schemas.v1 import ARecordUpdate
from ._base import CRUDBase


class ACrud(CRUDBase):
    """A crud to manage A records""",

    def __init__(self, config: Config, logger: Logger, aws_session: AioSession | None = None):
        super().__init__(schema=ARecord, config=config, logger=logger, aws_session=aws_session)

    async def update(
        self,
        *,
        record_current: ARecord,
        record_new: ARecordUpdate,
    ) -> ARecord:
        """
        Update an A Record

        Args:
            record_current (SchemaType): The current record
            record_update (UpdateSchemaType | SchemaType): The updates to the record

        Returns:
            ARecord: A pydantic model of the Route53 A Record
        """
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53.html#Route53.Client.change_resource_record_sets
        change_type = "UPSERT"
        self._logger.debug(
            "Upserting record %s type %s in %s",
            record_current.name,
            self.schema._record_type,
            record_current.hosted_zone_id,
        )
        comment = (
            f"route53-operator upserting {record_current.name}"
            f"{self.schema._record_type} in {record_current.hosted_zone_id}"
        )
        resource_record_set = {
            "Name": record_current.name,
            "Type": self.schema._record_type,
        }
        new_ttl = getattr(record_new, "ttl", None)
        if new_ttl is not None:
            resource_record_set["TTL"] = new_ttl
        new_value = getattr(record_new, "value", None)
        if new_value is not None:
            resource_record_set["ResourceRecords"] = [{"Value": value} for value in new_value]
        result = await self._change_record_set(
            hosted_zone_id=record_current.hosted_zone_id,
            change_type=change_type,
            resource_record_set=resource_record_set,
            comment=comment,
        )
        self._logger.debug(result)
        return await self.get(
            hosted_zone_id=record_current.hosted_zone_id,
            name=record_current.name,
        )
