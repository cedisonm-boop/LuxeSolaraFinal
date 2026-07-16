import logging, uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from app.api.admin import router as admin_router
from app.api.public import router as public_router
from app.core.config import get_settings
from app.core.database import Base, engine
import app.models  # noqa: F401

settings = get_settings()
logging.basicConfig(level=logging.INFO, format='{"level":"%(levelname)s","message":"%(message)s"}')
app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_methods=["*"], allow_headers=["*"])
app.mount("/assets", StaticFiles(directory="frontend"), name="assets")

TEST_PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Luxe Solara Fit Check</title>
  <style>
    :root { color-scheme: light; }
    body {
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: #1e2430;
      background: #faf8f5;
    }
    .ls-shell { min-height: 100vh; }
    .ls-hero {
      padding: 56px 20px 34px;
      background: linear-gradient(180deg, #ffffff 0%, #faf8f5 100%);
      border-bottom: 1px solid #e8e2d8;
    }
    .ls-wrap { width: min(1060px, calc(100% - 32px)); margin: 0 auto; }
    .ls-brand { font-size: 14px; letter-spacing: .08em; text-transform: uppercase; color: #9a7b22; font-weight: 700; }
    h1 { max-width: 800px; margin: 14px 0 14px; font-size: clamp(34px, 7vw, 64px); line-height: 1.02; letter-spacing: 0; }
    .ls-copy { max-width: 760px; color: #5f6673; font-size: 18px; line-height: 1.7; }
    .ls-note { margin-top: 18px; color: #5f6673; font-size: 14px; }
    .ls-form-band { padding: 36px 16px 64px; }
    .ls-footer { padding: 24px 20px; border-top: 1px solid #e8e2d8; color: #5f6673; font-size: 13px; }
  </style>
</head>
<body>
  <main class="ls-shell">
    <section class="ls-hero">
      <div class="ls-wrap">
        <div class="ls-brand">Luxe Solara</div>
        <h1>Free Resort Rental Fit Check</h1>
        <p class="ls-copy">Test the live Luxe Solara qualification flow. Submissions are saved by the API and delivered to GoHighLevel automatically when contact delivery is configured.</p>
        <p class="ls-note">Use a unique test email each time so GHL creates a new contact instead of updating an existing one.</p>
      </div>
    </section>
    <section class="ls-form-band">
      <luxe-solara-assessment assessment-key="fit-check"></luxe-solara-assessment>
    </section>
  </main>
  <footer class="ls-footer">
    <div class="ls-wrap">Testing page only. Luxe Solara does not guarantee rental income or program acceptance.</div>
  </footer>
  <script src="/assets/luxe-solara-assessment.js"></script>
</body>
</html>
"""

@app.middleware("http")
async def correlation(request: Request, call_next):
    cid = request.headers.get("x-correlation-id", str(uuid.uuid4()))
    response = await call_next(request)
    response.headers["x-correlation-id"] = cid
    return response

@app.exception_handler(Exception)
async def errors(request: Request, exc: Exception):
    if hasattr(exc, "status_code"):
        return JSONResponse(status_code=exc.status_code, content={"code":"ERROR","message":str(exc.detail),"correlation_id":request.headers.get("x-correlation-id")})
    logging.exception("Unhandled error")
    return JSONResponse(status_code=500, content={"code":"INTERNAL_ERROR","message":"Unexpected error"})

@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return TEST_PAGE

@app.get("/fit-check", response_class=HTMLResponse)
def fit_check() -> str:
    return TEST_PAGE

@app.get("/health")
def health() -> dict[str, str]: return {"status":"ok"}
@app.get("/ready")
def ready() -> dict[str, str]: return {"status":"ready"}
@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)

app.include_router(public_router)
app.include_router(admin_router)
