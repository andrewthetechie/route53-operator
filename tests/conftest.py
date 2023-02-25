import pytest
from pytest_kind import KindCluster
from filelock import FileLock, Timeout
from datetime import datetime
import os
from pathlib import Path
from route53_operator.crds import CRDS
from route53_operator.lib.config import Config
import yaml

import asyncio
import os
import random
import string
import sys
import tempfile
from contextlib import ExitStack
from itertools import chain
from unittest.mock import patch
import os
import pytest_asyncio
import docker
import aiohttp
from aiobotocore.session import get_session


import aiobotocore.session
from aiobotocore.config import AioConfig
from tests._helpers import AsyncExitStack


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
def crds(tmp_path_factory) -> list[Path]:
    """Returns a list of paths to CRD files for this operator"""
    crd_path = tmp_path_factory.getbasetemp().parent / "crds"
    crd_path.mkdir(exist_ok=True)
    to_return = []
    for crd in CRDS:
        this_crd_path = crd_path / f"{crd.__qualname__.yml}"
        with open(this_crd_path, "w") as f:
            f.write(yaml.dump(crd().to_crd()))
        to_return.append(this_crd_path)
    return to_return


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


@pytest.fixture(scope="session")
def test_config() -> Config:
    return Config(
        aws_access_key_id="x",
        aws_secret_access_key="x",
    )


host = "127.0.0.1"


@pytest.fixture(scope="session", params=[True, False], ids=["debug[true]", "debug[false]"])
def debug(request):
    return request.param


def random_bucketname():
    # 63 is the max bucket length.
    return random_name()


def random_tablename():
    return random_name()


def random_name():
    """Return a string with presumably unique contents

    The string contains only symbols allowed for s3 buckets
    (alphanumeric, dot and hyphen).
    """
    return "".join(random.sample(string.ascii_lowercase, k=26))


def assert_status_code(response, status_code):
    assert response["ResponseMetadata"]["HTTPStatusCode"] == status_code


async def assert_num_uploads_found(
    s3_client,
    bucket_name,
    operation,
    num_uploads,
    *,
    max_items=None,
    num_attempts=5,
):
    paginator = s3_client.get_paginator(operation)
    for _ in range(num_attempts):
        pages = paginator.paginate(Bucket=bucket_name, PaginationConfig={"MaxItems": max_items})
        responses = []
        async for page in pages:
            responses.append(page)

        # It sometimes takes a while for all the uploads to show up,
        # especially if the upload was just created.  If we don't
        # see the expected amount, we retry up to num_attempts time
        # before failing.
        amount_seen = len(responses[0]["Uploads"])
        if amount_seen == num_uploads:
            # Test passed.
            return
        else:
            # Sleep and try again.
            await asyncio.sleep(2)

        pytest.fail("Expected to see {} uploads, instead saw: {}".format(num_uploads, amount_seen))


@pytest.fixture
def aa_fail_proxy_config(monkeypatch):
    # NOTE: name of this fixture must be alphabetically first to run first
    monkeypatch.setenv("HTTP_PROXY", f"http://{host}:54321")
    monkeypatch.setenv("HTTPS_PROXY", f"http://{host}:54321")


@pytest.fixture
def aa_succeed_proxy_config(monkeypatch):
    # NOTE: name of this fixture must be alphabetically first to run first
    monkeypatch.setenv("HTTP_PROXY", f"http://{host}:54321")
    monkeypatch.setenv("HTTPS_PROXY", f"http://{host}:54321")

    # this will cause us to skip proxying
    monkeypatch.setenv("NO_PROXY", "amazonaws.com")


@pytest.fixture
def session():
    session = aiobotocore.session.AioSession()
    return session


@pytest.fixture
def region():
    return "us-east-1"


@pytest.fixture
def alternative_region():
    return "us-west-2"


@pytest.fixture
def signature_version():
    return "s3"


@pytest.fixture
def server_scheme():
    return "http"


@pytest.fixture
def s3_verify():
    return None


@pytest.fixture
def config(request, region, signature_version):
    config_kwargs = request.node.get_closest_marker("config_kwargs") or {}
    if config_kwargs:
        assert not config_kwargs.kwargs, config_kwargs
        assert len(config_kwargs.args) == 1
        config_kwargs = config_kwargs.args[0]

    connect_timeout = read_timout = 5
    if _PYCHARM_HOSTED:
        connect_timeout = read_timout = 180

    return AioConfig(
        region_name=region,
        signature_version=signature_version,
        read_timeout=read_timout,
        connect_timeout=connect_timeout,
        **config_kwargs,
    )


