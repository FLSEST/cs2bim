"""
This module contains wrapper functions to simplify the process of building
an ifc using ifcopenshells "create_entity" function.
"""

import math
import datetime
import logging
from ifcopenshell import file, entity_instance, guid
from shapely import Point

from config.configuration import Color, config
from core.ifc.model.ifc_version import IfcVersion
from i18n.language import Language
from i18n.translator import Translator

logger = logging.getLogger(__name__)


class IfcFile:
    """Wraps an ifcopenshell file and exposes factory methods for creating IFC entities."""

    def __init__(self, schema: IfcVersion, file_name: str, language: Language):
        """Initialize an IFC file with the given schema, file name, and output language."""
        self.schema = schema
        self.file = file(schema=schema.value)
        self.file.header.file_name.name = file_name
        self.file.header.file_name.author = [config.ifc.author]
        self.file.header.file_name.organization = [config.ifc.author]
        self.translator = Translator()
        self.language = language

    def write(self, path: str):
        """Write the IFC file to the given file system path."""
        self.file.write(path)

    def create_ifc_cartesian_point(self, point: Point) -> entity_instance:
        """Create an IfcCartesianPoint entity from a Shapely point."""
        return self.file.create_entity("IfcCartesianPoint", Coordinates=point.coords[0])

    def create_ifc_owner_history(self, name: str, version: str, application_full_name: str) -> entity_instance:
        """Create an IfcOwnerHistory entity with person, organization, and application metadata."""
        the_person = self.file.create_entity("IfcPerson", GivenName=name)
        the_organization = self.file.create_entity("IfcOrganization", Name=name)
        owning_user = self.file.create_entity(
            "IfcPersonAndOrganization", ThePerson=the_person, TheOrganization=the_organization
        )
        owning_application = self.file.create_entity(
            "IfcApplication",
            ApplicationDeveloper=the_organization,
            Version=version,
            ApplicationFullName=application_full_name,
            ApplicationIdentifier=application_full_name,
        )
        timestamp = int(datetime.datetime.now().timestamp())
        return self.file.create_entity(
            "IfcOwnerHistory",
            OwningUser=owning_user,
            OwningApplication=owning_application,
            ChangeAction="ADDED",
            LastModifiedDate=timestamp,
            CreationDate=timestamp,
        )

    def create_ifc_si_unit(self, unit_type: str, name: str) -> entity_instance:
        """Create an IfcSIUnit entity for the given unit type and SI unit name."""
        return self.file.create_entity("IfcSIUnit", UnitType=unit_type, Name=name)

    def create_ifc_unit_assignment(
            self,
            length_unit: entity_instance,
            area_unit: entity_instance,
            volume_unit: entity_instance,
            degree_unit: entity_instance,
    ) -> entity_instance:
        """Create an IfcUnitAssignment combining length, area, volume, and plane angle units."""
        plane_angle_measure = self.file.create_entity("IfcPlaneAngleMeasure", 0.017453292519943295)
        conversion_factor = self.file.create_entity(
            "IfcMeasureWithUnit", ValueComponent=plane_angle_measure, UnitComponent=degree_unit
        )
        dimensions = self.file.create_entity(
            "IfcDimensionalExponents",
            LengthExponent=0,
            MassExponent=0,
            TimeExponent=0,
            ElectricCurrentExponent=0,
            ThermodynamicTemperatureExponent=0,
            AmountOfSubstanceExponent=0,
            LuminousIntensityExponent=0,
        )
        conversion_based_unit = self.file.create_entity(
            "IfcConversionBasedUnit",
            Dimensions=dimensions,
            UnitType="PLANEANGLEUNIT",
            Name="DEGREE",
            ConversionFactor=conversion_factor,
        )
        return self.file.create_entity(
            "IfcUnitAssignment", Units=[length_unit, area_unit, volume_unit, conversion_based_unit]
        )

    def create_ifc_geometric_representation_context(self, location_coordinates: Point) -> entity_instance:
        """Create a 3D IfcGeometricRepresentationContext anchored at the given location."""
        location = self.create_ifc_cartesian_point(location_coordinates)
        world_coordinate_system = self.file.create_entity("IfcAxis2Placement3D", Location=location)
        return self.file.create_entity(
            "IfcGeometricRepresentationContext",
            ContextType="Model",
            CoordinateSpaceDimension=3,
            Precision=1e-05,
            WorldCoordinateSystem=world_coordinate_system,
        )

    def create_ifc_geometric_representation_sub_context(
            self, geometric_representation_context: entity_instance
    ) -> entity_instance:
        """Create a Body model-view sub-context for the given geometric representation context."""
        return self.file.create_entity(
            "IfcGeometricRepresentationSubContext",
            ContextIdentifier="Body",
            ContextType="Model",
            ParentContext=geometric_representation_context,
            TargetView="MODEL_VIEW",
        )

    def create_ifc_map_conversion(
            self,
            map_unit: entity_instance,
            source_crs: entity_instance,
            origin: Point,
    ) -> entity_instance:
        """Create an IfcMapConversion linking the model CRS to the configured projected CRS at the given origin."""
        target_crs = self.file.create_entity(
            "IfcProjectedCRS",
            Name=config.ifc.coordinate_reference_system.epsg_code,
            Description=config.ifc.coordinate_reference_system.description,
            GeodeticDatum=config.ifc.coordinate_reference_system.geodetic_datum,
            VerticalDatum=config.ifc.coordinate_reference_system.vertical_datum,
            MapUnit=map_unit,
        )
        return self.file.create_entity(
            "IfcMapConversion",
            SourceCRS=source_crs,
            TargetCRS=target_crs,
            Eastings=origin.x,
            Northings=origin.y,
            OrthogonalHeight=origin.z,
            XAxisAbscissa=1,
            XAxisOrdinate=0,
        )

    def create_ifc_project(
            self,
            name: str,
            owner_history: entity_instance,
            representation_context: entity_instance,
            units_in_context: entity_instance,
    ) -> entity_instance:
        """Create the root IfcProject entity with owner history, representation context, and unit assignment."""
        return self.file.create_entity(
            "IfcProject",
            Name=name,
            GlobalId=guid.new(),
            OwnerHistory=owner_history,
            RepresentationContexts=[representation_context],
            UnitsInContext=units_in_context,
        )

    def create_ifc_local_placement(self, location_coordinates: Point) -> entity_instance:
        """Create an absolute IfcLocalPlacement at the given coordinates."""
        location = self.create_ifc_cartesian_point(location_coordinates)
        relative_placement = self.file.create_entity("IfcAxis2Placement3D", Location=location)
        return self.file.create_entity("IfcLocalPlacement", RelativePlacement=relative_placement)

    def create_relative_ifc_local_placement(self, placement_rel_to: entity_instance,
                                            location_coordinates: Point) -> entity_instance:
        """Create an IfcLocalPlacement relative to an existing placement at the given offset coordinates."""
        location = self.create_ifc_cartesian_point(location_coordinates)
        relative_placement = self.file.create_entity("IfcAxis2Placement3D", Location=location)
        return self.file.create_entity("IfcLocalPlacement",
                                       PlacementRelTo=placement_rel_to,
                                       RelativePlacement=relative_placement)

    def create_ifc_rel_aggregates(
            self, relating_object: entity_instance, related_objects: list[entity_instance]
    ) -> entity_instance:
        """Create an IfcRelAggregates relationship between a parent object and a list of child objects."""
        return self.file.create_entity(
            "IfcRelAggregates",
            GlobalId=guid.new(),
            RelatingObject=relating_object,
            RelatedObjects=related_objects,
        )

    def create_ifc_rel_contained_in_spatial_structure(self, related_elements: list[entity_instance],
                                                      relating_structure: entity_instance) -> entity_instance:
        """Create an IfcRelContainedInSpatialStructure relationship between elements and a spatial structure."""
        return self.file.create_entity(
            "IfcRelContainedInSpatialStructure",
            GlobalId=guid.new(),
            RelatedElements=related_elements,
            RelatingStructure=relating_structure,
        )

    def create_ifc_rel_defines_by_type(self, related_objects, relating_type) -> entity_instance:
        """Create an IfcRelDefinesByType relationship linking element instances to a type definition."""
        return self.file.create_entity(
            "IfcRelDefinesByType",
            GlobalId=guid.new(),
            RelatedObjects=related_objects,
            RelatingType=relating_type,
        )

    def create_ifc_group(self, entity_type: str, name: str) -> entity_instance:
        """Create a named IFC group entity, normalizing entity type between IFC4 and IFC4X3_ADD2 schemas."""
        if self.schema == IfcVersion.IFC4 and entity_type == "IfcBuiltSystem":
            entity_type = "IfcBuildingSystem"
        if self.schema == IfcVersion.IFC4X3_ADD2 and entity_type == "IfcBuildingSystem":
            entity_type = "IfcBuiltSystem"
        return self.file.create_entity(entity_type, GlobalId=guid.new(),
                                       Name=self.translator.translate(name, self.language))

    def create_ifc_rel_assigns_to_group(
            self, related_objects: list[entity_instance], group: entity_instance
    ) -> entity_instance:
        """Create an IfcRelAssignsToGroup relationship assigning objects to a group."""
        return self.file.create_entity(
            "IfcRelAssignsToGroup", GlobalId=guid.new(), RelatedObjects=related_objects, RelatingGroup=group
        )

    def create_ifc_poly_loop(self, polygon: list[entity_instance]) -> entity_instance:
        """Create an IfcPolyLoop from a list of cartesian point entities."""
        return self.file.create_entity("IfcPolyLoop", Polygon=polygon)

    def create_ifc_face(self, exterior_poly_loop: entity_instance,
                        interior_poly_loops: list[entity_instance]) -> entity_instance:
        """Create an IfcFace with an outer boundary and optional inner void boundaries."""
        outer_bound = self.file.create_entity("IfcFaceOuterBound", Bound=exterior_poly_loop, Orientation=True)
        inner_bounds = []
        if interior_poly_loops:
            for interior_poly_loop in interior_poly_loops:
                inner_bound = self.file.create_entity("IfcFaceBound", Bound=interior_poly_loop, Orientation=False)
                inner_bounds.append(inner_bound)
        return self.file.create_entity("IfcFace", Bounds=[outer_bound] + inner_bounds)

    def create_ifc_faceted_brep(self, cfs_faces: list[entity_instance]) -> entity_instance:
        """Create an IfcFacetedBrep solid from a list of face entities."""
        outer = self.file.create_entity("IfcClosedShell", CfsFaces=cfs_faces)
        return self.file.create_entity("IfcFacetedBrep", Outer=outer)

    def create_ifc_faceted_brep_with_voids(self, outer_faces: list[entity_instance],
                                           void_faces_list: list[list[entity_instance]]) -> entity_instance:
        """Create an IfcFacetedBrepWithVoids solid with an outer shell and inner void shells."""
        outer = self.file.create_entity("IfcClosedShell", CfsFaces=outer_faces)
        voids = [self.file.create_entity("IfcClosedShell", CfsFaces=void_faces) for void_faces in void_faces_list]
        return self.file.create_entity("IfcFacetedBrepWithVoids", Outer=outer, Voids=voids)

    def create_ifc_triangulated_face_set(
            self, coord_list: list[Point], coord_index: list[tuple[int, int, int]]
    ) -> entity_instance:
        """Create an IfcTriangulatedFaceSet tessellation from coordinate points and triangle index triplets."""
        coordinates = self.file.create_entity("IfcCartesianPointList3D",
                                              CoordList=[coord.coords[0] for coord in coord_list])
        return self.file.create_entity("IfcTriangulatedFaceSet", Coordinates=coordinates, CoordIndex=coord_index)

    def create_ifc_polygonal_face_set(
            self, coord_list: list[Point], faces: list[entity_instance]
    ) -> entity_instance:
        """Create an IfcPolygonalFaceSet tessellation from coordinate points and face entities."""
        coordinates = self.file.create_entity("IfcCartesianPointList3D",
                                              CoordList=[coord.coords[0] for coord in coord_list])
        return self.file.create_entity("IfcPolygonalFaceSet", Coordinates=coordinates, Faces=faces)

    def create_ifc_indexed_polygonal_face(
            self, coord_index: list[tuple[int, int, int]]
    ) -> entity_instance:
        """Create an IfcIndexedPolygonalFace from coordinate index tuples."""
        return self.file.create_entity("IfcIndexedPolygonalFace", CoordIndex=coord_index)

    def create_ifc_indexed_polygonal_face_with_voids(
            self, coord_index: list[tuple[int, int, int]], inner_cord_indices: list[list[tuple[int, int, int]]]
    ) -> entity_instance:
        """Create an IfcIndexedPolygonalFaceWithVoids from outer and inner coordinate index lists."""
        return self.file.create_entity("IfcIndexedPolygonalFaceWithVoids", CoordList=coord_index,
                                       InnerCoordIndices=inner_cord_indices)

    def create_ifc_product_definition_shape(
            self, context_of_items: entity_instance, representation_type: str, items: list[entity_instance]
    ) -> entity_instance:
        """Create an IfcProductDefinitionShape wrapping a Body shape representation."""
        representation = self.file.create_entity(
            "IfcShapeRepresentation",
            ContextOfItems=context_of_items,
            RepresentationIdentifier="Body",
            RepresentationType=representation_type,
            Items=items
        )
        return self.file.create_entity("IfcProductDefinitionShape", Representations=[representation])

    def create_ifc_annotation(
            self, object_placement: entity_instance, representation: entity_instance
    ) -> entity_instance:
        """Create an IfcAnnotation element with the given placement and shape representation."""
        return self.file.create_entity(
            "IfcAnnotation", GlobalId=guid.new(), ObjectPlacement=object_placement, Representation=representation
        )

    def create_ifc_product(
            self, entity_type: str, object_placement: entity_instance,
            representation: entity_instance = None,
    ) -> entity_instance:
        """Create an IFC product entity of the specified type with optional shape representation."""
        if representation is None:
            return self.file.create_entity(entity_type, GlobalId=guid.new(), ObjectPlacement=object_placement)
        else:
            return self.file.create_entity(
                entity_type, GlobalId=guid.new(), Name="", ObjectPlacement=object_placement,
                Representation=representation
            )

    def create_ifc_type_product(self, entity_type: str) -> entity_instance:
        """Create an IFC type product entity of the specified type with a new global ID."""
        return self.file.create_entity(
            entity_type, GlobalId=guid.new()
        )

    def create_ifc_surface_style(self, color: Color) -> entity_instance:
        """Create an IfcSurfaceStyle with shading applied to both sides using the given color."""
        surface_colour = self.file.create_entity("IfcColourRgb", Red=color.r, Green=color.g, Blue=color.b)
        style = self.file.create_entity("IfcSurfaceStyleShading", SurfaceColour=surface_colour, Transparency=color.a)
        return self.file.create_entity("IfcSurfaceStyle", Side="BOTH", Styles=[style])

    def create_ifc_styled_item(self, item: entity_instance, style: entity_instance) -> entity_instance:
        """Create an IfcStyledItem associating a surface style with a representation item."""
        return self.file.create_entity("IfcStyledItem", Item=item, Styles=[style])

    def create_ifc_swept_disk_solid(self, directrix: entity_instance, radius: float) -> entity_instance:
        """Create an IfcSweptDiskSolid by sweeping a disk of given radius along a directrix curve."""
        return self.file.create_entity(
            "IfcSweptDiskSolid",
            Directrix=directrix,
            Radius=radius
        )

    def create_ifc_polyline(self, points: list[Point]) -> entity_instance:
        """Create an IfcPolyline from a list of Shapely points, closing loops without duplicating the last vertex."""
        if len(points) > 1 and points[0] == points[-1]:
            cartesian_points = [self.create_ifc_cartesian_point(point) for point in points[:-1]]
            cartesian_points.append(cartesian_points[0])
        else:
            cartesian_points = [self.create_ifc_cartesian_point(point) for point in points]
        return self.file.create_entity(
            "IfcPolyline",
            Points=cartesian_points
        )

    def create_ifc_arbitrary_closed_profile_def(self, outer_curve: list[Point]):
        """Create an IfcArbitraryClosedProfileDef from a list of points forming the outer boundary."""
        ifc_outer_curve = self.create_ifc_polyline(outer_curve)
        return self.file.create_entity(
            "IfcArbitraryClosedProfileDef",
            ProfileType="AREA",
            OuterCurve=ifc_outer_curve
        )

    def create_ifc_rectangle_profile_def(self, x_dim: float, y_dim: float) -> entity_instance:
        """Create an IfcRectangleProfileDef with the given x and y dimensions."""
        return self.file.create_entity(
            "IfcRectangleProfileDef",
            ProfileType="AREA",
            XDim=x_dim,
            YDim=y_dim
        )

    def create_ifc_circle_profile_def(self, radius: float) -> entity_instance:
        """Create an IfcCircleProfileDef with the given radius."""
        return self.file.create_entity(
            "IfcCircleProfileDef",
            ProfileType="AREA",
            Radius=radius
        )

    def create_ifc_sectioned_solid_horizontal(self, ifc_profile_def: entity_instance,
                                              directrix: entity_instance) -> entity_instance:
        """Create an IfcSectionedSolidHorizontal by applying a profile section along a directrix curve."""
        ifc_start_point = self.create_ifc_axis_2_placement_linear(
            self.create_ifc_point_by_distance_expression(0.0, directrix))
        ifc_end_point = self.create_ifc_axis_2_placement_linear(
            self.create_ifc_point_by_distance_expression(1.0, directrix))
        return self.file.create_entity(
            "IfcSectionedSolidHorizontal",
            Directrix=directrix,
            CrossSections=[ifc_profile_def, ifc_profile_def],
            CrossSectionPositions=[ifc_start_point, ifc_end_point]
        )

    def create_ifc_fixed_reference_swept_area_solid(self, ifc_profile_def: entity_instance, directrix: entity_instance):
        """Create an IfcFixedReferenceSweptAreaSolid sweeping a profile along a directrix with a fixed Z reference."""
        fixed_ref = self.file.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0))
        return self.file.create_entity("IfcFixedReferenceSweptAreaSolid",
                                       SweptArea=ifc_profile_def,
                                       Directrix=directrix,
                                       FixedReference=fixed_ref
                                       )

    def create_ifc_extruded_area_solid(self, ifc_profile_def: entity_instance,
                                       position: Point, depth: float, orientation: float):
        """Create an IfcExtrudedAreaSolid extruding a profile vertically by depth from the given position."""
        if orientation:
            angle_rad = math.radians(90.0 - orientation)
            x = math.cos(angle_rad)
            y = math.sin(angle_rad)
            ifc_direction_orientation = self.file.create_entity("IfcDirection", DirectionRatios=[x, y])
            ifc_axis_2_placement_3d = self.file.create_entity("IfcAxis2Placement3D",
                                                              Location=self.create_ifc_cartesian_point(position),
                                                              RefDirection=ifc_direction_orientation)
        else:
            ifc_axis_2_placement_3d = self.file.create_entity("IfcAxis2Placement3D",
                                                              Location=self.create_ifc_cartesian_point(position))
        ifc_direction = self.file.create_entity("IfcDirection", DirectionRatios=[0.0, 0.0, 1.0])
        return self.file.create_entity(
            "IfcExtrudedAreaSolid",
            SweptArea=ifc_profile_def,
            Position=ifc_axis_2_placement_3d,
            ExtrudedDirection=ifc_direction,
            Depth=depth
        )

    def create_ifc_axis_2_placement_linear(self, point: entity_instance):
        """Create an IfcAxis2PlacementLinear at the given point location."""
        return self.file.create_entity(
            "IfcAxis2PlacementLinear",
            Location=point
        )

    def create_ifc_point_by_distance_expression(self, distance_along: float, basis_curve: entity_instance):
        """Create an IfcPointByDistanceExpression at a fractional distance along a basis curve."""
        return self.file.create_entity(
            "IfcPointByDistanceExpression",
            DistanceAlong=self.file.createIfcParameterValue(distance_along),
            BasisCurve=basis_curve,
        )

    def create_ifc_property_single_value(self, name: str, text: str) -> entity_instance:
        """Create an IfcPropertySingleValue with a translated text name and value."""
        nominal_value = self.file.create_entity("IfcText", self.translator.translate(text, self.language))
        return self.file.create_entity("IfcPropertySingleValue", Name=self.translator.translate(name, self.language),
                                       NominalValue=nominal_value)

    def create_ifc_property_set(
            self, name: str, has_properties: list[entity_instance], related_object: entity_instance
    ) -> entity_instance:
        """Create an IfcPropertySet and link it to the related object via IfcRelDefinesByProperties."""
        relating_property_definition = self.file.create_entity(
            "IfcPropertySet", GlobalId=guid.new(), Name=self.translator.translate(name, self.language),
            HasProperties=has_properties
        )
        self.file.create_entity(
            "IfcRelDefinesByProperties",
            GlobalId=guid.new(),
            RelatedObjects=[related_object],
            RelatingPropertyDefinition=relating_property_definition,
        )
        return relating_property_definition

    def create_attribute(self, item: entity_instance, attribute, value):
        """Set a translated attribute value on an IFC entity instance if the attribute exists."""
        if hasattr(item, attribute):
            setattr(item, attribute, self.translator.translate(value, self.language))
