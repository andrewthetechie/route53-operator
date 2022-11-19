"""Contains a handler for login to the k8s cluster"""
from .. import kopf
from .. import kopf_registry


@kopf.on.login(registry=kopf_registry)
def login_fn(**kwargs) -> None:
    """
    Uses kopf piggybacking to login to k8s via pykybe

    """
    # https://kopf.readthedocs.io/en/stable/authentication/#piggybacking
    return kopf.login_via_pykube(**kwargs)
