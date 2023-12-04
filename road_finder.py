from osgeo import gdal
from fiona.crs import from_epsg
from shapely.geometry import mapping, Point
import fiona
from qgis.analysis import QgsNativeAlgorithms
from qgis.core import (
    QgsApplication, QgsProject, QgsField, QgsFeature, QgsVectorLayer, QgsVectorFileWriter,
)
from PyQt5.QtCore import QVariant
import processing

# Set up the QGIS Application
QgsApplication.setPrefixPath("C:/OSGeo4W/apps/qgis", True)
qgs = QgsApplication([], False)
qgs.initQgis()

# Initialize the Processing framework
import processing
# from processing.tools import general as qgsprocessing

# processing.core.Processing.initialize()
QgsApplication.processingRegistry()
qgs.processingRegistry().addProvider(QgsNativeAlgorithms())

# Open the raster file
raster_ds = gdal.Open("D:/Destination/Projects_Civil3D/23-1820_test231121/gis/GEOREF_RASTER/1820_SLOPE(DEGREE).tif", gdal.GA_ReadOnly)

# Get raster georeference info
transform = raster_ds.GetGeoTransform()
xOrigin = transform[0]
yOrigin = transform[3]
pixelWidth = transform[1]
pixelHeight = -transform[5]

# Get the first raster band (assuming the slope is a single-band raster)
band = raster_ds.GetRasterBand(1)
raster_array = band.ReadAsArray()

# Prepare the output shapefile
schema = {
    'geometry': 'Point',
    'properties': {'Value': 'float'},
}
road_finder_path = "D:/Destination/Projects_Civil3D/23-1820_test231121/gis/GEOREF_RASTER/ROAD_FINDER/"
crs = from_epsg(26910)  # Replace with the correct EPSG code for your raster
output_shp_path = f"{road_finder_path}OUTPUT_POINTS_0-24.shp"
output_shp_path_24_32 = f"{road_finder_path}OUTPUT_POINTS_24-32.shp"
output_shp_path_32_40 = f"{road_finder_path}OUTPUT_POINTS_32-40.shp"
output_shp_path_40_45 = f"{road_finder_path}OUTPUT_POINTS_40-45.shp"
output_shp_path_45 = f"{road_finder_path}OUTPUT_POINTS_45.shp"
streams_shp = f"D:/Destination/Projects_Civil3D/23-1820_test231121/gis/PROJECT SHAPEFILES/1820_Streams-2225.shp"
output_road_points_path = f"{road_finder_path}GENERATED ROAD POINTS.shp"

# Function to write points to shapefile based on a value range
def write_points_to_shapefile(raster_array, value_range, output_path, crs, schema, x_origin, y_origin, pixel_width,
                              pixel_height):
    with fiona.open(output_path, 'w', driver='ESRI Shapefile', crs=crs, schema=schema) as output_shp:
        for row in range(raster_array.shape[0]):
            for col in range(raster_array.shape[1]):
                value = raster_array[row, col]
                if value_range[0] <= value < value_range[1]:
                    x = x_origin + col * pixel_width + (pixel_width / 2.0)
                    y = y_origin - (row * pixel_height) + (pixel_height / 2.0)
                    point = Point(x, y)
                    output_shp.write({
                        'geometry': mapping(point),
                        'properties': {'Value': float(value)},
                    })


# Example usage of the function
write_points_to_shapefile(raster_array, (0, 24), output_shp_path, crs, schema, xOrigin, yOrigin, pixelWidth,
                          pixelHeight)
write_points_to_shapefile(raster_array, (24, 32), output_shp_path_24_32, crs, schema, xOrigin, yOrigin, pixelWidth,
                          pixelHeight)
write_points_to_shapefile(raster_array, (32, 40), output_shp_path_32_40, crs, schema, xOrigin, yOrigin, pixelWidth,
                          pixelHeight)
write_points_to_shapefile(raster_array, (40, 45), output_shp_path_40_45, crs, schema, xOrigin, yOrigin, pixelWidth,
                          pixelHeight)
write_points_to_shapefile(raster_array, (0, 45), output_shp_path_45, crs, schema, xOrigin, yOrigin, pixelWidth,
                          pixelHeight)

# Loading layers and processing
points_layer = QgsVectorLayer(output_shp_path_45, 'points', 'ogr')
streams_layer = QgsVectorLayer(streams_shp, 'streams', 'ogr')
QgsProject.instance().addMapLayer(points_layer)
QgsProject.instance().addMapLayer(streams_layer)

# Create a buffer around streams to exclude points within this buffer
buffer_distance = 10  # adjust the distance according to your CRS and requirements
params = {
    'INPUT': streams_layer,
    'DISTANCE': buffer_distance,
    'OUTPUT': 'memory:'
}
buffer_result = processing.run("native:buffer", params)
buffer_layer = buffer_result['OUTPUT']

# Perform a spatial query to select points outside the buffer
params = {
    'INPUT': points_layer,
    'PREDICATE': [6],  # 6 corresponds to disjoint, meaning outside the buffer
    'INTERSECT': buffer_layer,
    'METHOD': 0  # creating new selection
}
selected_points_result = processing.run("qgis:selectbylocation", params)
selected_points_layer = selected_points_result['OUTPUT']

# Now you can iterate over selected features to process them further
# Create a new layer for potential road points
crs = points_layer.crs().toWkt()
road_points_layer = QgsVectorLayer(f'Point?crs={crs}', 'PotentialRoadPoints', 'memory')
prov = road_points_layer.dataProvider()
prov.addAttributes([QgsField('Value', QVariant.Double)])
road_points_layer.updateFields()

# Add selected points to the new layer
for feature in selected_points_layer.getFeatures():
    new_feat = QgsFeature()
    new_feat.setGeometry(feature.geometry())
    new_feat.setAttributes([feature['Value']])
    prov.addFeature(new_feat)

# Add the potential road points layer to the project
QgsProject.instance().addMapLayer(road_points_layer)

# Save the potential road points layer to a new shapefile
error = QgsVectorFileWriter.writeAsVectorFormat(road_points_layer, output_road_points_path, 'UTF-8', driverName='ESRI Shapefile')
if error[0] == QgsVectorFileWriter.NoError:
    print("Success! Shapefile created.")
else:
    print(f"Error: could not create shapefile due to {error}.")

qgs.exitQgis()
