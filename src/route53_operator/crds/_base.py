from typing import Any
from typing import TypeVar

from pydantic import BaseModel

from ..schemas._base import RecordBase  # noqa: F401

RecordBaseT = TypeVar("RecordBase")


def get_crd_properties(
    schema: RecordBaseT, remove_fields: tuple[str] = ()
) -> dict[str, Any]:
    strip_from_schema = ("title", "description")
    to_return = {}
    for key, value in schema.schema()["properties"].items():
        if key in remove_fields:
            continue

        for stripped_key in strip_from_schema:
            if stripped_key in value:
                del value[stripped_key]
        to_return[key] = value
    return to_return


class CRDModel(BaseModel):
    def to_crd(self):
        return self.dict()


class CRDStatus(CRDModel):
    preserve_unknown_fields: bool = True
    messages: list[str | None] = []

    def to_crd(self):
        return {
            "type": "object",
            "x-kubernetes-preserve-unknown-fields": self.preserve_unknown_fields,
            "properties": get_crd_properties(
                self, remove_fields=("preserve_unknown_fields")
            ),
        }


class CRDPrinterColumns(CRDModel):
    name: str
    type: str
    description: str = ""
    json_path: str

    def to_crd(self):
        this_dict = self.dict()
        this_dict["jsonPath"] = this_dict.pop("json_path")
        return this_dict


class CRDVersion(CRDModel):
    name: str
    served: bool
    storage: bool
    crd_schema: RecordBaseT
    status: CRDStatus
    additional_printer_columns: list[CRDPrinterColumns] = []

    def to_crd(self):
        to_return = {
            "name": self.name,
            "served": self.served,
            "storage": self.storage,
            "schema": {
                "openAPIV3Schema": {
                    "type": "object",
                    "properties": {
                        "spec": {
                            "type": "object",
                            "properties": get_crd_properties(self.crd_schema),
                        },
                        "status": self.status.to_crd(),
                    },
                }
            },
        }
        if len(self.additional_printer_columns) > 0:
            to_return["additionalPrinterColumns"] = [
                column.to_crd() for column in self.additional_printer_columns
            ]
        return to_return


class CRDNames(CRDModel):
    plural: str
    singular: str
    kind: str
    short_names: list[str]

    def to_crd(self):
        dict = self.dict()
        dict["shortNames"] = dict.pop("short_names")
        return dict


class CRDSpec(CRDModel):
    group: str
    versions: list[CRDVersion]
    scope: str = "Namespaced"
    names: CRDNames

    def to_crd(self):
        return {
            "group": self.group,
            "versions": [version.to_crd() for version in self.versions],
            "scope": self.scope,
            "names": self.names.to_crd(),
        }


class CRDMetadata(CRDModel):
    name: str
    labels: list[str | None] = []

    def to_crd(self) -> dict[str, str | list[str | None]]:
        to_return = {
            "name": self.name,
        }
        if len(self.labels) > 0:
            to_return["labels"] = self.labels
        return to_return


class CRDBase(CRDModel):
    api_version: str = "apiextensions.k8s.io/v1"
    kind: str = "CustomResourceDefinition"
    metadata: CRDMetadata
    spec: CRDSpec

    def to_crd(self) -> dict[str, Any]:
        return {
            "apiVersion": self.api_version,
            "kind": self.kind,
            "metadata": self.metadata.to_crd(),
            "spec": self.spec.to_crd(),
        }
