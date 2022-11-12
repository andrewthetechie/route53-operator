FROM python:3.10-slim-buster as builder

ADD src /src
ADD poetry.lock /poetry.lock
ADD pyproject.toml /pyproject.toml
ADD README.md /README.md
ADD constraints.txt /constraints.txt

RUN --mount=type=cache,target=/root/.cache/pip pip install --upgrade pip twine build --constraint /constraints.txt
RUN --mount=type=cache,target=/root/.cache/pip python -m build --sdist --wheel --outdir /dist/
RUN twine check /dist/*

FROM python:3.10-slim-buster

COPY --from=builder /dist /dist
RUN --mount=type=cache,target=/root/.cache/pip pip install /dist/*.whl
RUN adduser --no-create-home nonroot

USER nonroot
ENTRYPOINT ["r53operator"]
