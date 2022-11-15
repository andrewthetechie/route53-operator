from ..schemas.v1 import CNAMERecord as V1ACNAMERecord
from ._base import CRDBase
from ._base import CRDMetadata
from ._base import CRDNames
from ._base import CRDSpec
from ._base import CRDStatus
from ._base import CRDVersion


class CNAMERecordCRD(CRDBase):
    metadata: CRDMetadata = CRDMetadata(
        name=".".join(reversed(V1ACNAMERecord._namespace))
    )
    spec: CRDSpec = CRDSpec(
        group=".".join(tuple(reversed(V1ACNAMERecord._namespace))[-2:]),
        versions=[
            CRDVersion(
                name="v1",
                served=True,
                storage=True,
                crd_schema=V1ACNAMERecord,
                status=CRDStatus(),
            ),
        ],
        names=CRDNames(
            plural=V1ACNAMERecord._plural,
            singular=V1ACNAMERecord._singular,
            kind=V1ACNAMERecord._kind,
            shortnames=V1ACNAMERecord._shortnames,
        ),
    )
