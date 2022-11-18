Contributor Guide
=================

Thank you for your interest in improving this project.
This project is open-source under the `MIT license`_ and
welcomes contributions in the form of bug reports, feature requests, and pull requests.

Here is a list of important resources for contributors:

- `Source Code`_
- `Documentation`_
- `Issue Tracker`_
- `Code of Conduct`_

.. _MIT license: https://opensource.org/licenses/MIT
.. _Source Code: https://github.com/andrewthetechie/pydantic-aioredis
.. _Documentation: https://pydantic-aioredis.readthedocs.io/
.. _Issue Tracker: https://github.com/andrewthetechie/pydantic-aioredis/issues

How to report a bug
-------------------

Report bugs on the `Issue Tracker`_.

When filing an issue, make sure to answer these questions:

- Which operating system and Python version are you using?
- Which version of this project are you using?
- What did you do?
- What did you expect to see?
- What did you see instead?

The best way to get your bug fixed is to provide a test case,
and/or steps to reproduce the issue.


How to request a feature
------------------------

Request features on the `Issue Tracker`_.


How to set up your development environment
------------------------------------------

You need Python 3.10+ and the following tools:

- Poetry_
- Docker_
- kind_

Install the package with development requirements:

.. code:: console

   $ poetry install

You can now run an interactive Python session,
or the command-line interface:

.. code:: console

   $ poetry run python

.. _Poetry: https://python-poetry.org/
.. _Docker: https://www.docker.com/
.. _kind: https://kind.sigs.k8s.io/


How to test the project
-----------------------

Run the full test suite:

.. code:: console

   $ pytest


Unit tests are located in the ``tests`` directory,
and are written using the pytest_ testing framework.


Tests against k8s
^^^^^^^^^^^^^^^^^

Some tests use kind to create a k8s cluster to run against. If you want to speed up local execution,
you can create a kind cluster and run the tests against that cluster. To do so, run the following commands:

.. code:: console
    Creating cluster "test" ...
    ✓ Ensuring node image (kindest/node:v1.25.3) 🖼
    ✓ Preparing nodes 📦
    ✓ Writing configuration 📜
    ✓ Starting control-plane 🕹️
    ✓ Installing CNI 🔌
    ✓ Installing StorageClass 💾
    Set kubectl context to "kind-test"
    You can now use your cluster with:

    kubectl cluster-info --context kind-test

    Have a nice day! 👋
    $ R53_OP_TEST_KIND_CLUSTER_NAME=pytest pytest


The environment variable `R53_OP_TEST_KIND_CLUSTER_NAME` sets an existing cluster name. `R53_OP_TEST_KIND_KUBECONFIG` can set a path to a custom kubeconfig,
but will assume `~/.kube/config` by default.

Skipping k8s tests for speed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Tests using k8s are all marked with `k8s`. You can skip them by telling pytest to skip that mark.

.. code:: console

   $ pytest -m "not k8s"


.. _pytest: https://pytest.readthedocs.io/


Running the Operator Locally for Development
--------------------------------------------

You can run the operator locally using localstack to emulate the AWS Route53 API and kind to create a k8s cluster.

The Makefile has a target to make this easier:

.. code:: console

   $ make run-local-operator



How to submit changes
---------------------

Open a `pull request`_ to submit changes to this project.

Your pull request needs to meet the following guidelines for acceptance:

- The Nox test suite must pass without errors and warnings.
- Include unit tests. This project maintains 100% code coverage.
- If your changes add functionality, update the documentation accordingly.

Feel free to submit early, though—we can always iterate on this.

To run linting and code formatting checks before committing your change, you can install pre-commit as a Git hook by running the following command:

.. code:: console

   $ nox --session=pre-commit -- install

It is recommended to open an issue before starting work on anything.
This will allow a chance to talk it over with the owners and validate your approach.

.. _pull request: https://github.com/andrewthetechie/pydantic-aioredis/pulls
.. github-only
.. _Code of Conduct: CODE_OF_CONDUCT.rst
