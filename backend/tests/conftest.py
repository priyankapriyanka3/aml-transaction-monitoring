import os
import tempfile
from pathlib import Path

# 1. Configuration BEFORE anything imports the app
_BACKEND = Path(__file__).resolve().parents[1]
for _seed in ("dev.env", ".env.example"):
    if (_BACKEND / _seed).is_file():
        for _line in (_BACKEND / _seed).read_text().splitlines():
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _key, _value = _line.removeprefix("export ").split("=", 1)
                os.environ.setdefault(_key.strip(), _value.strip().strip("\"'"))
        break

_DB_FILE = Path(tempfile.mkdtemp()) / "test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_DB_FILE.as_posix()}"
os.environ["RATE_LIMIT_ENABLED"] = "false"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base, get_db
import app.models  # noqa: F401

engine = create_engine(os.environ["DATABASE_URL"], connect_args={"check_same_thread": False})
TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture(autouse=True)
def _fresh_schema():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session() -> Session:
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    from app.main import app
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_client(client, db_session):
    """Logged in test client through the app's own login"""
    import bcrypt
    import uuid
    from app.models.user import User
    
    # Create test user
    password_hash = bcrypt.hashpw("Test-pass-1".encode(), bcrypt.gensalt()).decode()
    user = User(
        user_id=uuid.UUID(int=999),
        username="tester",
        display_name="Test User",
        email="tester@example.com",
        password_hash=password_hash,
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    # Login through real endpoint
    response = client.post("/api/v1/auth/login", json={"username": "tester", "password": "Test-pass-1"})
    assert response.status_code == 200, response.text
    token = response.json().get("auth_token")
    
    if token:
        client.headers["Authorization"] = f"Bearer {token}"
    
    return client
