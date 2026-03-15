"""Module defining the PropertySet data class for grouping IFC properties by name."""


class PropertySet:
    """Class holding a set of properties"""

    def __init__(self, name: str):
        """Initialize a PropertySet with the given name and an empty properties dictionary."""
        self.name = name
        self.properties: dict[str, str] = {}

    def add_property(self, key: str, value: str):
        """Add a property key-value pair, raising ValueError if the key already exists."""
        if key not in self.properties:
            self.properties[key] = value
        else:
            raise ValueError(f"Property {key} already exists")

    def __eq__(self, other):
        """Return True if the other PropertySet has the same name and properties."""
        if not isinstance(other, PropertySet):
            return False
        return self.name == other.name and self.properties == other.properties

    def __hash__(self):
        """Return a hash based on the name and sorted property items."""
        return hash((self.name, tuple(sorted(self.properties.items()))))

    def __repr__(self):
        """Return string representation."""
        return f"PropertySet(name={self.name!r}, properties={self.properties!r})"
