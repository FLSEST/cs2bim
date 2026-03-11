"""Module defining rectangle cross-section geometry."""
import logging

from core.ifc.model.extrusion.cross_section import CrossSection

logger = logging.getLogger(__name__)


class Rectangle(CrossSection):
    """Represents a rectangular cross-section for extrusion."""

    def __init__(self, width: float, height: float):
        super().__init__()
        self.width = width
        self.height = height
