import logging, uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.admin import router as admin_router
from app.api.public import router as public_router
from app.core.config import get_settings
from app.core.database import Base, engine
import app.models  # noqa: F401

settings = get_settings()
logging.basicConfig(level=logging.INFO, format='{"level":"%(levelname)s","message":"%(message)s"}')
app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_methods=["*"], allow_headers=["*"])

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

@app.get("/health")
def health() -> dict[str, str]: return {"status":"ok"}
@app.get("/ready")
def ready() -> dict[str, str]: return {"status":"ready"}
@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)

app.include_router(public_router)
app.include_router(admin_router)
