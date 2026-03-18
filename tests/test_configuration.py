"""Tests for cs2bim.configuration module."""
import pytest
from cs2bim.configuration import Config, DatabaseConfig, GeometryConfig, DTMConfig


class TestDatabaseConfig:
    def test_default_values(self):
        """Test DatabaseConfig default values."""
        cfg = DatabaseConfig()
        assert cfg.host == "localhost"
        assert cfg.port == 5432
        assert cfg.database == "citygml"
        assert cfg.user == "postgres"
        assert cfg.schema == "public"

    def test_connection_string(self, default_db_config):
        """Test connection string generation."""
        conn_str = default_db_config.get_connection_string()
        assert "localhost" in conn_str
        assert "5432" in conn_str
        assert "testdb" in conn_str
        assert "testuser" in conn_str

    def test_validate_valid_config(self, default_db_config):
        """Valid config should not raise."""
        default_db_config.validate()  # Should not raise

    def test_validate_empty_host(self):
        """Empty host should raise ValueError."""
        cfg = DatabaseConfig(host="")
        with pytest.raises(ValueError, match="host"):
            cfg.validate()

    def test_validate_invalid_port(self):
        """Invalid port should raise ValueError."""
        cfg = DatabaseConfig(port=0)
        with pytest.raises(ValueError, match="port"):
            cfg.validate()

    def test_validate_port_too_large(self):
        """Port > 65535 should raise ValueError."""
        cfg = DatabaseConfig(port=99999)
        with pytest.raises(ValueError):
            cfg.validate()


class TestGeometryConfig:
    def test_default_values(self):
        """Test GeometryConfig default values."""
        cfg = GeometryConfig()
        assert cfg.srid == 25832
        assert cfg.lod == 2
        assert cfg.simplify_tolerance == 0.1
        assert cfg.min_building_area == 5.0

    def test_validate_valid(self, default_geometry_config):
        """Valid geometry config should not raise."""
        default_geometry_config.validate()

    def test_validate_invalid_lod(self):
        """LOD outside 1-4 should raise ValueError."""
        cfg = GeometryConfig(lod=5)
        with pytest.raises(ValueError, match="LOD"):
            cfg.validate()

    def test_validate_negative_tolerance(self):
        """Negative tolerance should raise ValueError."""
        cfg = GeometryConfig(simplify_tolerance=-1.0)
        with pytest.raises(ValueError):
            cfg.validate()


class TestDTMConfig:
    def test_validate_invalid_interpolation(self):
        """Invalid interpolation method should raise ValueError."""
        cfg = DTMConfig(interpolation_method="unknown")
        with pytest.raises(ValueError, match="interpolation"):
            cfg.validate()

    def test_validate_valid_methods(self):
        """All valid interpolation methods should pass."""
        for method in ("bilinear", "nearest", "cubic"):
            cfg = DTMConfig(interpolation_method=method)
            cfg.validate()  # Should not raise


class TestConfig:
    def test_from_dict_minimal(self):
        """from_dict with minimal data should use defaults."""
        cfg = Config.from_dict({})
        assert cfg.project_name == "cs2bim_project"
        assert cfg.output_dir == "output"

    def test_from_dict_with_database(self):
        """from_dict should populate database config."""
        cfg = Config.from_dict({
            "database": {"host": "myserver", "port": 5433, "database": "mydb"},
            "project_name": "MyProject"
        })
        assert cfg.database.host == "myserver"
        assert cfg.database.port == 5433
        assert cfg.project_name == "MyProject"

    def test_validate_empty_output_dir(self):
        """Empty output_dir should raise ValueError."""
        cfg = Config(output_dir="")
        with pytest.raises(ValueError, match="output_dir"):
            cfg.validate()

    def test_validate_empty_project_name(self):
        """Empty project_name should raise ValueError."""
        cfg = Config(project_name="")
        with pytest.raises(ValueError, match="project_name"):
            cfg.validate()
