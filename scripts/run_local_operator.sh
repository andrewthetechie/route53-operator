#!/bin/bash
# Script used to run the operator locally.
# Starts a cluster in kind, starts localstack for AWS emulation, and starts the operator with env vars so it uses localstack and the kind k8s cluster
# The Trap will cleanup the cluster and localstack when the script exits.
set -e
function cleanup {
    echo "Deleting kind cluster and stopping localstack"
    kind delete cluster --name local-operator
    localstack stop
}

trap cleanup EXIT
echo "Creating a kind cluster"
kind create cluster --name local-operator
echo "Starting localstack"
localstack start -d
echo "Setting up CRDs in the cluster"
python scripts/generate_crds_yaml.py ./.crd_yaml
find ./.crd_yaml -type f -name '*.yml' -exec kubectl apply -f {} \;
echo "Starting local operator"
AWS_ACCESS_KEY_ID=x AWS_SECRET_ACCESS_KEY=x AWS_USE_SSL=false AWS_ENDPOINT_URL=http://localhost:4566 r53operator
