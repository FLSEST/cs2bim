"""Tests for cs2bim.postgis module (with mocks)."""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from cs2bim.configuration import DatabaseConfig
from cs2bim.postgis import PostGISConnector, PostGISConnectionError, PostGISQueryError


@pytest.fixture
def connector(default_db_config):
    return PostGISConnector(default_db_config)


@pytest.fixture
def connected_connector(connector):
    """Return a connector with a mocked active connection."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    connector._connection = mock_conn
    connector._cursor = mock_cursor
    return connector


class TestPostGISConnector:
    def test_initial_state(self, connector):
        """Connector should start disconnected."""
        assert not connector.is_connected()

    def test_connect_no_psycopg2(self, connector):
        """Missing psycopg2 should raise PostGISConnectionError."""
        with patch.dict("sys.modules", {"psycopg2": None}):
            with pytest.raises(PostGISConnectionError):
                connector.connect()

    def test_disconnect_when_connected(self, connected_connector):
        """Disconnect should clear connection and cursor."""
        connected_connector.disconnect()
        assert not connected_connector.is_connected()
        assert connected_connector._cursor is None

    def test_query_buildings_not_connected(self, connector):
        """Querying without connection should raise PostGISQueryError."""
        with pytest.raises(PostGISQueryError, match="Not connected"):
            connector.query_buildings()

    def test_query_buildings_success(self, connected_connector):
        """Successful building query should return list of dicts."""
        mock_cursor = connected_connector._cursor
        mock_cursor.description = [
            ("id",), ("geometry",), ("height",), ("name",)
        ]
        mock_cursor.fetchall.return_value = [
            (1, "POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))", 12.5, "Building A"),
            (2, "POLYGON((20 0, 30 0, 30 10, 20 10, 20 0))", 8.0, "Building B"),
        ]

        results = connected_connector.query_buildings()
        assert len(results) == 2
        assert results[0]["id"] == 1
        assert results[0]["height"] == 12.5
        assert results[1]["name"] == "Building B"

    def test_query_buildings_with_limit(self, connected_connector):
        """Query with limit should include LIMIT in SQL."""
        mock_cursor = connected_connector._cursor
        mock_cursor.description = [("id",), ("geometry",), ("height",), ("name",)]
        mock_cursor.fetchall.return_value = []

        connected_connector.query_buildings(limit=10)

        call_args = mock_cursor.execute.call_args[0][0]
        assert "LIMIT 10" in call_args

    def test_get_building_count_success(self, connected_connector):
        """get_building_count should return integer from COUNT query."""
        connected_connector._cursor.fetchone.return_value = (42,)
        count = connected_connector.get_building_count()
        assert count == 42

    def test_get_building_count_not_connected(self, connector):
        """get_building_count without connection should raise PostGISQueryError."""
        with pytest.raises(PostGISQueryError):
            connector.get_building_count()
