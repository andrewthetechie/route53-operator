"""Base CRD classes are parent classes that the CRD objects inherit from"""
from typing import Any
from typing import TypeVar

from pydantic import BaseModel

from ..schemas._base import RecordBase  # noqa: F401

RecordBaseT = TypeVar("RecordBase")


def get_crd_properties(
    schema: RecordBaseT, remove_fields: tuple[str] = ()
) -> dict[str, Any]:
    """
    Turns a schema into a CRD properties dict

    Args:
        schema (RecordBaseT): The schema to convert
        remove_fields (tuple[str], optional): Extra fields to remove. Defaults to ().

    Returns:
        dict[str, Any]: A CRD properties dict
    """
    # title and description are not used in a CRD
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
    """
    A parent class for all CRD objects
    """

    def to_crd(self) -> dict[str, Any]:
        """
        Turn the CRD model into a dictonary representation of a k8s CRD

        Returns:
            dict[str, Any]: CRD
        """
        return self.dict()


class CRDStatus(CRDModel):
    """
    CRD Status object
    """

    preserve_unknown_fields: bool = True
    messages: list[str | None] = []

    def to_crd(self) -> dict[str, Any]:
        """
        Turn the CRDStatus into a dictonary representation of a k8s CRD Status object

        Returns:
            dict[str, Any]: CRD Status
        """
        return {
            "type": "object",
            "x-kubernetes-preserve-unknown-fields": self.preserve_unknown_fields,
            "properties": get_crd_properties(
                self, remove_fields=("preserve_unknown_fields")
            ),
        }


class CRDPrinterColumns(CRDModel):
    """
    CRD Additional Printers object
    """

    name: str
    type: str
    description: str = ""
    json_path: str

    def to_crd(self) -> dict[str, Any]:
        """
        Turn the CRDPrinterColumns into a dictonary representation of a k8s CRD Additional Printers object

        Returns:
            dict[str, Any]: CRD Additional Printers
        """
        this_dict = self.dict()
        this_dict["jsonPath"] = this_dict.pop("json_path")
        return this_dict


class CRDVersion(CRDModel):
    """
    CRD Version object
    """

    name: str
    served: bool
    storage: bool
    crd_schema: RecordBaseT
    status: CRDStatus
    additional_printer_columns: list[CRDPrinterColumns] = []

    def to_crd(self) -> dict[str, Any]:
        """
        Turn the CRDVersion into a dictonary representation of a k8s CRD Version object

        Returns:
            dict[str, Any]: CRD Version
        """
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
    """
    CRD Names object
    """

    plural: str
    singular: str
    kind: str
    short_names: list[str]

    def to_crd(self) -> dict[str, Any]:
        """
        Turn the CRDNames into a dictonary representation of a k8s CRD Names object

        Returns:
            dict[str, Any]: CRD Names
        """
        dict = self.dict()
        dict["shortNames"] = dict.pop("short_names")
        return dict


class CRDSpec(CRDModel):
    """
    CRD Spec object
    """

    group: str
    versions: list[CRDVersion]
    scope: str = "Namespaced"
    names: CRDNames

    def to_crd(self) -> dict[str, Any]:
        """
        Turn the CRDSpec into a dictonary representation of a k8s CRD Spec object

        Returns:
            dict[str, Any]: CRD Spec
        """
        return {
            "group": self.group,
            "versions": [version.to_crd() for version in self.versions],
            "scope": self.scope,
            "names": self.names.to_crd(),
        }


class CRDMetadata(CRDModel):
    """
    CRD Metadata object
    """

    name: str
    labels: list[str | None] = []

    def to_crd(self) -> dict[str, str | list[str | None]]:
        """
        Turn the CRDMetadata into a dictonary representation of a k8s CRD Metadata object

        Returns:
            dict[str, str | list[str | None]]: CRD Metadata
        """
        to_return = {
            "name": self.name,
        }
        if len(self.labels) > 0:
            to_return["labels"] = self.labels
        return to_return


class CRDBase(CRDModel):
    """
    CRD Base is a parent that all CRD objects inherit from
    """

    api_version: str = "apiextensions.k8s.io/v1"
    kind: str = "CustomResourceDefinition"
    metadata: CRDMetadata
    spec: CRDSpec

    def to_crd(self) -> dict[str, Any]:
        """
        Trurn the CRD Pydantic object into a dictonary representation of a k8s CRD

        Returns:
            dict[str, Any]: CRD as a dict
        """
        return {
            "apiVersion": self.api_version,
            "kind": self.kind,
            "metadata": self.metadata.to_crd(),
            "spec": self.spec.to_crd(),
        }
