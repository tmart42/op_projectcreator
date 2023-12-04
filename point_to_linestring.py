from qgis.core import (
    QgsTask,
    QgsMessageLog,
    QgsFeatureRequest,
    QgsApplication,
    QgsFeature,
    QgsFields,
    QgsGeometry,
    QgsVectorLayer,
    QgsVectorFileWriter,
    QgsField,
    QgsSpatialIndex,
    QgsProject,
    QgsWkbTypes,
    QgsFeatureIterator,
    QgsFeatureSink,
    Qgis
)
from PyQt5.QtCore import QVariant
import logging

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelness)s - %(message)s')
logger = logging.getLogger(__name__)
logger.info("Script started")

qgs = QgsApplication([], False)
qgs.initQgis()

class CreateStreamLinesTask(QgsTask):
    def __init__(self, point_layer):
        super().__init__("Create Stream Lines Task", QgsTask.CanCancel)
        self.point_layer = point_layer
        self.linestring_layer = None
        self.exception = None
        self.output_path = "D:/Source/DEM_Files/StreamExtractionTests/HumCoStreams_Final.shp"
        self.output_geojson_path = "D:/Source/DEM_Files/StreamExtractionTests/HumCoStreams_Final.geojson"

    def run(self):
        logger.info("Run method begins...")
        try:
            # Prepare spatial index for faster lookup
            spatial_index = QgsSpatialIndex()
            for f in self.point_layer.getFeatures():
                spatial_index.addFeature(f)
            logger.info("Spatial index created")

            already_connected = set()
            features = []

            # Create the linestring layer
            crs = self.point_layer.crs().toWkt()
            self.linestring_layer = QgsVectorLayer(
                'LineString?crs=' + crs, 'stream_lines', 'memory'
            )
            provider = self.linestring_layer.dataProvider()
            provider.addAttributes([
                QgsField('id', QVariant.Int)
            ])
            self.linestring_layer.updateFields()
            logger.info("linestring layer created")

            # Process each feature
            for current_feature in self.point_layer.getFeatures():
                current_id = current_feature.id()
                if current_id in already_connected:
                    continue
                logger.info("Feature {} processing...".format(current_id))

                # Build a line connecting points
                line_points = [current_feature.geometry().asPoint()]
                already_connected.add(current_id)

                MAX_DISTANCE = 3  # Maximum distance in CRS units (change if CRS is not in feet)

                next_id = current_id

                while next_id is not None:
                    # Retrieve the 10 nearest points
                    nearest_ids = spatial_index.nearestNeighbor(line_points[-1], 10)
                    nearest_id = None
                    min_distance = float('inf')

                    for nid in nearest_ids:
                        if nid == next_id or nid in already_connected:
                            continue
                        candidate_feature = self.point_layer.getFeature(nid)
                        if candidate_feature is None:
                            continue
                        candidate_point = candidate_feature.geometry().asPoint()
                        distance = line_points[-1].distance(candidate_point)
                        if distance < MAX_DISTANCE and distance < min_distance:
                            nearest_id = nid
                            min_distance = distance

                    next_id = nearest_id
                    if next_id is not None:
                        already_connected.add(next_id)
                        next_feature = self.point_layer.getFeature(next_id)
                        line_points.append(next_feature.geometry().asPoint())

                # Create a linestring feature
                if len(line_points) > 1:  # Avoid single-point lines
                    line_feature = QgsFeature()
                    line_feature.setGeometry(QgsGeometry.fromPolylineXY(line_points))
                    line_feature.setAttributes([current_id])
                    features.append(line_feature)

                # Update task progress
                self.setProgress(len(already_connected) / self.point_layer.featureCount() * 100)
            logger.info("Processing finished")

            # Add features to the linestring layer
            provider.addFeatures(features)
            self.linestring_layer.updateExtents()
            logger.info("Features added")

            # After processing, write the output to a file
            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = "ESRI Shapefile"
            options.fileEncoding = "UTF-8"

            QgsVectorFileWriter.writeAsVectorFormatV3(
                self.linestring_layer,
                self.output_path,
                QgsProject.instance().transformContext(),
                options
            )
            logger.info("Shapefile written")

            return True

        except Exception as e:
            self.exception = e
            logger.error("Error writing output file")
            logger.error(e)
            return False

    def finished(self, successful):
        if successful and self.linestring_layer:
            QgsProject.instance().addMapLayer(self.linestring_layer)
            logger.info("Stream linestring layer added to project")

            QgsMessageLog.logMessage(
                f"Stream linestring creation completed. Layer '{self.linestring_layer.name()}' with {len(self.linestring_layer.featureCount())} features added.",
                level=Qgis.Info
            )
        elif self.exception:
            logger.error(self.exception)
            QgsMessageLog.logMessage(f"Error: {self.exception}", level=Qgis.Critical)