@pytest.fixture
def mocking_test():
    # change this flag for test with real aws
    # TODO: this should be merged with pytest.mark.moto
    return True


def moto_config(endpoint_url):
    kw = dict(
        endpoint_url=endpoint_url,
        aws_secret_access_key="xxx",
        aws_access_key_id="xxx",
    )

    return kw


@pytest.fixture
def patch_attributes(request):
    """Call unittest.mock.patch on arguments passed through a pytest mark.

    This fixture looks at the @pytest.mark.patch_attributes mark. This mark is a list
    of arguments to be passed to unittest.mock.patch (see example below). This fixture
    returns the list of mock objects, one per element in the input list.

    Why do we need this? In some cases, we want to perform the patching before other
    fixtures are run. For instance, the `s3_client` fixture creates an aiobotocore
    client. During the client creation process, some event listeners are registered.
    When we want to patch the target of these event listeners, we must do so before
    the `s3_client` fixture is executed.  Otherwise, the aiobotocore client will store
    references to the unpatched targets.

    In such situations, make sure that subsequent fixtures explicitly depends on
    `patch_attribute` to enforce the ordering between fixtures.

    Example:

    @pytest.mark.patch_attributes([
        dict(
            target="aiobotocore.retries.adaptive.AsyncClientRateLimiter.on_sending_request",
            side_effect=aiobotocore.retries.adaptive.AsyncClientRateLimiter.on_sending_request,
            autospec=True
        )
    ])
    async def test_client_rate_limiter_called(s3_client, patch_attributes):
        await s3_client.get_object(Bucket="bucket", Key="key")
        # Just for illustration (this test doesn't pass).
        # mock_attributes is a list of 1 element, since we passed a list of 1 element
        # to the patch_attributes marker.
        mock_attributes[0].assert_called_once()
    """
    marker = request.node.get_closest_marker("patch_attributes")
    if marker is None:
        yield
    else:
        with ExitStack() as stack:
            yield [stack.enter_context(patch(**kwargs)) for kwargs in marker.args[0]]


@pytest.fixture
async def dynamodb_client(session, region, config, dynamodb2_server, mocking_test):
    kw = moto_config(dynamodb2_server) if mocking_test else {}
    async with session.create_client("dynamodb", region_name=region, config=config, **kw) as client:
        yield client


@pytest.fixture
async def aio_session():
    async with aiohttp.ClientSession() as session:
        yield session


@pytest.fixture
async def exit_stack():
    async with AsyncExitStack() as es:
        yield es


pytest_plugins = ["tests.mock_server"]


@pytest_asyncio.fixture(scope="session", name="ls_container")
def create_localstack_container(unused_tcp_port_factory):
    """Runs a localstack container for use with testing"""
    import time

    port1 = unused_tcp_port_factory()
    port2 = unused_tcp_port_factory()
    try:
        client = docker.from_env()
        container = client.containers.run(
            f"localstack/localstack:{os.environ.get('LOCALSTACK_IMAGE_TAG', 'latest')}",
            ports={"4566/tcp": port1, "4571/tcp": port2},
            detach=True,
        )
        time.sleep(1)
        yield {"endpoint_url": f"http://localhost:{port1}/", "port_2": port2}
    finally:
        container.remove(force=True)


@pytest_asyncio.fixture(name="ls_session")
async def create_ls_session_and_client_args(test_config, ls_container) -> dict:
    endpoint_url = ls_container["endpoint_url"]
    session = get_session()
    test_config.aws_use_ssl = False
    test_config.aws_endpoint_url = endpoint_url
    yield {"session": session, "config": test_config}


@pytest_asyncio.fixture(name="ls_zone")
async def create_localstack_hosted_zone(ls_session):
    """Creates a hosted zone in localstack for use with testing"""
    session = ls_session["session"]

    zone_name = f"{''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=8))}.com"
    async with session.create_client("route53", **ls_session["config"].aws_client_kwargs) as client:
        response = await client.create_hosted_zone(
            Name=zone_name,
            CallerReference="".join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=8)),
        )
        yield {
            "zone_id": response["HostedZone"]["Id"],
            "name": response["HostedZone"]["Name"],
            "session": session,
            "config": ls_session["config"],
        }
