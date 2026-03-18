"""Tests for cs2bim.geometry module."""
import math
import pytest
from cs2bim.geometry import (
    calculate_area,
    calculate_perimeter,
    centroid,
    transform_coordinates,
    extrude_polygon,
    distance,
    bounding_box,
)


class TestCalculateArea:
    def test_square_area(self, simple_square_polygon):
        """10x10 square should have area 100."""
        area = calculate_area(simple_square_polygon)
        assert abs(area - 100.0) < 1e-9

    def test_triangle_area(self, triangle_polygon):
        """Triangle with base 6, height 4 should have area 12."""
        area = calculate_area(triangle_polygon)
        assert abs(area - 12.0) < 1e-9

    def test_too_few_points(self):
        """Less than 3 points should raise ValueError."""
        with pytest.raises(ValueError, match="3 points"):
            calculate_area([(0, 0), (1, 1)])

    def test_area_is_positive(self):
        """Area should always be positive regardless of winding order."""
        cw = [(0, 0), (0, 10), (10, 10), (10, 0)]
        ccw = [(0, 0), (10, 0), (10, 10), (0, 10)]
        assert calculate_area(cw) > 0
        assert calculate_area(ccw) > 0


class TestCalculatePerimeter:
    def test_square_perimeter(self, simple_square_polygon):
        """10x10 square should have perimeter 40."""
        perimeter = calculate_perimeter(simple_square_polygon)
        assert abs(perimeter - 40.0) < 1e-9

    def test_too_few_points(self):
        """Less than 2 points should raise ValueError."""
        with pytest.raises(ValueError, match="2 points"):
            calculate_perimeter([(0, 0)])


class TestCentroid:
    def test_square_centroid(self, simple_square_polygon):
        """Centroid of 10x10 square at origin should be (5, 5)."""
        cx, cy = centroid(simple_square_polygon)
        assert abs(cx - 5.0) < 1e-9
        assert abs(cy - 5.0) < 1e-9

    def test_empty_polygon(self):
        """Empty polygon should raise ValueError."""
        with pytest.raises(ValueError):
            centroid([])


class TestTransformCoordinates:
    def test_basic_transform(self):
        """Subtract origin from point."""
        result = transform_coordinates((100.0, 200.0), (90.0, 190.0))
        assert result == (10.0, 10.0)

    def test_with_scale(self):
        """Scale factor should multiply the offset."""
        result = transform_coordinates((10.0, 20.0), (0.0, 0.0), scale=2.0)
        assert result == (20.0, 40.0)

    def test_identity_transform(self):
        """Subtracting self as origin should yield (0, 0)."""
        result = transform_coordinates((5.0, 5.0), (5.0, 5.0))
        assert result == (0.0, 0.0)


class TestExtrudePolygon:
    def test_basic_extrusion(self, simple_square_polygon):
        """Extruding square should give 8 points (4 bottom + 4 top)."""
        result = extrude_polygon(simple_square_polygon, 0.0, 10.0)
        assert len(result) == 8
        # Bottom ring at z=0
        assert all(p[2] == 0.0 for p in result[:4])
        # Top ring at z=10
        assert all(p[2] == 10.0 for p in result[4:])

    def test_roof_must_be_above_base(self):
        """roof_height <= base_height should raise ValueError."""
        with pytest.raises(ValueError, match="roof_height"):
            extrude_polygon([(0, 0), (1, 0), (1, 1)], 5.0, 3.0)


class TestDistance:
    def test_pythagorean(self):
        """3-4-5 triangle distance."""
        d = distance((0.0, 0.0), (3.0, 4.0))
        assert abs(d - 5.0) < 1e-9

    def test_same_point(self):
        """Distance from point to itself is 0."""
        assert distance((5.0, 5.0), (5.0, 5.0)) == 0.0


class TestBoundingBox:
    def test_square_bbox(self, simple_square_polygon):
        """Bounding box of 10x10 square at origin."""
        bbox = bounding_box(simple_square_polygon)
        assert bbox == (0.0, 0.0, 10.0, 10.0)

    def test_empty_polygon(self):
        """Empty polygon should raise ValueError."""
        with pytest.raises(ValueError):
            bounding_box([])