# Assuming 'point_layer' is a QgsVectorLayer of stream points


layer_path = "D:/Source/DEM_Files/StreamExtractionTests/Smaller Sample_231104-2223.shp"

point_layer = QgsVectorLayer(layer_path, 'stream_points', 'ogr')
logger.debug("Loaded point layer")

task = CreateStreamLinesTask(point_layer)
QgsApplication.taskManager().addTask(task)
qgs.exitQgis()



def point_to_line(source_layer, line_layer):
    """
    Create a line layer from a point layer.
    """
    source_orderby_request = QgsFeatureRequest()

    source_layer_idx = QgsSpatialIndex(source_layer.getFeatures(), flags=QgsSpatialIndex.FlagStoreFeatureGeometries)

    output_layer_fields = QgsFields()
    output_layer_fields.append(QgsField('path_group_id', QVariant.Int))
    output_layer_fields.append(QgsField('path_group_name', QVariant.String))
    output_layer_fields.append(QgsField('path_n_vertices', QVariant.Int))
    output_layer_fields.append(QgsField('path_length', QVariant.Double))
    output_layer_fields.append(QgsField('path_begin_fid', QVariant.Int))
    output_layer_fields.append(QgsField('path_begin_cid', QVariant.String))
    output_layer_fields.append(QgsField('path_end_fid', QVariant.Int))
    output_layer_fields.append(QgsField('path_end_cid', QVariant.String))

    (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context,
                                           output_layer_fields, QgsWkbTypes.LineString,
                                           crs=source_layer.sourceCrs())

    points_skip = []
    path_group_id = 1

    max_dist = 5
    max_points = 10000
    source_layer_feature_count = source_layer.featureCount()
    invalid_paths = 0
    handle_invalid = 1
    groupby_expr = False

    for source_feat in source_layer.getFeatures(source_orderby_request):
        if source_feat.id() in points_skip:
            continue

        new_geom = [source_feat.geometry().centroid().asPoint()]
        new_begin = source_feat.id()
        new_end = source_feat.id()
        group = source_feat.id()

        search_from_point_geom = source_feat.geometry().centroid()
        search_from_point_id = source_feat.id()
        no_further_matches = False


        points_skip.append(source_feat.id())

        allow_self_crossing = False

        for i in range(0, source_layer_feature_count + 1):

            if no_further_matches:
                break
            if len(new_geom) >= max_points:
                break
            nearest_neighbors = source_layer_idx.nearestNeighbor(search_from_point_geom.asPoint(), neighbors=-1,
                                                                 maxDistance=max_dist)
            nearest_neighbors.remove(search_from_point_id)
            for j, neighbor_id in enumerate(nearest_neighbors):
                if neighbor_id in points_skip:
                    continue
                neighbor_geom = source_layer_idx.geometry(neighbor_id)
                neighbor_geom = neighbor_geom.centroid()
                if not allow_self_crossing:
                    current_geom = QgsGeometry.fromPolylineXY(new_geom)
                    planned_geom = QgsGeometry.fromPolylineXY([new_geom[-1], neighbor_geom.asPoint()])
                    if current_geom.crosses(planned_geom):
                        continue
                new_end = neighbor_id
                new_geom.append(neighbor_geom.asPoint())
                search_from_point_geom = neighbor_geom
                search_from_point_id = neighbor_id
                points_skip.append(neighbor_id)
                break
            else:
                no_further_matches = True

            if len(new_geom) < 2:
                invalid_paths += 1
                if handle_invalid == 0:
                    new_geom.append(
                        source_feat.geometry().centroid().asPoint())  # will likely create invalid geometry, but should the feature be skipped instead?
                elif handle_invalid == 1:
                    continue
            new_feat = QgsFeature(output_layer_fields)
            new_feat.setGeometry(QgsGeometry.fromPolylineXY(new_geom))
            new_feat['path_group_id'] = path_group_id
            new_feat['path_group_name'] = str(group)
            new_feat['path_n_vertices'] = len(new_geom)
            new_feat['path_length'] = QgsGeometry.fromPolylineXY(new_geom).length()
            new_feat['path_begin_fid'] = new_begin
            new_feat['path_end_fid'] = new_end

            sink.addFeature(new_feat, QgsFeatureSink.FastInsert)
            path_group_id += 1

        if handle_invalid == 0 and invalid_paths > 0:

        elif handle_invalid == 1 and invalid_paths > 0:

        return {self.OUTPUT: dest_id}