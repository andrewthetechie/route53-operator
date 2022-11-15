from route53_operator.crds import ARecordCRD
from route53_operator.crds import CNAMERecordCRD
from route53_operator.crds import TXTRecordCRD
import yaml
import pytest


@pytest.mark.parametrize("model", [ARecordCRD, CNAMERecordCRD, TXTRecordCRD])
def test_crd_is_valid_yaml(model):
    """Test that the CRD is valid YAML"""
    # Is this test dumb? Yeah probably
    # But it's here. And it's passing.
    assert yaml.safe_load(yaml.dump(model().to_crd()))
