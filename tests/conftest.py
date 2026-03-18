"""Shared pytest fixtures for cs2bim tests."""
import pytest
import sys
import os

# Add project root to path so cs2bim package can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cs2bim.configuration import Config, DatabaseConfig, GeometryConfig, DTMConfig
from cs2bim.geometry import Polygon2D


@pytest.fixture
def default_db_config():
    """Return a default DatabaseConfig."""
    return DatabaseConfig(
        host="localhost",
        port=5432,
        database="testdb",
        user="testuser",
        password="testpass",
        schema="public"
    )


@pytest.fixture
def default_geometry_config():
    """Return a default GeometryConfig."""
    return GeometryConfig(
        srid=25832,
        lod=2,
        simplify_tolerance=0.1,
        min_building_area=5.0
    )


@pytest.fixture
def default_dtm_config():
    """Return a default DTMConfig."""
    return DTMConfig(
        file_path="/tmp/test.tif",
        interpolation_method="bilinear",
        nodata_value=-9999.0
    )


@pytest.fixture
def default_config(default_db_config, default_geometry_config, default_dtm_config):
    """Return a fully populated Config."""
    return Config(
        database=default_db_config,
        geometry=default_geometry_config,
        dtm=default_dtm_config,
        output_dir="/tmp/cs2bim_output",
        project_name="TestProject",
        author="TestAuthor"
    )


@pytest.fixture
def simple_square_polygon() -> Polygon2D:
    """Return a simple 4-point square polygon."""
    return [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]


@pytest.fixture
def triangle_polygon() -> Polygon2D:
    """Return a simple triangle polygon."""
    return [(0.0, 0.0), (6.0, 0.0), (3.0, 4.0)]
