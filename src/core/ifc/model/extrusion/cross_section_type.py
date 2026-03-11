"""Module defining cross-section type enumeration."""
from enum import Enum


class CrossSectionType(Enum):
    """Enumeration of available cross-section types."""
    CIRCLE = "CIRCLE"
    EGG = "EGG"
    RECTANGLE = "RECTANGLE"
    POLYGON_LOCAL = "POLYGON_LOCAL"
    POLYGON_GLOBAL = "POLYGON_GLOBAL"
