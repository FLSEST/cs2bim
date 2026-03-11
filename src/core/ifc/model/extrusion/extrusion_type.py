"""Module defining extrusion type enumeration."""
from enum import Enum


class ExtrusionType(Enum):
    """Enumeration of available extrusion types."""
    POLYLINE = "POLYLINE"
    SURFACE = "SURFACE"
    POINT = "POINT"
