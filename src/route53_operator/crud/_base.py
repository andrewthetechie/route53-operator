"""base CRUD class that implements the CRUD interface"""
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
    """
    CRUDBase can be used to implement a CRUD interface for any model.
    """

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
        aws_region: str = "us-east-1",
        aws_session: AioSession | None = None,
    ) -> SchemaType:
        """
        Get an AWS record by name and hosted zone id.

        Uses list_resource_record_sets to look up the record from the AWS API.

        Args:
            hosted_zone_id (str): The Route53 hosted zone id to search in
            name (str): Name of the DNS Record to get
            aws_region (str, optional): AWS Rregion. Defaults to "us-east-1".
            aws_session (AioSession | None, optional): An AIOSession object. Defaults to None.
                If None, will create a session

        Raises:
            RecordNotFoundError: Raised when the record is not found

        Returns:
            SchemaType: A pydantic model of the record
        """
        if aws_session is None:
            aws_session = get_session()

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53.html#Route53.Client.list_resource_record_sets
        async with aws_session.create_client(
            "route53", **self._config.aws_client_kwargs, region_name=aws_region
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
            record_sets[0].get("Name", "") != name + "."
            or record_sets[0].get("Type", "") != self.schema._record_type
        ):
            raise RecordNotFoundError("No records found")

        return self.schema.from_recordset(
            hosted_zone_id=hosted_zone_id, record_set=record_sets[0]
        )

    async def create(
        self,
        *,
        record_in: CreateSchemaType | SchemaType,
        aws_session: AioSession | None = None,
    ) -> SchemaType:
        """
        Create a new record Route53 record.

        Args:
            record_in (CreateSchemaType | SchemaType): The record to create
            aws_session (AioSession | None, optional): An AIOSession object. Defaults to None.
                If None, will create a session

        Returns:
            SchemaType: A pydantic model of the record
        """
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53.html#Route53.Client.change_resource_record_sets
        if aws_session is None:
            aws_session = get_session()
        change_type = "CREATE"
        self._logger.debug(
            "Creating record %s type %s in %s",
            record_in.name,
            self.schema._record_type,
            record_in.hosted_zone_id,
        )
        comment = f"route53-operator creating {record_in.name} {self.schema._record_type} in {record_in.hosted_zone_id}"
        resource_record_set = record_in.recordset
        result = await self._change_record_set(
            aws_session=aws_session,
            hosted_zone_id=record_in.hosted_zone_id,
            change_type=change_type,
            resource_record_set=resource_record_set,
            aws_region=record_in.region,
            comment=comment,
        )
        self._logger.debug(result)
        return await self.get(
            hosted_zone_id=record_in.hosted_zone_id,
            name=record_in.name,
            aws_region=record_in.region,
            aws_session=aws_session,
        )

    async def update(
        self,
        *,
        record_current: SchemaType,
        record_update: UpdateSchemaType | SchemaType,
        aws_session: AioSession | None = None,
    ) -> SchemaType:
        """
        Update a route53 record.

        Args:
            record_current (SchemaType): The current record
            record_update (UpdateSchemaType | SchemaType): The updates to the record
            aws_session (AioSession | None, optional): An AIOSession object. Defaults to None.
                If None, will create a session

        Returns:
            SchemaType: A pydantic model of the record
        """
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53.html#Route53.Client.change_resource_record_sets
        if aws_session is None:
            aws_session = get_session()
        change_type = "UPSERT"
        self._logger.debug(
            "Upserting record %s type %s in %s",
            record_current.name,
            self.schema._record_type,
            record_current.hosted_zone_id,
        )
        comment = (
            f"route53-operator upserting {record_current.name} "
            f"{self.schema._record_type} in {record_current.hosted_zone_id}"
        )
        resource_record_set = {
            "Name": record_current.name,
            "Type": self.schema._record_type,
        }
        new_ttl = getattr(record_update, "ttl", None)
        if new_ttl is not None:
            resource_record_set["TTL"] = new_ttl
        new_value = getattr(record_update, "value", None)
        if new_value is not None:
            resource_record_set["ResourceRecords"] = [{"Value": new_value}]
        result = await self._change_record_set(
            aws_session=aws_session,
            hosted_zone_id=record_current.hosted_zone_id,
            change_type=change_type,
            resource_record_set=resource_record_set,
            aws_region=record_current.region,
            comment=comment,
        )
        self._logger.debug(result)
        return await self.get(
            hosted_zone_id=record_current.hosted_zone_id,
            name=record_current.name,
            aws_region=record_current.region,
            aws_session=aws_session,
        )

    async def remove(
        self,
        *,
        record_in: SchemaType,
        aws_session: AioSession | None = None,
    ) -> None:
        """
        Remove a route53 record.

        Args:
            record_in (SchemaType): The record to remove
            aws_session (AioSession | None, optional): An AIOSession object. Defaults to None.
                If None, will create a session
        """
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53.html#Route53.Client.change_resource_record_sets
        if aws_session is None:
            aws_session = get_session()
        name = record_in.name
        hosted_zone_id = record_in.hosted_zone_id
        aws_region = record_in.region
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
            aws_region=aws_region,
        )
        self._logger.debug(result)
        return

    async def _change_record_set(
        self,
        aws_session: AioSession,
        hosted_zone_id: str,
        change_type: str,
        resource_record_set: dict[str, str | bool | dict[str, str | bool]],
        aws_region: str = "us-east-1",
        comment: str = "",
    ) -> dict[str, str | datetime]:
        """
        Uses botocore change_resource_record_sets to update a route53 record using the AWS API.

        Args:
            aws_session (AioSession): The Aiobotocore session to use with the AWS API
            hosted_zone_id (str): The Route53 hosted zone id
            change_type (str): The changetype, one of
            resource_record_set (dict[str, str  |  bool  |  dict[str, str  |  bool]]): _description_
            aws_region (str, optional): _description_. Defaults to "us-east-1".
            comment (str, optional): _description_. Defaults to "".

        Returns:
            dict[str, str | datetime]: the ChangeInfo from the AWS API
        """
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53.html#Route53.Client.change_resource_record_sets
        async with aws_session.create_client(
            "route53", **self._config.aws_client_kwargs, region_name=aws_region
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
