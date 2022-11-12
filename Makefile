
.DEFAULT_GOAL := help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-40s\033[0m %s\n", $$1, $$2}'

setup: ## Setup a dev environment for working in this repo. Assumes in a venv or other isolation
	pip install --upgrade pip poetry --constraint constraints.txt
	poetry install

build: ## build python packages
	pip install --upgrade twine build --constraint constraints.txt
	python -m build --sdist --wheel --outdir dist/
	twine check dist/*

build-ci: setup build

test: ## Run unit tests
	poetry run pytest

test-ci: setup test
