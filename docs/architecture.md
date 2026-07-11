# Architecture

The implementation is a modular FastAPI monolith. The public API serves versioned assessment schemas and accepts submissions. The qualification engine is a pure Python domain service that evaluates validated structured rule data and has no dependency on FastAPI, HTML, payment providers, GoHighLevel, or SQLAlchemy sessions.

Core modules:
- `app/domain`: Pydantic domain schemas for assessments, rules, results, and submissions.
- `app/services`: assessment validation, submissions, qualification, results, and access control services.
- `app/api`: versioned public and admin routes.
- `app/integrations`: GoHighLevel adapter and retry queue abstractions.
- `app/models.py`: SQLAlchemy persistence model.
- `frontend/luxe-solara-assessment.js`: embeddable schema-rendered widget with no qualification logic.
