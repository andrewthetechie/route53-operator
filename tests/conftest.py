import pytest
from pytest_kind import KindCluster
from filelock import FileLock, Timeout
from datetime import datetime
import os
from pathlib import Path


def existing_cluster(cluster_name: str) -> KindCluster:
    """Returns an existing kind cluster if it exists"""
    kubeconfig = Path(os.environ.get("R53_OP_TEST_KIND_KUBECONFIG", "~/.kube/config")).expanduser()
    cluster = KindCluster(name=cluster_name, kubeconfig=kubeconfig)
    cluster.ensure_kind()
    cluster.ensure_kubectl()
    return cluster


def new_cluster(tmp_path_factory, worker_id: str | None) -> KindCluster:
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    root_tmp_dir = tmp_path_factory.getbasetemp().parent
    if not worker_id:
        # we're not running under xdist
        name = f"pytest-r53-op-{timestamp}"
        pytest_kind_path = root_tmp_dir / f"pytest-kind-{timestamp}"
    else:
        name = f"pytest-r53-op-{worker_id}-{timestamp}"
        pytest_kind_path = root_tmp_dir / f"pytest-kind-{worker_id}-{timestamp}"

    pytest_kind_path.mkdir(exist_ok=True)
    cluster = KindCluster(name=name)
    cluster.path = pytest_kind_path
    return cluster


@pytest.fixture(scope="session")
def session_kind_cluster(tmp_path_factory, worker_id):
    """A kubernetes cluster shared across the whole test of sessions, faster than per test clusters but isn't guaranteed to be clean
    The upstream kind_cluster fixture blows up with xdist, this works around that issue.
    """
    existing_cluster_name = os.environ.get("R53_OP_TEST_KIND_CLUSTER_NAME", None)
    use_existing_cluster = existing_cluster_name is not None
    if use_existing_cluster:
        cluster = existing_cluster(existing_cluster_name)
    else:
        cluster = new_cluster(tmp_path_factory, worker_id)
    cluster.create()
    yield cluster
    if not use_existing_cluster:
        cluster.delete()


def pytest_configure(config):
    """Configure our markers"""
    config.addinivalue_line("markers", "slow: Slow tests, exclude with -m 'not slow'")
    config.addinivalue_line("markers", "k8s: tests that use kind to spin up a k8s cluster, exclude with -m 'not k8s'")
