import pytest
from pytest_kind import KindCluster
from filelock import FileLock, Timeout
from datetime import datetime


@pytest.fixture(scope="session")
def session_kind_cluster(tmp_path_factory, worker_id):
    """A kubernetes cluster shared across the whole test of sessions, faster than per test clusters but isn't guaranteed to be clean
    The upstream kind_cluster fixture blows up with xdist, this works around that issue.
    """
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
    cluster.create()
    yield cluster
    cluster.delete()


def pytest_configure(config):
    """Configure our markers"""
    config.addinivalue_line("markers", "slow: Slow tests, exclude with -m 'not slow'")
    config.addinivalue_line("markers", "k8s: tests that use kind to spin up a k8s cluster, exclude with -m 'not k8s'")
