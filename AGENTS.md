# Luxe Solara Project Instructions

## Architecture
- Use a modular FastAPI monolith.
- Keep qualification business logic server-side in `app/services/qualification_engine.py` and configuration data, never in the public widget.
- Public front-end code may render schemas and perform UX validation only.
- Published assessment, rule-set, and program versions are immutable; clone to draft before changes.
- Integrations must use adapters and queued delivery records; submission success must not depend on GoHighLevel.

## Commands
- Install: `python -m pip install -e .[dev]`
- Run API: `uvicorn app.main:app --reload`
- Test: `pytest`
- Lint: `ruff check .`
- Type check: `mypy app`
- Migrate: `alembic upgrade head`
- Seed: `python -m app.seed seeds/development_seed.json`

## Testing
- Add tests for engine operators, schema validation, submissions, idempotency, and integration retry behavior.
- Tests must not require live payment or GoHighLevel credentials.

## Style
- Type hints are required for application code.
- Do not wrap imports in try/except.
- Do not use `eval`, `exec`, or generated Python for rules.
- Do not log full PII payloads.

## Dependency troubleshooting
- If editable install fails with `Tunnel connection failed: 403 Forbidden` while fetching build dependencies, retry with `python -m pip install --no-build-isolation -e .[dev]` when dependencies are already available, or configure pip to use the required private package index/mirror.
