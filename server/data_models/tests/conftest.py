"""Shared test fixtures and configuration."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def mock_bigquery_client():
    """Create a mock BigQuery client."""
    mock_client = MagicMock()
    mock_client.project = "test-project"
    yield mock_client
