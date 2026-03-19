import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "requires_postgis: mark test as requiring a live PostGIS database"
    )
    config.addinivalue_line(
        "markers", "requires_redis: mark test as requiring a live Redis instance"
    )
    config.addinivalue_line(
        "markers", "requires_external: mark test as requiring external services"
    )


@pytest.fixture
def mock_config():
    """Provide a minimal in-memory configuration object for tests that need config but no real services."""

    class MockRedis:
        host = "localhost"
        port = 6379
        global_keyprefix = "test"

        class db:
            file_cache = 0

    class MockDb:
        host = "localhost"
        port = 5432
        dbname = "cs2bim_test"
        user = "test"
        password = "test"

    class MockIfc:
        author = "Test Author"
        geo_referencing = None

    class MockI18n:
        de = "de.yml"
        fr = "fr.yml"
        it = "it.yml"

    class Config:
        logging_level = "DEBUG"
        redis = MockRedis()
        db = MockDb()
        ifc = MockIfc()
        i18n = MockI18n()

    return Config()
