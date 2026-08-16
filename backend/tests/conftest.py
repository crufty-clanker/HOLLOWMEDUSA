import pytest
from fastapi.testclient import TestClient

from hollowmedusa.api.main import app


@pytest.fixture
def client():
    """Simple test client without DB override.

    Note: Full integration tests require async test setup.
    This fixture provides basic endpoint structure validation.
    """
    with TestClient(app) as c:
        yield c
