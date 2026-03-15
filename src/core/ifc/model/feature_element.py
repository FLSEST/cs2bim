"""Module defining FeatureElement, extending Element with type, spatial structure, and group support."""
from core.ifc.model.element import Element


class FeatureElement(Element):
    """An IFC element with an optional element type, spatial structure, and group memberships."""

    def __init__(self):
        """Initialize a FeatureElement with no element type, spatial structure, or groups."""
        super().__init__()
        self.element_type = None
        self.spatial_structure = None
        self.groups = []

    def add_group(self, name: str):
        """Add a group name to this element if it is not already present."""
        if name not in self.groups:
            self.groups.append(name)
