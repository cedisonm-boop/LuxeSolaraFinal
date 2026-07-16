# Deployment

1. Copy `.env.example` to `.env` and set secrets.
2. Start PostgreSQL and app with `docker compose up --build`.
3. Run migrations: `alembic upgrade head`.
4. Load development seed data: `python -m app.seed seeds/development_seed.json`.
5. Serve `frontend/luxe-solara-assessment.js` from a CDN or static hosting.

Backups should include PostgreSQL logical dumps and immutable object storage for uploaded document metadata/files when enabled.
