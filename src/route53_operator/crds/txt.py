from ..schemas.v1 import TXTRecord as TXTRecord
from ._base import CRDBase
from ._base import CRDMetadata
from ._base import CRDNames
from ._base import CRDSpec
from ._base import CRDStatus
from ._base import CRDVersion


class TXTRecordCRD(CRDBase):
    metadata: CRDMetadata = CRDMetadata(name=".".join(reversed(TXTRecord._namespace)))
    spec: CRDSpec = CRDSpec(
        group=".".join(tuple(reversed(TXTRecord._namespace))[-2:]),
        versions=[
            CRDVersion(
                name="v1",
                served=True,
                storage=True,
                crd_schema=TXTRecord,
                status=CRDStatus(),
            ),
        ],
        names=CRDNames(
            plural=TXTRecord._plural,
            singular=TXTRecord._singular,
            kind=TXTRecord._kind,
            shortnames=TXTRecord._shortnames,
        ),
    )
