"""
Pytest configuration and global fixtures for JobShield AI tests.

Provides isolated test database fixtures to prevent state pollution of production db.
"""

import os
import tempfile
import pytest
from pathlib import Path

# Add backend directory to sys.path
import sys
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import database.db as db_module


@pytest.fixture(scope="session", autouse=True)
def isolate_test_database():
    """
    Session-wide fixture that creates a temporary isolated SQLite database
    and sets JOBSHIELD_DB_PATH so all tests run against an isolated sandbox.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
        tmp_db_path = tmp_db.name

    original_env = os.environ.get("JOBSHIELD_DB_PATH")
    os.environ["JOBSHIELD_DB_PATH"] = tmp_db_path
    db_module.DB_PATH = tmp_db_path

    # Initialize schema in test database
    db_module.init_db()

    yield tmp_db_path

    # Teardown
    if original_env is not None:
        os.environ["JOBSHIELD_DB_PATH"] = original_env
    else:
        os.environ.pop("JOBSHIELD_DB_PATH", None)

    try:
        if os.path.exists(tmp_db_path):
            os.remove(tmp_db_path)
    except Exception:
        pass
