import geopandas as gpd
from shapely.geometry import LineString, Point
import numpy as np
from scipy.spatial import cKDTree

layer_path = "D:/Source/DEM_Files/StreamExtractionTests/PixelToPoints_231104_try2-2225.shp"
output_filepath = "D:/Source/DEM_Files/StreamExtractionTests/FINAL STREAMS-2225.shp"


# Load the point shapefile
gdf_points = gpd.read_file(layer_path)

# Ensure the geometry type is Point
gdf_points = gdf_points[gdf_points.geometry.type == 'Point']

# Convert the geometries to a 2D numpy array for cKDTree
coords = np.array(list(gdf_points.geometry.apply(lambda geom: (geom.x, geom.y))))

# Create a cKDTree for efficient spatial queries
tree = cKDTree(coords)

# Define the search radius in feet (since EPSG:2225 is in feet)
search_radius = 5  # 5 feet

# Initialize an empty list to hold the LineString geometries
linestring_geoms = []

# Keep track of points that are already connected
connected_points = set()

# Iterate over the points
for idx, point in enumerate(gdf_points.geometry):
    if idx not in connected_points:
        # Query the tree for the nearest point within the search radius
        distances, indices = tree.query([coords[idx]], k=2, distance_upper_bound=search_radius)

        # Skip if no neighbor within the radius
        if np.isinf(distances[0][1]):
            continue

        # Get the index of the closest point
        closest_idx = indices[0][1]

        # Check if the closest point is already connected
        if closest_idx in connected_points:
            continue

        # Create a LineString between the point and its closest neighbor
        linestring = LineString([point, gdf_points.geometry.iloc[closest_idx]])

        # Add the LineString to our list
        linestring_geoms.append(linestring)

        # Mark the points as connected
        connected_points.update([idx, closest_idx])

# Create a GeoDataFrame for the LineStrings
gdf_lines = gpd.GeoDataFrame(geometry=linestring_geoms)

# Set the CRS to EPSG:2225
gdf_lines.crs = "EPSG:2225"

# Output the LineStrings to a new shapefile
gdf_lines.to_file(output_filepath)
