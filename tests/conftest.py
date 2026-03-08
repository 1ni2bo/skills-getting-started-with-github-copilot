"""Pytest configuration and shared fixtures"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Fixture that provides a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Fixture that resets activities to a known state before each test"""
    from app import activities
    original_state = {
        name: {
            "description": data["description"],
            "schedule": data["schedule"],
            "max_participants": data["max_participants"],
            "participants": data["participants"].copy()
        }
        for name, data in activities.items()
    }
    yield
    # Reset after test
    activities.clear()
    activities.update(original_state)