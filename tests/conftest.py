import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from io import BytesIO
from reportlab.pdfgen import canvas

from app.main import app
from app.database import Base, get_db
from app.config import settings
from app import models  # noqa - ensures all models are registered on Base.metadata
from app.services.ai_matcher import redis_client as ai_redis_client

# Reuse the same Postgres server, but point at the dedicated test database
TEST_DATABASE_URL = settings.database_url.rsplit("/", 1)[0] + "/resumefit_test"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def flush_redis():
    """Ensure a clean cache + rate-limit slate before every test."""
    ai_redis_client.flushdb()
    yield


@pytest.fixture()
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()  # undo everything the test did
    connection.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    
@pytest.fixture()
def sample_pdf_bytes() -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.drawString(100, 750, "Jane Doe - Backend Developer")
    pdf.drawString(100, 730, "Skills: Python, FastAPI, PostgreSQL, Docker, Redis")
    pdf.save()
    buffer.seek(0)
    return buffer.read()

@pytest.fixture()
def auth_headers(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "resumeuser@example.com", "password": "strongpassword123"},
    )
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "resumeuser@example.com", "password": "strongpassword123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}