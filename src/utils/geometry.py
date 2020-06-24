"""
This module provides various functions for manipulating objects and data frames with geometry.
Supported features include e.g. reprojection, finding nearest point on a line and transforming geometries.

"""

from typing import List, Set, Dict, Tuple
import pyproj
from pyproj import CRS
from shapely.geometry import Point, LineString
from shapely.ops import split, snap, transform

def get_xy_from_geom(geom: Point) -> Dict[str, float]:
    return { 'x': geom.x, 'y': geom.y }

def get_coords_from_lat_lon(latLon: Dict[str, float]) -> List[float]:
    return [latLon['lon'], latLon['lat']]

def get_point_from_lat_lon(latLon: Dict[str, float]) -> Point:
    return Point(get_coords_from_lat_lon(latLon))

def round_coordinates(coords_list: List[tuple], digits=6) -> List[tuple]:
    return [ (round(coords[0], digits), round(coords[1], digits)) for coords in coords_list]

__projections = {
    (4326, 3879): pyproj.Transformer.from_crs(
        crs_from=CRS('epsg:4326'), 
        crs_to=CRS('epsg:3879'),
        always_xy=True),
    (3879, 4326): pyproj.Transformer.from_crs(
        crs_from=CRS('epsg:3879'), 
        crs_to=CRS('epsg:4326'),
        always_xy=True)
}

def project_geom(geom, geom_epsg: int = 4326, to_epsg: int = 3879):
    """Projects Shapely geometry object (e.g. Point or LineString) to another CRS. 
    The default conversion is from EPSG 4326 to 3879.
    """
    project = __projections[(geom_epsg, to_epsg)]
    return transform(project.transform, geom)

def get_split_lines(line: LineString, point: Point, tolerance: float) -> List[LineString]:
    """Splits a line at nearest intersecting point.
    Returns:
        A list containing two LineString objects.
    """
    snap_line = snap(line, point, tolerance)
    split_lines = split(snap_line, point)
    if (len(split_lines) == 1):
        raise ValueError('Split lines to only one line instead of 2 - split point was probably not on the line')
    return split_lines

def split_line_at_point(point_1, point_2, line_geom: LineString, split_point: Point, tolerance = 0.01) -> Tuple[LineString]:
    """Splits the line geometry of an edge to two parts at the location of a new node. Split parts can subsequently be used as linking edges 
    that connect the new node to the graph.

    Returns:
        Tuple containing the geometries of the link edges (LineString, LineString).
    """
    edge_first_p = Point(line_geom.coords[0])
    # split edge at new node to two line geometries
    split_lines = get_split_lines(line_geom, split_point, tolerance)
    if(edge_first_p.distance(point_1) < edge_first_p.distance(point_2)):
        link1 = split_lines[0]
        link2 = split_lines[1]
    else:
        link1 = split_lines[1]
        link2 = split_lines[0]
    return link1, link2
