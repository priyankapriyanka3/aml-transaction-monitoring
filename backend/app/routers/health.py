"""
Health Check API router.
Provides readiness and liveness endpoints.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..config import Settings
from ..database import get_db

router = APIRouter(prefix="/api/v1/health", tags=["health"])


@router.get("/ready", response_model=dict, status_code=status.HTTP_200_OK)
def get_readiness(db: Session = Depends(get_db)):
    """
    Health readiness check.
    
    Returns:
    - status: "ready" if all checks pass
    - app_version: Application version from config
    - database: Database connection status
    - checked_at: Timestamp of check
    
    This endpoint can be used by orchestrators (Kubernetes, Docker Compose)
    to determine if the application is ready to serve traffic.
    """
    settings = Settings()
    
    # Check database connection
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "ready",
        "app_version": "1.0.0",
        "database": db_status,
        "checked_at": datetime.now(timezone.utc).isoformat()
    }
