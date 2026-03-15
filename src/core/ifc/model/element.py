"""Module defining the Element base class for holding IFC attributes and property sets."""
from typing import Any

from ifcopenshell import entity_instance

from core.ifc.ifc_file import IfcFile
from core.ifc.model.property_set import PropertySet


class Element:
    """Base class for IFC model elements, managing attributes and grouped property sets."""

    def __init__(self):
        """Initialize an Element with empty attributes and property sets."""
        self.attributes = {}
        self.property_sets = {}

    def add_property(self, property_set: str, key: str, value: Any):
        """Add a property to the named property set, creating the set if it does not yet exist."""
        if property_set not in self.property_sets:
            self.property_sets[property_set] = PropertySet(property_set)
        self.property_sets[property_set].add_property(key, str(value))

    def add_attribute(self, name: str, value: Any):
        """Add a named attribute, raising ValueError if the attribute already exists."""
        if name not in self.attributes:
            self.attributes[name] = value
        else:
            raise ValueError(f"Attribute {name} already exists")

    def set_ifc_properties(self, ifc_file: IfcFile, ifc_element: entity_instance):
        """Write all property sets and their values to the IFC file for the given IFC element."""
        for property_set in self.property_sets.values():
            ifc_property_single_values = []
            for key, value in property_set.properties.items():
                ifc_property_single_values.append(ifc_file.create_ifc_property_single_value(key, value))
            ifc_file.create_ifc_property_set(property_set.name, ifc_property_single_values, ifc_element)

    def set_ifc_attributes(self, ifc_file: IfcFile, ifc_element: entity_instance):
        """Write all attributes to the IFC file for the given IFC element."""
        for attribute, value in self.attributes.items():
            ifc_file.create_attribute(ifc_element, attribute, value)

    def __eq__(self, other: Any) -> bool:
        """Return True if the other Element has equal attributes and property sets."""
        if not isinstance(other, Element):
            return False
        return self.attributes == other.attributes and self.property_sets == other.property_sets

    def __hash__(self) -> int:
        """Return a hash based on sorted attributes and property set hashes."""
        return hash((
            tuple(sorted(self.attributes.items())),
            tuple(sorted((name, hash(ps)) for name, ps in self.property_sets.items()))
        ))

    def __repr__(self) -> str:
        """Return string representation."""
        return f"Element(attributes={self.attributes!r}, " f"property_sets={list(self.property_sets.keys())!r})"
