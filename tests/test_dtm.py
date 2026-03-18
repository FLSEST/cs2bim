"""Tests for cs2bim.dtm module (with mocks)."""
import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from cs2bim.configuration import DTMConfig
from cs2bim.dtm import DTMProcessor, DTMLoadError


@pytest.fixture
def dtm_config():
    return DTMConfig(
        file_path="/tmp/test.tif",
        interpolation_method="bilinear",
        nodata_value=-9999.0
    )


@pytest.fixture
def dtm_processor(dtm_config):
    return DTMProcessor(dtm_config)


@pytest.fixture
def loaded_dtm(dtm_processor):
    """Return DTMProcessor with pre-loaded mock data."""
    dtm_processor._data = np.array([
        [100.0, 101.0, 102.0],
        [103.0, 104.0, 105.0],
        [106.0, 107.0, 108.0],
    ])
    # GeoTransform: (origin_x, pixel_width, 0, origin_y, 0, -pixel_height)
    dtm_processor._transform = (0.0, 1.0, 0.0, 3.0, 0.0, -1.0)
    dtm_processor._width = 3
    dtm_processor._height = 3
    dtm_processor._loaded = True
    return dtm_processor


class TestDTMProcessor:
    def test_initial_state(self, dtm_processor):
        """Processor should start unloaded."""
        assert not dtm_processor.is_loaded()

    def test_load_no_gdal(self, dtm_processor):
        """Missing GDAL should raise DTMLoadError."""
        with patch.dict("sys.modules", {"osgeo": None, "osgeo.gdal": None}):
            with pytest.raises(DTMLoadError):
                dtm_processor.load()

    def test_load_no_path(self, dtm_processor):
        """Empty path should raise DTMLoadError."""
        dtm_processor.config.file_path = ""
        with pytest.raises(DTMLoadError, match="No file path"):
            dtm_processor.load()

    def test_get_elevation_not_loaded(self, dtm_processor):
        """Getting elevation before load should raise DTMLoadError."""
        with pytest.raises(DTMLoadError, match="not loaded"):
            dtm_processor.get_elevation(0.0, 0.0)

    def test_get_elevation_valid(self, loaded_dtm):
        """Get elevation at a known grid point."""
        # Transform: origin_x=0, pixel_w=1, origin_y=3, pixel_h=-1
        # For (x=0, y=3): px=0, py=0 → row=0, col=0 → value=100.0
        elevation = loaded_dtm.get_elevation(0.0, 3.0)
        assert elevation == 100.0

    def test_get_elevation_out_of_bounds(self, loaded_dtm):
        """Out-of-bounds coordinates should raise ValueError."""
        with pytest.raises(ValueError, match="outside"):
            loaded_dtm.get_elevation(100.0, 100.0)

    def test_get_stats_loaded(self, loaded_dtm):
        """Stats should return min, max, mean, count."""
        stats = loaded_dtm.get_stats()
        assert stats["min"] == 100.0
        assert stats["max"] == 108.0
        assert stats["count"] == 9
        assert abs(stats["mean"] - 104.0) < 1e-9

    def test_get_stats_not_loaded(self, dtm_processor):
        """Stats on unloaded DTM should raise DTMLoadError."""
        with pytest.raises(DTMLoadError):
            dtm_processor.get_stats()
