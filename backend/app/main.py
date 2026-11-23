"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, alerts, cases, requests, decisions, readiness


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup: Seed data (database initialized by Alembic migrations)
    print("Starting up AML Workbench Backend...")
    
    # Import and run seeding
    from app.seed import seed_all
    seed_all()
    
    yield
    
    # Shutdown
    print("Shutting down AML Workbench Backend...")


# Create FastAPI application
app = FastAPI(
    title="AML Transaction Monitoring & Compliance Workbench",
    description="Backend API for AML transaction monitoring, case investigation, and compliance workflows",
    version="0.1.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(alerts.router)
app.include_router(cases.router)
app.include_router(requests.router, tags=["requests"])
app.include_router(readiness.router, tags=["readiness"])
app.include_router(decisions.router, tags=["decisions"])


@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "aml-workbench-backend",
        "version": "0.1.0"
    }


@app.get("/", tags=["root"])
def root():
    """Root endpoint with API information."""
    return {
        "service": "AML Transaction Monitoring & Compliance Workbench API",
        "version": "0.1.0",
        "docs": "/api/v1/docs",
        "health": "/health"
    }
