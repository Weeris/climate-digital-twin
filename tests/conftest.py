"""
Pytest configuration and shared fixtures for Climate Digital Twin tests
"""
import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def project_root():
    """Get project root directory."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def sample_asset_value():
    """Sample asset value for testing."""
    return 10000000


@pytest.fixture
def sample_portfolio():
    """Sample portfolio for testing."""
    return [
        {"id": "A001", "value": 10000000, "pd": 0.02, "lgd": 0.4, "damage_ratio": 0.1},
        {"id": "A002", "value": 5000000, "pd": 0.015, "lgd": 0.35, "damage_ratio": 0.2},
        {"id": "A003", "value": 8000000, "pd": 0.025, "lgd": 0.45, "damage_ratio": 0.15},
    ]


@pytest.fixture
def hk_districts():
    """Sample HK districts for testing."""
    return ["hk_central", "hk_kowloon", "hk_new_territories_west", "hk_new_territories_east"]
