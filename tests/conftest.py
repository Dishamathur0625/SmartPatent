import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Ensure the project root is in the path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Mock the database pool BEFORE importing app
mock_pool = MagicMock()
mock_conn = MagicMock()
mock_cursor = MagicMock()

mock_pool.get_connection.return_value = mock_conn
mock_conn.cursor.return_value = mock_cursor

# Patch the connection pool globally during imports
with patch('mysql.connector.pooling.MySQLConnectionPool', return_value=mock_pool):
    from app import app as flask_app

@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": "testing_secret_key"
    })
    return flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db_mocks():
    return {
        "pool": mock_pool,
        "conn": mock_conn,
        "cursor": mock_cursor
    }
