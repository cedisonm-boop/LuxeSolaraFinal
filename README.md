# Luxe Solara Qualification Platform

Configuration-driven qualification platform for Luxe Solara resort-owner assessments.

## Run locally

```bash
python -m pip install -e .[dev]
alembic upgrade head
python -m app.seed seeds/development_seed.json
uvicorn app.main:app --reload
```

## Public embed

```html
<luxe-solara-assessment assessment-key="fit-check" api-base-url="https://api.example.com"></luxe-solara-assessment>
<script type="module" src="https://cdn.example.com/luxe-solara-assessment.js"></script>
```

## Checks

```bash
pytest
ruff check .
mypy app
```

## Environment

Copy `.env.example` to `.env` and set `DATABASE_URL`, `SECRET_KEY`, CORS origins, and optional GoHighLevel credentials.

## Troubleshooting dependency installation

If `python -m pip install -e .[dev]` fails while installing build dependencies with a package-index/proxy error such as `Tunnel connection failed: 403 Forbidden`, the issue is the execution environment's access to PyPI, not the application code. Use one of these fixes:

1. In a restricted environment where dependencies are already present, bypass build isolation so pip does not try to create an isolated build environment and fetch `setuptools`:

```bash
python -m pip install --no-build-isolation -e .[dev]
pytest -q
```

2. In an environment that requires a corporate/private package index, configure pip before installing:

```bash
python -m pip config set global.index-url https://<your-private-index>/simple
python -m pip config set global.trusted-host <your-private-index-host>
python -m pip install -e .[dev]
pytest -q
```

3. In CI, ensure the runner has outbound access to PyPI or to the configured private package mirror.
