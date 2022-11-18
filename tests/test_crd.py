from route53_operator.crds import ARecordCRD
from route53_operator.crds import CNAMERecordCRD
from route53_operator.crds import TXTRecordCRD
import yaml
import pytest
import pytest

CRD_OBJECTS = [ARecordCRD, CNAMERecordCRD, TXTRecordCRD]


@pytest.mark.parametrize("crd", CRD_OBJECTS)
def test_crd_is_valid_yaml(crd):
    """Test that the CRD is valid YAML"""
    # Is this test dumb? Yeah probably
    # But it's here. And it's passing.
    assert yaml.safe_load(yaml.dump(crd().to_crd()))


@pytest.mark.k8s
@pytest.mark.slow
@pytest.mark.parametrize("crd", CRD_OBJECTS)
def test_crd_is_valid_crd(crd, session_kind_cluster, tmp_path_factory):
    """Test that the CRD is a valid CRD by loading it into a k8s cluster with kind"""
    temp_path = tmp_path_factory.mktemp(crd.__qualname__)
    crd_path = temp_path / "crd.yml"
    with open(crd_path, "w") as f:
        f.write(yaml.dump(crd().to_crd()))

    session_kind_cluster.kubectl("apply", "-f", crd_path)
