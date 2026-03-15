"""Module defining the IfcVersion enumeration for supported IFC schema versions."""
from enum import Enum


class IfcVersion(Enum):
    """Supported Ifc versions"""

    IFC4 = "IFC4"
    IFC4X3_ADD2 = "IFC4X3_ADD2"
