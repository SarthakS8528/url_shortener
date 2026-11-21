
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from app.routes import urls


# Create an isolated in-memory SQLite database
TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


# Fake Redis implementation
class FakeRedis:
    def __init__(self):
        self.data = {}

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value, ex=None):
        self.data[key] = value
        return True


@pytest.fixture
def client(db_session, monkeypatch):

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Replace actual Redis client with FakeRedis
    fake_redis = FakeRedis()

    monkeypatch.setattr(
        urls,
        "redis_client",
        fake_redis
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
