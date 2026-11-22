from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from .config import settings
from .middleware.error_handlers import (
    general_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from .routers import alerts, audit_events, auth, cases, health, information_requests


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: migrations are applied via alembic upgrade head before server starts
    # Seed data loaded via separate seed script
    yield
    # Shutdown: cleanup if needed


app = FastAPI(
    title="AML Transaction Monitoring & Compliance Workbench",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(Exception, general_exception_handler)

# Mount routers
app.include_router(auth.router)
app.include_router(alerts.router)
app.include_router(cases.router)
app.include_router(information_requests.router)
app.include_router(audit_events.router)
app.include_router(health.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "app": "aml-backend"}
