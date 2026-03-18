"""Tests for cs2bim.ifc_builder module (with mocks)."""
import pytest
from unittest.mock import MagicMock, patch
from cs2bim.ifc_builder import IFCBuilder, IFCBuilding, IFCStorey, IFCBuildError
from cs2bim.configuration import Config


@pytest.fixture
def ifc_builder(default_config):
    return IFCBuilder(default_config)


@pytest.fixture
def initialized_builder(ifc_builder):
    """Return IFCBuilder with project initialized."""
    ifc_builder.create_project("TestProject")
    return ifc_builder


class TestIFCBuilder:
    def test_initial_state(self, ifc_builder):
        """Builder should start with no buildings."""
        assert ifc_builder.get_building_count() == 0
        assert ifc_builder._project_name is None

    def test_create_project(self, ifc_builder):
        """create_project should return a non-empty GUID."""
        project_id = ifc_builder.create_project("MyProject")
        assert project_id
        assert ifc_builder._project_name == "MyProject"

    def test_create_project_uses_config_name(self, ifc_builder):
        """create_project without name should use config.project_name."""
        ifc_builder.create_project()
        assert ifc_builder._project_name == ifc_builder.config.project_name

    def test_add_building_success(self, initialized_builder, simple_square_polygon):
        """add_building should return IFCBuilding and increment count."""
        building = initialized_builder.add_building("House1", simple_square_polygon, 10.0)
        assert isinstance(building, IFCBuilding)
        assert building.name == "House1"
        assert initialized_builder.get_building_count() == 1

    def test_add_building_zero_height(self, initialized_builder, simple_square_polygon):
        """Zero height should raise IFCBuildError."""
        with pytest.raises(IFCBuildError, match="height"):
            initialized_builder.add_building("Bad", simple_square_polygon, 0.0)

    def test_add_building_negative_height(self, initialized_builder, simple_square_polygon):
        """Negative height should raise IFCBuildError."""
        with pytest.raises(IFCBuildError):
            initialized_builder.add_building("Bad", simple_square_polygon, -5.0)

    def test_add_building_too_few_footprint_points(self, initialized_builder):
        """Footprint with fewer than 3 points should raise IFCBuildError."""
        with pytest.raises(IFCBuildError, match="3 points"):
            initialized_builder.add_building("Bad", [(0, 0), (1, 1)], 10.0)

    def test_multiple_buildings(self, initialized_builder, simple_square_polygon):
        """Multiple buildings can be added."""
        initialized_builder.add_building("A", simple_square_polygon, 5.0)
        initialized_builder.add_building("B", simple_square_polygon, 8.0)
        initialized_builder.add_building("C", simple_square_polygon, 12.0)
        assert initialized_builder.get_building_count() == 3

    def test_save_no_ifcopenshell(self, initialized_builder):
        """Missing ifcopenshell should raise IFCBuildError."""
        with patch.dict("sys.modules", {"ifcopenshell": None}):
            with pytest.raises(IFCBuildError, match="ifcopenshell"):
                initialized_builder.save("/tmp/test.ifc")

    def test_save_without_project_raises(self, ifc_builder):
        """save() before create_project() should raise IFCBuildError."""
        with pytest.raises(IFCBuildError, match="not initialized"):
            ifc_builder.save("/tmp/test.ifc")

    def test_generate_ifc_content(self, initialized_builder, simple_square_polygon):
        """generate_ifc_content should return valid IFC header."""
        initialized_builder.add_building("B1", simple_square_polygon, 10.0)
        content = initialized_builder.generate_ifc_content()
        assert "ISO-10303-21" in content
        assert "IFC4" in content
        assert "TestProject" in content

    def test_generate_ifc_without_project_raises(self, ifc_builder):
        """generate_ifc_content without project should raise IFCBuildError."""
        with pytest.raises(IFCBuildError, match="not initialized"):
            ifc_builder.generate_ifc_content()


class TestIFCBuilding:
    def test_add_storey(self):
        """add_storey should append and return IFCStorey."""
        building = IFCBuilding("TestBuilding", [(0,0),(1,0),(1,1),(0,1)], 10.0)
        storey = building.add_storey("Ground Floor", 0.0, 3.0)
        assert isinstance(storey, IFCStorey)
        assert building.get_storey_count() == 1
        assert storey.name == "Ground Floor"

    def test_multiple_storeys(self):
        """Multiple storeys can be added."""
        building = IFCBuilding("B", [(0,0),(1,0),(1,1),(0,1)], 10.0)
        building.add_storey("GF", 0.0, 3.0)
        building.add_storey("1F", 3.0, 3.0)
        building.add_storey("2F", 6.0, 3.0)
        assert building.get_storey_count() == 3
