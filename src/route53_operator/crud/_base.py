from datetime import datetime
from logging import Logger
from typing import Generic
from typing import TypeVar

from aiobotocore.session import AioSession
from pydantic import BaseModel

from ..exceptions import RecordNotFoundError
from ..lib.aws import get_session
from ..lib.config import Config
from ..schemas._base import RecordBase

CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
SchemaType = TypeVar("SchemaType", bound=BaseModel)
T = TypeVar("T", bound=RecordBase)


class CRUDBase(Generic[SchemaType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, schema: type[SchemaType], config: Config, logger: Logger):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        """
        self.schema = schema
        self._config = config
        self._logger = logger

    async def get(
        self,
        *,
        hosted_zone_id: str,
        name: str,
        aws_session: AioSession | None = None,
    ) -> list[SchemaType] | None:
        if aws_session is None:
            aws_session = get_session(self._config)

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53.html#Route53.Client.list_resource_record_sets
        async with aws_session.create_client(
            "route53", **self._config.aws_client_kwargs
        ) as client:
            response = await client.list_resource_record_sets(
                HostedZoneId=hosted_zone_id,
                StartRecordName=name,
                StartRecordType=self.schema._record_type,
                MaxItems="1",
            )
        record_sets = response.get("ResourceRecordSets", [])
        if len(record_sets) == 0:
            raise RecordNotFoundError("No records found")
        if (
            record_sets[0].get("Name", "") != name
            or record_sets[0].get("Type", "") != self.schema._record_type
        ):
            raise RecordNotFoundError("No records found")

        return self.schema.from_recordset(record_sets[0])

    async def create(
        self,
        *,
        obj_in: CreateSchemaType | SchemaType,
        aws_session: AioSession | None = None,
    ) -> SchemaType:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53.html#Route53.Client.change_resource_record_sets
        if aws_session is None:
            aws_session = get_session(self._config)
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
            "ResourceRecords": [{"Value": obj_in.value}],
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
        obj_current: SchemaType,
        obj_new: UpdateSchemaType | SchemaType,
        aws_session: AioSession | None = None,
    ) -> SchemaType:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53.html#Route53.Client.change_resource_record_sets
        if aws_session is None:
            aws_session = get_session(self._config)
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
            resource_record_set["ResourceRecords"] = [{"Value": new_value}]
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

    async def remove(
        self,
        *,
        hosted_zone_id: str,
        name: str,
        aws_session: AioSession | None = None,
    ) -> None:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53.html#Route53.Client.change_resource_record_sets
        if aws_session is None:
            aws_session = get_session(self._config)
        change_type = "DELETE"
        self._logger.debug(
            "Deleting record %s type %s in %s", name, type, hosted_zone_id
        )
        comment = f"route53-operator deleting {name} {self.schema._record_type} in {hosted_zone_id}"
        resource_record_set = {
            "Name": name,
            "Type": self.schema._record_type,
        }
        result = await self._change_record_set(
            aws_session=aws_session,
            hosted_zone_id=hosted_zone_id,
            change_type=change_type,
            resource_record_set=resource_record_set,
            comment=comment,
        )
        self._logger.debug(result)
        return

    async def _change_record_set(
        self,
        aws_session: AioSession,
        hosted_zone_id: str,
        change_type: str,
        resource_record_set: dict[str, str | bool | dict[str, str | bool]],
        comment: str = "",
    ) -> dict[str, str | datetime]:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53.html#Route53.Client.change_resource_record_sets
        async with aws_session.create_client(
            "route53", **self._config.aws_client_kwargs
        ) as client:
            response = await client.change_resource_record_sets(
                HostedZoneId=hosted_zone_id,
                ChangeBatch={
                    "Comment": comment,
                    "Changes": [
                        {
                            "Action": change_type,
                            "ResourceRecordSet": resource_record_set,
                        },
                    ],
                },
            )
        return response["ChangeInfo"]
