from ..schemas.v1 import ARecord as V1ARecord
from ._base import CRDBase
from ._base import CRDMetadata
from ._base import CRDNames
from ._base import CRDSpec
from ._base import CRDStatus
from ._base import CRDVersion


class ARecordCRD(CRDBase):
    metadata: CRDMetadata = CRDMetadata(name=".".join(reversed(V1ARecord._namespace)))
    spec: CRDSpec = CRDSpec(
        group=".".join(tuple(reversed(V1ARecord._namespace))[-2:]),
        versions=[
            CRDVersion(
                name="v1",
                served=True,
                storage=True,
                crd_schema=V1ARecord,
                status=CRDStatus(),
            ),
        ],
        names=CRDNames(
            plural=V1ARecord._plural,
            singular=V1ARecord._singular,
            kind=V1ARecord._kind,
            shortnames=V1ARecord._shortnames,
        ),
    )
