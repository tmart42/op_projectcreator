import shutil
import json
import os
import re
import shutil
import time
import zipfile
from urllib.parse import unquote
import rasterio
import requests
from qgis import processing
from qgis.PyQt.QtCore import (
    pyqtSignal,
)
from qgis.PyQt.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QDesktopWidget,
    QDialog,
    QMessageBox,
    QHBoxLayout,
    QApplication,
    QPushButton,
    QSpacerItem,
    QSizePolicy
)
from qgis.core import (
    Qgis,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeature,
    QgsFeatureRequest,
    QgsGeometry,
    QgsLayerTreeLayer,
    QgsLayoutItemMap,
    QgsMessageLog,
    QgsProcessingFeedback,
    QgsRasterPipe,
    QgsRasterLayer,
    QgsRectangle,
    QgsRasterFileWriter,
    QgsTask,
    QgsVectorLayer,
    QgsVectorFileWriter,
    QgsWkbTypes,
)
from requests.exceptions import ChunkedEncodingError, RequestException
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog, QgsProject, QgsField, QgsFeature, QgsVectorLayer, QgsVectorFileWriter
)
from PyQt5.QtCore import QVariant
import processing
from osgeo import gdal
from fiona.crs import from_epsg
from shapely.geometry import mapping, Point
import fiona
from .source_variables import *
from .projinit_algorithm import *

global project_file, home_test, test_file, test_mode, laptop_mode, selected_files_status, selected_site_data_status, \
    selected_raster_status, file_path_loc, destination_gis, multiple_apn, apn_list, prj_folder, proj_apn, proj_name, \
    proj_num, proj_test, proj_type, dxf_choice, map_choice, folder_choice, buffer_radius, buffer_parcels, buffer_dem, \
    source_shp, destination_shp, qgis_path, r_layer1, destination_ras, dwg_folder, output_dst, proposal_check, \
    raster_file, input_epsg, dem1m, layer, buffer_layer, dst_file, layer_name, parcel_center, goog_geo_dst, \
    destination_dxf, destination_map, project, naip_temp, crs, year_dbl, mem_layer, goog_task, dem_radius_buffer, \
    merged_geometry, road_points_all_exclude, road_finder_path


class DataUpdate(QgsTask):
    def __init__(self):
        super().__init__("DataUpdate", QgsTask.CanCancel)
        cancel_sig = pyqtSignal()
        down_sig = pyqtSignal()
        finish_sig = pyqtSignal()
        error_sig = pyqtSignal()
        up_to_date_sig = pyqtSignal()
        self.canceled = False
        self.dialog = None
        self.new_files = False
        self.exception = None
        self.window = QDialog()
        self.reproject = False
        self.old_extentions = ['.shp', '.shx', '.dbf', '.prj', '.cpg', '.sbn', '.sbx', '.shp.xml', '.xml']
        self.rep_extentions = ['.shp', '.shx', '.dbf', '.prj', '.cpg']

    def cancel_this(self, position_x, position_y):
        self.canceled = True
        confirm_msg = QMessageBox()
        confirm_msg.setIcon(QMessageBox.Information)
        confirm_msg.setText("Data update process had and error or was canceled.")
        confirm_msg.setWindowTitle("Data Update Canceled")
        confirm_msg.setStandardButtons(QMessageBox.Ok)
        confirm_msg.move(position_x, position_y)
        confirm_msg.exec_()
        self.initial_msg.accept()
        self.cancel()
        QApplication.processEvents()
        super().reject()
        return False

    def dont_download_file(self, url, save_path):
        with requests.get(url, stream=True) as r:
            content_disposition = r.headers.get('Content-Disposition')
            if not content_disposition:
                return False
            filenames = re.findall("filename=(.+)", content_disposition)
            if not filenames:
                return False
            filename = unquote(filenames[0])
            with open(f"{save_path}{filename}", 'wb') as f_out:
                for chunk in r.iter_content(chunk_size=8192):
                    f_out.write(chunk)
            return filename  # Return the actual filename used

    def download_file(self, url, save_path, max_retries=3):
        session = requests.Session()
        retries = 0
        while retries < max_retries:
            try:
                with session.get(url, stream=True) as r:
                    content_disposition = r.headers.get('Content-Disposition')
                    if not content_disposition:
                        return False
                    filenames = re.findall("filename=(.+)", content_disposition)
                    if not filenames:
                        return False
                    filename = unquote(filenames[0])
                    with open(os.path.join(save_path, filename), 'wb') as f_out:
                        for chunk in r.iter_content(chunk_size=8192):
                            f_out.write(chunk)
                    return filename  # Return the actual filename used
            except ChunkedEncodingError as e:
                retries += 1
                print(f"ChunkedEncodingError encountered. Retrying {retries}/{max_retries}...")
            except RequestException as e:
                print(f"Request failed: {e}")
                return False
        return False  # Return False if all retries fail

    def where_qgis(self):
        qgis_main_window = None
        for widget in QApplication.topLevelWidgets():
            if widget.objectName() == 'QgisApp':
                qgis_main_window = widget
                break

        if qgis_main_window is not None:
            screen = QDesktopWidget().screenNumber(qgis_main_window)
            screen_geometry = QDesktopWidget().screenGeometry(screen)

            x_center = screen_geometry.center().x()  - screen_geometry.width() // 10
            y_center = screen_geometry.center().y()  - screen_geometry.height() // 10

            # Move the message box to that screen
            return x_center, y_center
    def remove_old_files(self, feature_dir, feature_name, extensions):
        for ext in extensions:
            file_path = f'{feature_dir}{feature_name}{ext}'
            if os.path.exists(file_path):
                attempts = 0
                while attempts < 5:  # 5 attempts to delete the file
                    try:
                        os.remove(file_path)
                        break
                    except PermissionError:
                        time.sleep(1)
                        attempts += 1

    def initial_message(self, pos_x, pos_y):
        self.initial_msg = QMessageBox()
        self.initial_msg.setIcon(QMessageBox.Information)
        self.initial_msg.setText("Updating GIS source data...please be patient...")
        self.initial_msg.setWindowTitle("Data Update")
        self.initial_msg.setStandardButtons(QMessageBox.Cancel)  # No button
        self.initial_msg.move(pos_x, pos_y)
        self.initial_msg.show()

        QApplication.processEvents()

    def save_new_filename(self, data_source, new_filename):
        try:
            with open(config_file_path, 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            config = {}

        config[data_source] = new_filename

        with open(config_file_path, 'w') as f:
            json.dump(config, f)

    def load_filenames(self):
        with open(f'{config_file_path}', 'r') as f:
            return json.load(f)

    def check_crs(self, feature_dir, feature_name):
        if os.path.exists(f'{feature_dir}{feature_name}.shp'):
            layer_update = QgsVectorLayer(f'{feature_dir}{feature_name}.shp', f'{feature_name}', 'ogr')
            if not layer_update.isValid():
                del layer_update
                return False

            if layer_update.crs().authid() != 'EPSG:2225':
                target_crs = QgsCoordinateReferenceSystem('EPSG:2225')
                temp_reprojected_layer_path = f'{feature_dir}{feature_name}_reprojected.shp'

                # Perform Reprojection
                error, _ = QgsVectorFileWriter.writeAsVectorFormat(
                    layer_update,
                    temp_reprojected_layer_path,
                    "UTF-8",
                    driverName="ESRI Shapefile",
                    destCRS=target_crs
                )

                del layer_update  # Explicitly delete the layer

                if error != QgsVectorFileWriter.NoError:
                    return False

                # Replace the original with the reprojected
                for ext in self.rep_extentions:
                    original_path = f'{feature_dir}{feature_name}{ext}'
                    temp_path = f'{feature_dir}{feature_name}_reprojected{ext}'
                    shutil.move(temp_path, original_path)

                return True
            else:
                del layer_update  # Explicitly delete the layer
                return False
        else:
            return False

    def fix_shapefile_geometries(self, shapefile_path):
        """
        Loads a shapefile, checks for invalid geometries, and attempts to fix them.

        :param shapefile_path: The file system path to the shapefile.
        """
        # Load the shapefile as a QgsVectorLayer
        layer = QgsVectorLayer(shapefile_path, "Layer", "ogr")

        # Check if the layer is valid
        if not layer.isValid():
            return

        QgsProject.instance().addMapLayer(layer)

        # Fetch features with invalid geometries
        invalid_features = layer.getFeatures(QgsFeatureRequest().setInvalidGeometryCheck(True))
        invalid_feature_ids = [feature.id() for feature in invalid_features]

        if not invalid_feature_ids:
            return

        # Start an edit session to modify the features
        layer.startEditing()

        for feature_id in invalid_feature_ids:
            feature = layer.getFeature(feature_id)
            geometry = feature.geometry()
            # Attempt to fix the invalid geometry
            fixed_geometry = geometry.makeValid()
            if fixed_geometry:
                layer.changeGeometry(feature_id, fixed_geometry)
            else:
                print(f"Could not fix geometry for feature ID {feature_id}")

        # Commit changes to the layer
        if layer.commitChanges():
            print(f"Fixed invalid geometries in the layer: {layer.name()}")
        else:
            print(f"Failed to fix some geometries in the layer: {layer.name()}")
            layer.rollBack()

    def fix_directory_shapefiles(self, directory_path):
        """
        Applies the fix_shapefile_geometries function to all shapefiles in the given directory.

        :param directory_path: The file system path to the directory containing shapefiles.
        """
        # Ensure the directory exists
        if not os.path.isdir(directory_path):
            return

        # List all shapefiles in the directory
        shapefiles = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.lower().endswith('.shp')]

        if not shapefiles:
            return

        # Fix geometries for each shapefile
        for shapefile in shapefiles:
            self.fix_shapefile_geometries(shapefile)

    def make_apn_list(self, feature_dir, feature_name):
        if os.path.exists(f'{feature_dir}HumCo_Parcels.shp'):
            layer_update = QgsVectorLayer(f'{feature_dir}HumCo_Parcels.shp', f'{feature_name}', 'ogr')
            if not layer_update.isValid():
                del layer_update
                return False
            column_name = 'APN_12'
            output_list_path = apn_path
            apn_list = [str(feature[column_name]) for feature in
                        layer_update.getFeatures(QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry))]
            with open(output_list_path, 'w') as f:
                f.writelines(f"{apn}\n" for apn in apn_list)

        del layer_update

    def update_dialog(self):
        self.window.setWindowTitle("Updating GIS source data...")
        layout = QVBoxLayout()

        message_label = QLabel("Working to update local source files for GIS data collection.")
        message_label.setStyleSheet("QLabel { color : black; font-weight : bold; }")
        layout.addWidget(message_label)

        button_layout = QHBoxLayout()
        spacer = QSpacerItem(0, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        button_layout.addItem(spacer)
        update_cancel_button = QPushButton("Cancel")
        update_cancel_button.setFixedSize(80, 40)
        update_cancel_button.clicked.connect(self.cancel)  # Connect to instance method
        button_layout.addWidget(update_cancel_button)

        layout.addLayout(button_layout)
        self.window.setLayout(layout)
        self.window.resize(400, 100)
        self.window.show()

    def run(self):
        position_x, position_y = self.where_qgis()
        # self.message0.emit()
        self.initial_message(position_x, position_y)
        # self.update_dialog()

        data_sources = [
            {
                'url': 'https://humboldtgov.org/DocumentCenter/View/562',  # Parcels
                'feature_dir': f'{source_shp}Parcels/',
                'feature_name': 'HumCo_Parcels',
            },
            {
                'url': 'https://humboldtgov.org/DocumentCenter/View/566',  # Roads
                'feature_dir': f'{source_shp}Roads/',
                'feature_name': 'HumCo_Road_CL',
            },
            {
                'url': 'https://humboldtgov.org/DocumentCenter/View/681',  # General plan
                'feature_dir': f'{source_shp}General Plan Land Use/',
                'feature_name': 'Land Use',
            },
            {
                'url': 'https://humboldtgov.org/DocumentCenter/View/685',  # Zoning
                'feature_dir': f'{source_shp}Humboldt County Zoning/',
                'feature_name': 'HumCo_Zoning',
            },
            {
                'url': 'https://humboldtgov.org/DocumentCenter/View/564',  # City Boundaries
                'feature_dir': f'{source_shp}City Limits/',
                'feature_name': 'City Limits',
            },
            {
                'url': 'https://humboldtgov.org/DocumentCenter/View/585',  # Community Service Districts
                'feature_dir': f'{source_shp}Community Service Districts/',
                'feature_name': 'HumCo_Service_Districts',
            },
            {
                'url': 'https://humboldtgov.org/DocumentCenter/View/589',  # Fire Districts
                'feature_dir': f'{source_shp}Fire District/',
                'feature_name': 'HumCo_Fire_Districts',
            },
            {
                'url': 'https://humboldtgov.org/DocumentCenter/View/579',  # Coastal Zone
                'feature_dir': f'{source_shp}Coastal Zone/',
                'feature_name': 'HumCo_Coastal_Zone',
            },
            {
                'url': 'https://humboldtgov.org/DocumentCenter/View/593',  # Public Lands
                'feature_dir': f'{source_shp}Public Lands/',
                'feature_name': 'HumCo_Public_Lands',
            },
            {
                'url': 'https://humboldtgov.org/DocumentCenter/View/583',  # Community Planning Areas
                'feature_dir': f'{source_shp}Community Planning Areas/',
                'feature_name': 'HumCo_Planning',
            },
            {
                'url': 'https://humboldtgov.org/DocumentCenter/View/597',  # Biological Resource Areas
                'feature_dir': f'{source_shp}Biological Resource Areas/',
                'feature_name': 'Bio_Res',
            },
            {
                'url': 'https://humboldtgov.org/DocumentCenter/View/610',  # Fire Hydrants
                'feature_dir': f'{source_shp}Fire Hydrants/',
                'feature_name': 'FireHydrants',
            },
            {
                'url': 'https://humboldtgov.org/DocumentCenter/View/612',  # Fire Stations
                'feature_dir': f'{source_shp}Fire Stations/',
                'feature_name': 'FireStations',
            },
            {
                'url': 'https://humboldtgov.org/DocumentCenter/View/628',  # Alquist-Priolo Zones
                'feature_dir': f'{source_shp}Alquist-Priolo Zones/',
                'feature_name': 'AlquistPriolo',
            },
            {
                'url': 'https://humboldtgov.org/DocumentCenter/View/622',  # Earthquake Fault Lines
                'feature_dir': f'{source_shp}Earthquake Fault Lines/',
                'feature_name': 'HumCo_FaultLines',
            },
            {
                'url': 'https://humboldtgov.org/DocumentCenter/View/624',  # Liquefaction Zones
                'feature_dir': f'{source_shp}Liquefaction Zones/',
                'feature_name': 'Liquefaction',
            },
            {
                'url': 'https://humboldtgov.org/DocumentCenter/View/633',  # Slope Stability Humboldt Bay
                'feature_dir': f'{source_shp}Slope Stability (HUMBOLDT BAY)/',
                'feature_name': 'SlopeStab_BAY',
            },
            {
                'url': 'https://humboldtgov.org/DocumentCenter/View/637',  # Tsunami Zone
                'feature_dir': f'{source_shp}Tsunami Inundation Zone/',
                'feature_name': 'tsunami',
            },
            {
                'url': 'https://humboldtgov.org/DocumentCenter/View/635',  # Slope Stability Humboldt County
                'feature_dir': f'{source_shp}Slope Stability (COUNTY)/',
                'feature_name': 'SlopeStability_HUM',
            },
            {
                'url': 'https://humboldtgov.org/DocumentCenter/View/639',  # Wildland Fire Rating
                'feature_dir': f'{source_shp}Wildland Fire Risk/',
                'feature_name': 'Fire_Risk',
            },
            {
                'url': 'https://humboldtgov.org/DocumentCenter/View/643',  # Mill Creek Wetlands
                'feature_dir': f'{source_shp}Mill Creek Wetlands/',
                'feature_name': 'MillCreekWetlands',
            },
            {
                'url': 'https://humboldtgov.org/DocumentCenter/View/683',  # Williamson Act
                'feature_dir': f'{source_shp}Williamson Act Lands/',
                'feature_name': 'HumCo_Williamson_Act',
            },
            {
                'url': 'https://humboldtgov.org/DocumentCenter/View/677',  # Airport Compatibility Zone
                'feature_dir': f'{source_shp}Airport Compatibility Zone/',
                'feature_name': 'Airport_Comp',
            },
            {
                'url': 'https://humboldtgov.org/DocumentCenter/View/781',  # Ag Lands
                'feature_dir': f'{source_shp}Agricultural Lands/',
                'feature_name': 'AgLands',
            },
            {
                'url': 'https://humboldtgov.org/DocumentCenter/View/792',  # Slope Less Than 30%
                'feature_dir': f'{source_shp}Slopes Greater than 30%/',
                'feature_name': 'slope30',
            },
            {
                'url': 'https://humboldtgov.org/DocumentCenter/View/85576/Percent-Slope-Less-Than-15-Polygons-Shapefile-ZIP',  # Slope Less Than 15%
                'feature_dir': f'{source_shp}Slopes Less than 15%/',
                'feature_name': 'slope15',
            },
        ]

        # Load saved filenames at the start of the program
        saved_filenames = self.load_filenames()

        for data in data_sources:
            downloaded_filename = self.download_file(data['url'], source_zip)

            if self.isCanceled():
                self.canceled = True
                self.cancel_this(position_x, position_y)
                return False

            # Use the saved_filenames dictionary to check if it's a new file.
            if saved_filenames.get(data['feature_name'], "") != downloaded_filename:
                self.remove_old_files(data['feature_dir'], data['feature_name'], self.old_extentions)

                new_zip_path = os.path.join(source_zip, downloaded_filename)
                feature_dir = data['feature_dir']
                feature_name = data['feature_name']

                # Extract new files and handle them
                with zipfile.ZipFile(new_zip_path, 'r') as zip_ref:
                    zip_ref.extractall(feature_dir)

                    # Remove temporary and old files, then rename new files
                    for file_info in zip_ref.infolist():
                        old_file_path = os.path.join(feature_dir, file_info.filename)
                        new_file_path = os.path.join(feature_dir,
                                                     feature_name + os.path.splitext(file_info.filename)[1])
                        if os.path.exists(new_file_path):
                            os.remove(new_file_path)
                        os.rename(old_file_path, new_file_path)

                # Reproject if necessary
                self.reproject = self.check_crs(feature_dir, feature_name)

                # Update APN list if this is the parcels file
                if feature_name == 'HumCo_Parcels' or not os.path.exists(apn_path):
                    self.make_apn_list(feature_dir, feature_name)

                # Update the filename in the JSON file
                self.save_new_filename(data['feature_name'], downloaded_filename)

        if self.isCanceled():
            self.initial_msg.accept()
            self.cancel_this(position_x, position_y)
            return False
        if not self.canceled:
            self.fix_directory_shapefiles(source_shp)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Source file update complete!")
            msg.setWindowTitle("Data Update")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.move(position_x, position_y)
            msg.exec_()
            self.initial_msg.accept()
            QApplication.processEvents()
            return True


class RasterExtraction(QgsTask):
    def __init__(self, do_goog, do_naip, do_dem, goog_layer=None, dem_radius_buffer=None, goog_geo_dst=None,
                 goog_geo2225=None, naip_temp=None, naip_dst=None, dem_layer=None, dem_dst=None, flow_src=None,
                 parent=None):
        super().__init__(parent)

        self.dem_radius_buffer = dem_radius_buffer
        self.canceled = False
        self.exception = None
        self.mask_layer = None
        self.naip_layer = QgsRasterLayer(naip_src, 'NAIP 2022_TEMP')
        self.goog_geo_dst = goog_geo_dst
        self.goog_geo2225 = goog_geo2225
        self.naip_temp = naip_temp
        self.naip_dst = naip_dst
        self.project = QgsProject.instance()
        self.goog_layer = goog_layer
        self.dem_layer = dem_layer
        self.dem_dst = dem_dst
        self.flow_src = flow_src
        self.goog_done = False
        self.naip_done = False
        self.do_goog = do_goog
        self.do_naip = do_naip
        self.do_dem = do_dem


    def run(self):
        if selected_raster_status["Google Earth Aerial"] and self.goog_layer is not None and self.do_goog:
            # Get extents and export clipped GeoTIFF
            extent_layer = self.dem_radius_buffer.boundingBox()
            provider = self.goog_layer.dataProvider()
            x_pixels = int(extent_layer.width() * 3.2808)  # Converting to feet
            y_pixels = int(extent_layer.height() * 3.2808)

            # Set input and output CRS
            crs_src = QgsCoordinateReferenceSystem(self.goog_layer.crs())  # EPSG of Google Earth Satellite (3857)
            crs_dst = QgsCoordinateReferenceSystem("EPSG:2225")  # EPSG of target crs

            # Code for QGIS 3.xx - QgsCoordinateTransform is different in v 2.xx #
            xform_dst_to_src = QgsCoordinateTransform(crs_dst, crs_src, self.project)
            projected_extent = xform_dst_to_src.transformBoundingBox(extent_layer)

            pipe = QgsRasterPipe()
            pipe.set(provider.clone())

            file_writer_raster = QgsRasterFileWriter(self.goog_geo_dst)
            file_writer_raster.Mode(0)
            file_writer_raster.setMaxTileWidth(2000)
            file_writer_raster.setMaxTileHeight(2000)

            # file_writer_raster.writeRaster(pipe, x_pixels, y_pixels, projected_extent, crs_src, self.project.transformContext())
            del file_writer_raster

            MESSAGE_CATEGORY = "Google Earth Aerial"

            # Define the target CRS
            dst_crs = crs

            params = {
                'INPUT': self.goog_geo_dst,
                'TARGET_CRS': dst_crs,
                'OUTPUT': self.goog_geo2225
            }

            # Run the algorithm synchronously
            feedback_goog = QgsProcessingFeedback()
            processing.run("gdal:warpreproject", params, feedback=feedback_goog)

        # Get extents and export clipped GeoTIFF
        extent_layer = self.dem_radius_buffer.boundingBox()
        provider = self.naip_layer.dataProvider()
        x_pixels = int(extent_layer.width() * 3.2808)  # Converting to feet
        y_pixels = int(extent_layer.height() * 3.2808)

        # Set input and output CRS
        crs_src = QgsCoordinateReferenceSystem(self.naip_layer.crs())  # EPSG of Google Earth Satellite (3857)
        crs_dst = QgsCoordinateReferenceSystem("EPSG:2225")  # EPSG of target crs

        # Code for QGIS 3.xx - QgsCoordinateTransform is different in v 2.xx #
        xform_dst_to_src = QgsCoordinateTransform(crs_dst, crs_src, self.project)
        projected_extent = xform_dst_to_src.transformBoundingBox(extent_layer)

        # Create a rectangle from the extent
        rect = QgsRectangle(projected_extent.xMinimum(), projected_extent.yMinimum(),
                            projected_extent.xMaximum(), projected_extent.yMaximum())

        # Create a new temporary vector layer for the extent polygon
        self.mask_layer = QgsVectorLayer("Polygon", "mask_layer", "memory")
        self.mask_layer.setCrs(crs_src)

        # Create a new feature in the layer
        feature = QgsFeature()

        # Set the geometry of the feature to a polygon that matches the extent
        geom = QgsGeometry().fromRect(rect)
        feature.setGeometry(geom)

        # Add the feature to the layer
        self.mask_layer.dataProvider().addFeatures([feature])
        crs_dst = QgsCoordinateReferenceSystem("EPSG:2225")
        feedback_mask = QgsProcessingFeedback()

        if selected_raster_status["2022 NAIP Aerial"] and self.do_naip:
            reprojected_mask = processing.run(
                "native:reprojectlayer",
                {
                    'INPUT': self.mask_layer,
                    'TARGET_CRS': crs_dst,
                    'OUTPUT': 'memory:'
                },
                feedback=feedback_mask
            )['OUTPUT']

            # Set input and output CRS
            crs_src = QgsCoordinateReferenceSystem(self.naip_layer.crs())

            # xform_src_to_dst = QgsCoordinateTransform(crs_src, crs_dst, QgsProject.instance())
            feedback_naip_clip = QgsProcessingFeedback()
            feedback_naip_reproject = QgsProcessingFeedback()

            # Clip the raster
            params_clip = {
                'INPUT': self.naip_layer,
                'MASK': reprojected_mask,
                'NODATA': -9999,
                'ALPHA_BAND': False,
                'CROP_TO_CUTLINE': True,
                'KEEP_RESOLUTION': True,
                'OPTIONS': None,
                'DATA_TYPE': 0,
                'OUTPUT': self.naip_temp
            }
            processing.run("gdal:cliprasterbymasklayer", params_clip, feedback=feedback_naip_clip)

            # Reproject clipped raster to 'EPSG:2225'
            params_warp = {
                'INPUT': self.naip_temp,
                'TARGET_CRS': crs_dst,
                'OUTPUT': self.naip_dst
            }
            processing.run("gdal:warpreproject", params_warp, feedback=feedback_naip_reproject)

        if dem1m and self.do_dem:
            reprojected_mask = processing.run(
                "native:reprojectlayer",
                {
                    'INPUT': self.mask_layer,
                    'TARGET_CRS': crs_dst,
                    'OUTPUT': 'memory:'
                },
                feedback=feedback_mask
            )['OUTPUT']

            crs_src = QgsCoordinateReferenceSystem(self.dem_layer.crs())  # EPSG of Google Earth Satellite (3857)
            xform_dst_to_src = QgsCoordinateTransform(crs_dst, crs_src, self.project)
            feedback_dem = QgsProcessingFeedback()
            feedback_dem_clip = QgsProcessingFeedback()
            feedback_flow_clip = QgsProcessingFeedback()
            feedback_dem_reproject = QgsProcessingFeedback()

            # Clip the raster
            params_clip = {
                'INPUT': self.dem_layer,
                'MASK': reprojected_mask,
                'NODATA': -9999,
                'ALPHA_BAND': False,
                'CROP_TO_CUTLINE': True,
                'KEEP_RESOLUTION': True,
                'OPTIONS': None,
                'DATA_TYPE': 0,
                'OUTPUT': self.dem_dst
            }
            processing.run("gdal:cliprasterbymasklayer", params_clip, feedback=feedback_dem_clip)


            params_clip = {
                'INPUT': self.flow_src,
                'MASK': reprojected_mask,
                'NODATA': -9999,
                'ALPHA_BAND': False,
                'CROP_TO_CUTLINE': True,
                'KEEP_RESOLUTION': True,
                'OPTIONS': None,
                'DATA_TYPE': 0,
                'OUTPUT': flow_accumulation_dst
            }
            processing.run("gdal:cliprasterbymasklayer", params_clip, feedback=feedback_flow_clip)

        return True

    def finished(self, result):
        if result:
            # Task completed successfully
            QgsMessageLog.logMessage(f"'{self.description()}' task completed successfully", level=Qgis.Info)

            naip_layer_id = self.naip_layer.id()
            mask_layer_id = self.mask_layer.id()

            if self.project.mapLayer(naip_layer_id):
                time.sleep(0.5)
                self.project.removeMapLayer(naip_layer_id)
            if self.project.mapLayer(mask_layer_id):
                time.sleep(0.5)
                self.project.removeMapLayer(mask_layer_id)
            raster_task_finished = True

            try:
                os.remove(self.goog_geo_dst)
                os.remove(self.naip_temp)
            except OSError as e:
                QgsMessageLog.logMessage("Error: %s : %s" % (self.goog_geo_dst, e.strerror))
        else:
            if self.exception is not None:
                # An exception occurred during the task
                QgsMessageLog.logMessage(f"'{self.description()}' task encountered an exception: {self.exception}", level=Qgis.Critical)
            elif self.isCanceled():
                # The task was canceled
                QgsMessageLog.logMessage(f"'{self.description()}' task was canceled by the user", level=Qgis.Warning)


class SlopeExtractor(QgsTask):
    def __init__(self, dem1m, raster_file, slope_per, slope_deg, percent_style, group2, dem1m_layer_name, destination_dem, hillshade_dst):
        super().__init__('DEM Processing Task', QgsTask.CanCancel)
        self.dem1m = dem1m
        self.raster_file = raster_file
        self.slope_per = slope_per
        self.slope_deg = slope_deg
        self.hillshade_dst = hillshade_dst
        self.percent_style = percent_style
        self.group2 = group2
        self.dem1m_layer_name = dem1m_layer_name

    def run(self):
        project = QgsProject.instance()

        if self.dem1m:
            # Run the Slope plugin to get a slope and hillshade raster for the project
            gdal.DEMProcessing(self.slope_per, self.raster_file, 'slope', computeEdges=True, slopeFormat='percent')
            gdal.DEMProcessing(self.slope_deg, self.raster_file, 'slope', computeEdges=True, slopeFormat='degree')
            gdal.DEMProcessing(self.hillshade_dst, self.raster_file, 'hillshade', computeEdges=True)

        return True  # Return True if the task completed successfully

    def finished(self, result):
        QgsMessageLog.logMessage(f"'{self.description()}' task completed successfully", level=Qgis.Info)
        pass
        """
        if self.dem1m:
            r_layer1 = QgsRasterLayer(self.raster_file, self.dem1m_layer_name)
            if r_layer1.isValid():
                r_layer1.triggerRepaint()
                project.addMapLayer(r_layer1, False)
                self.group2.insertChildNode(3, QgsLayerTreeLayer(r_layer1))
                project.layerTreeRoot().findLayer(r_layer1.id()).setExpanded(False)

                rlayer4 = QgsRasterLayer(self.slope_deg, "SLOPE (DEGREE)")
                if rlayer4.isValid():
                    rlayer4.triggerRepaint()
                    project.addMapLayer(rlayer4, False)
                    self.group2.insertChildNode(4, QgsLayerTreeLayer(rlayer4))
                    project.layerTreeRoot().findLayer(rlayer4.id()).setExpanded(False)

                rlayer5 = QgsRasterLayer(self.slope_per, "SLOPE (PERCENT)")
                if rlayer5.isValid():
                    rlayer5.triggerRepaint()
                    project.addMapLayer(rlayer5, False)
                    self.group2.insertChildNode(5, QgsLayerTreeLayer(rlayer5))
                    project.layerTreeRoot().findLayer(rlayer5.id()).setExpanded(False)
                    rlayer5.loadNamedStyle(self.percent_style)

                rlayer6 = QgsRasterLayer(self.hillshade_dst, "HILLSHADE")
                if rlayer6.isValid():
                    rlayer6.triggerRepaint()
                    project.addMapLayer(rlayer6, False)
                    self.group2.insertChildNode(5, QgsLayerTreeLayer(rlayer6))
                    project.layerTreeRoot().findLayer(rlayer6.id()).setExpanded(False)

        else:
            r_layer1 = QgsRasterLayer(self.destination_dem, "10M HUM_CO USGS DEM (1/3 ARC-SECOND)")
            if r_layer1.isValid():
                r_layer1.triggerRepaint()
                project.addMapLayer(r_layer1, False)
                self.group2.insertChildNode(3, QgsLayerTreeLayer(r_layer1))
                project.layerTreeRoot().findLayer(r_layer1.id()).setExpanded(False)
        """

class MapCreator(QgsTask):
    def __init__(self, description, project, map_dst, goog_layer, project_parcel):
        super().__init__(description, QgsTask.CanCancel)
        self.project = project
        self.map_dst = map_dst
        self.exception = None
        self.goog_layer = goog_layer
        self.project_parcel = project_parcel
        self.layer_list = QgsProject.instance().mapLayersByName(layer_name)

    def run(self):
        manager = self.project.layoutManager()
        layouts_list = manager.printLayouts()

        # Remove any duplicate layouts
        for layout in layouts_list:
            if layout.name() == self.layout_name:
                manager.removeLayout(layout)

        layout = QgsPrintLayout(self.project)
        layout.initializeDefaults()
        layout.setName(self.layout_name)
        manager.addLayout(layout)

        # Define the layers for the legend
        self.legend_layers = ["PROJECT PARCEL", "ADJACENT PARCELS", "SURROUNDING PARCELS", "ROAD CENTERLINE",
                         "STREAMS", "CONTOURS-20FT", "CONTOURS-100FT"]

        # Get other layers by their names
        self.other_layers = []
        for layer_name in self.legend_layers:
            if self.layer_list:
                self.other_layers.append(self.layer_list[0])
            else:
                QgsMessageLog.logMessage(f"No layer found with the name: {layer_name}")

        # Get the page collection
        pages = layout.pageCollection()

        # Set the page size
        # page_size = QgsLayoutSize(7.5, 9, QgsUnitTypes.LayoutInches)
        page_size = QgsLayoutSize(190.5, 228.6, QgsUnitTypes.LayoutMillimeters)
        pages.pages()[0].setPageSize(page_size)

        # Create a map item and add it to the layout
        map = QgsLayoutItemMap(layout)
        map.setLayers(self.other_layers + [self.goog_layer])
        map.setRect(0, 0, page_size.width(), page_size.height())

        # Get the bounding box of the feature
        bbox = self.project_parcel.extent()

        # Width and height of the bounding box in feet
        bbox_width_ft = bbox.width()  # EPSG:2225
        bbox_height_ft = bbox.height()  # EPSG:2225

        # Calculate the max length
        bbox_max_size_ft = max(bbox_width_ft, bbox_height_ft)

        # Scales list (1 inch = X feet)
        scales = [10, 20, 30, 40, 50, 60, 100, 200, 300, 400, 500, 600, 800,
                  1000, 1200, 1500, 2000, 2500, 3000]

        map_width_inches = 7.5  # width of the map canvas in inches
        map_height_inches = 9  # height of the map canvas in inches

        element = 0

        # Iterate over the scales in order to find the largest one that fits on the map
        for scale in scales:
            map_max_width_ft = map_width_inches * scales[element]
            map_max_height_ft = (map_height_inches - 1.5) * scales[element]

            if map_max_width_ft > bbox_width_ft and map_max_height_ft > bbox_height_ft:
                # Calculate the centroid of the project parcel layer for map extent placement
                features = self.project_parcel.getFeatures()
                geometry_union = QgsGeometry().unaryUnion([feature.geometry() for feature in features])
                bbox = geometry_union.boundingBox()
                center_point = bbox.center()

                # Grab the scale number
                fin_scale = scales[element + 1]

                map_render_height = map_height_inches * fin_scale
                map_render_width = map_width_inches * fin_scale

                # Get the coordinates for map size
                west_x = center_point.x() - map_render_width / 2
                south_y = center_point.y() - map_render_height / 2
                east_x = center_point.x() + map_render_width / 2
                north_y = center_point.y() + map_render_height / 2

                # Calculate the new extent based on the center point and the size of the map
                new_extent = QgsRectangle(west_x, south_y, east_x, north_y)
                layout.addLayoutItem(map)

                # Set map extent and scale
                map.setExtent(new_extent)

                conversion_factor = map.mapUnitsToLayoutUnits()
                segment_length = fin_scale / conversion_factor

                # Create and configure the scale bar
                scalebar = QgsLayoutItemScaleBar(layout)
                scalebar.setLinkedMap(map)
                scalebar.setStyle('Single Box')
                scalebar.setUnits(QgsUnitTypes.DistanceFeet)
                scalebar.setNumberOfSegments(2)
                scalebar.setNumberOfSegmentsLeft(0)
                scalebar.setUnitsPerSegment(fin_scale)
                scalebar.setUnitLabel('FT')
                scalebar.update()

                # Add the scale bar to the layout
                layout.addLayoutItem(scalebar)
                scalebar.attemptMove(QgsLayoutPoint(10, 200, QgsUnitTypes.LayoutMillimeters))
                scalebar.attemptResize(
                    QgsLayoutSize(50, 5, QgsUnitTypes.LayoutMillimeters))
                scalebar.refresh()

                break
            else:
                # Continue to next element in scales
                element = element + 1
                continue

        # Create legend
        legend = QgsLayoutItemLegend(layout)
        legend.setTitle("LEGEND")
        layout.addLayoutItem(legend)
        legend.setAutoUpdateModel(False)
        legend.model().rootGroup().clear()

        # Add the layers and add to map
        for layer in self.other_layers: legend.model().rootGroup().addLayer(layer)
        legend.setLinkedMap(map)
        legend.setItemOpacity(0.70)
        legend.refresh()

        layout = manager.layoutByName(self.layout_name)
        self.exporter = QgsLayoutExporter(layout)

        self.settings = QgsLayoutExporter.ImageExportSettings()
        self.settings.dpi = 150

        # self.exporter.exportToImage(self.map_dst, self.settings)

    def finished(self, result):
        if result:
            QgsMessageLog.logMessage("Layout creation task completed successfully", 'LayoutTask')
            self.exporter.exportToImage(self.map_dst, self.settings)

        else:
            if self.exception is not None:
                QgsMessageLog.logMessage(f"Layout creation task failed: {self.exception}", 'LayoutTask')
            else:
                QgsMessageLog.logMessage("Layout creation task was cancelled", 'LayoutTask')

    def cancel(self):
        QgsMessageLog.logMessage("Layout creation task was cancelled", 'LayoutTask')
        super().cancel()


class RoadFinderOld(QgsTask):
    def __init__(self, slope_path, road_finder_dir, streams_shp, proc_point_all, proj_num):
        super().__init__("Road Point Extraction Task", QgsTask.CanCancel)
        self.raster_path = slope_path
        self.road_finder_dir = road_finder_dir
        self.streams_shp = streams_shp
        self.feedback = QgsProcessingFeedback()
        self.road_points_all_exclude = proc_point_all

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), 'RoadFinder')

        raster_ds = gdal.Open(self.raster_path, gdal.GA_ReadOnly)
        transform = raster_ds.GetGeoTransform()
        x_origin = transform[0]
        y_origin = transform[3]
        pixel_width = transform[1]
        pixel_height = -transform[5]
        band = raster_ds.GetRasterBand(1)
        raster_array = band.ReadAsArray()

        schema = {
            'geometry': 'Point',
            'properties': {'Value': 'float'},
        }
        crs = from_epsg(26910)

        # Define the range of values and output shapefile names
        ranges = [(0, 24), (24, 32), (32, 40), (40, 45), (0, 45)]
        filenames = ["OUTPUT_POINTS_0-24", "OUTPUT_POINTS_24-32",
                     "OUTPUT_POINTS_32-40", "OUTPUT_POINTS_40-45", "OUTPUT_POINTS_45"]

        for value_range, filename in zip(ranges, filenames):
            output_shp_path = f"{self.road_finder_dir}{filename}.shp"
            self.write_points_to_shapefile(raster_array, value_range, output_shp_path, crs, schema, x_origin, y_origin, pixel_width, pixel_height)

        # Create buffer around streams
        params = {
            'INPUT': self.streams_shp,
            'DISTANCE': 8,
            'OUTPUT': 'memory:'
        }
        buffer_result = processing.run("native:buffer", params, feedback=self.feedback)
        buffer_layer = buffer_result['OUTPUT']

        # Process each shapefile to exclude points within the buffer
        for value_range, filename in zip(ranges, filenames):
            input_shp_path = f"{self.road_finder_dir}{filename}.shp"
            output_shp_path = f"{self.road_finder_dir}{filename}_BUFFER_EXCLUSION.shp"

            params = {
                'INPUT': input_shp_path,
                'PREDICATE': [2],  # 2 corresponds to does not intersect
                'INTERSECT': buffer_layer,
                'OUTPUT': output_shp_path
            }
            processing.run("qgis:extractbylocation", params, feedback=self.feedback)

        # Use QgsVectorLayer to load the shapefile
        input_shp_path = f"{self.road_finder_dir}OUTPUT_POINTS_45.shp"
        road_point_layer = QgsVectorLayer(input_shp_path, 'Road Points', 'ogr')

        # Ensure the layer is valid before proceeding
        if not road_point_layer.isValid():
            QgsMessageLog.logMessage(f"Layer failed to load: {input_shp_path}", 'RoadFinder')
            return False

        # Filter points based on the criteria
        filtered_points = f'{self.road_finder_dir}OUTPUT_POINTS_45_BUFFER_FILTERED.shp'
        self.save_filtered_points(road_point_layer, filtered_points)

        return True
    def write_points_to_shapefile(self, raster_array, value_range, output_path, crs, schema, x_origin, y_origin, pixel_width, pixel_height):
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

    def export_excluded_points_to_shapefile(self, excluded_ids, feature_dict, output_path, crs):
        fields = QgsFields()
        for field in list(feature_dict.values())[0].fields():
            fields.append(field)

        writer = QgsVectorFileWriter(
            output_path,
            "UTF-8",
            fields,
            QgsWkbTypes.Point,
            crs,
            "ESRI Shapefile"
        )

        if writer.hasError() != QgsVectorFileWriter.NoError:
            raise Exception("Error when creating shapefile: " + writer.errorMessage())

        for fid in excluded_ids:
            writer.addFeature(feature_dict[fid])

        del writer

    def save_filtered_points(self, layer, output_path):
        spatial_index = QgsSpatialIndex()
        feature_dict = {f.id(): f for f in layer.getFeatures()}
        step_distance = 1  # assuming CRS units are in feet, for 1 meter
        already_excluded = set()

        # Define a small distance to consider points as neighbors
        # neighbor_distance = 3.5  # Adjust this value based on your CRS units (FEET)
        neighbor_distance = 5  # Adjust this value based on your CRS units (METER)

        # Function to check if a feature is part of a small cluster
        def is_part_of_small_cluster(fid, feature_dict, spatial_index, neighbor_distance, max_cluster_size):
            feature = feature_dict[fid]
            point = feature.geometry()
            # Find neighbors within a small distance
            neighbors = spatial_index.nearestNeighbor(point, max_cluster_size + 1, neighbor_distance)  # +1 to include the feature itself
            QgsMessageLog.logMessage(f'There are {len(neighbors)} neighbors within {neighbor_distance} meters of {point}', 'RoadFinder')
            if len(neighbors) < max_cluster_size:
                return True
            return False

        # Function to check if a point has 10 consecutive neighbors in any direction
        def has_ten_consecutive_neighbors(fid, feature_dict, spatial_index, step_distance):
            feature = feature_dict[fid]
            point = feature.geometry().asPoint()
            directions = {
                'left': (-step_distance, 0),
                'right': (step_distance, 0),
                'up': (0, step_distance),
                'down': (0, -step_distance)
            }

            # This tolerance must correspond to the maximum allowed distance between points on the grid.
            tolerance = 0.1

            for direction, (dx, dy) in directions.items():
                consecutive_neighbors = 0

                for i in range(1, 11):  # Check for the next 10 points in the direction
                    # Calculate the expected location of the next neighbor
                    expected_location = QgsPointXY(point.x() + dx * i, point.y() + dy * i)

                    # Find the nearest neighbor to the expected location
                    nearest_ids = spatial_index.nearestNeighbor(expected_location, 0.5)

                    if not nearest_ids:
                        # No neighbor found, not consecutive
                        return False

                    nearest_id = nearest_ids[0]
                    if nearest_id == fid:
                        # It's the same point, skip it
                        continue

                    # Get the actual location of the nearest neighbor
                    nearest_feature = feature_dict[nearest_id]
                    nearest_point = nearest_feature.geometry().asPoint()

                    # Check if the nearest neighbor is within the tolerance of the expected location
                    if expected_location.distance(nearest_point) > tolerance:
                        # Neighbor is too far from the expected location, not consecutive
                        return False
                    else:
                        consecutive_neighbors += 1

                if consecutive_neighbors < 10:
                    # Less than 10 consecutive neighbors in this direction, don't exclude
                    return False

            # If the function hasn't returned False yet, it means there are 10 consecutive neighbors in all directions
            # Exclude this point and its neighbors within a 10-step radius
            radius = 10 * step_distance
            ids_within_radius = spatial_index.nearestNeighbor(point, 70, int(radius / step_distance))

            # Collect IDs to exclude, ensuring they're not the central point and they're not already in the set
            points_to_exclude = set(ids_within_radius) - {fid}
            return points_to_exclude

        # Initialize the set of points already excluded
        already_excluded = set()

        # Identify clusters with less than 20 points
        for fid in feature_dict.keys():
            if is_part_of_small_cluster(fid, feature_dict, spatial_index, neighbor_distance, 20):
                already_excluded.add(fid)

        # Identify points with 10 consecutive neighbors in all directions
        for fid in feature_dict.keys():
            if fid not in already_excluded:
                points_to_exclude = has_ten_consecutive_neighbors(fid, feature_dict, spatial_index, step_distance)
                already_excluded.update(points_to_exclude)

        # Rest of your code ...

        # Define the fields for the output layer
        fields = QgsFields()
        for field in layer.fields():
            fields.append(field)

        # Export the excluded points to a separate shapefile
        excluded_output_path = output_path.replace('.shp', '_excluded.shp')
        self.export_excluded_points_to_shapefile(already_excluded, feature_dict, excluded_output_path, layer.crs())

        # Add features that were not excluded to the shapefile
        writer = QgsVectorFileWriter(
            output_path,
            "UTF-8",
            layer.fields(),
            QgsWkbTypes.Point,
            layer.crs(),
            "ESRI Shapefile"
        )

        if writer.hasError() != QgsVectorFileWriter.NoError:
            raise Exception("Error when creating shapefile: " + writer.errorMessage())

        for fid, feature in feature_dict.items():
            if fid not in already_excluded:
                writer.addFeature(feature)

        del writer  # Ensure that the writer is closed properly


    def finished(self, result):
        if result:
            QgsMessageLog.logMessage('Task "{}" finished successfully'.format(self.description()), 'RoadFinder')
        else:
            QgsMessageLog.logMessage('Task "{}" did not finish successfully'.format(self.description()), 'RoadFinder')

    def cancel(self):
        QgsMessageLog.logMessage('Task "{}" was canceled'.format(self.description()), 'RoadFinder')
        super().cancel()


class RoadFinder(QgsTask):
    def __init__(self, slope_raster, road_finder_dir, streams_shp, processed_pts, proj_num):
        super().__init__("Road Finder Algorithm", QgsTask.CanCancel)
        self.slope_raster = slope_raster
        self.road_finder_dir = road_finder_dir
        self.streams_shp = streams_shp
        self.processed_pts = processed_pts
        self.proj_num = proj_num
        self.feedback = QgsProcessingFeedback()
        self.spatial_index = QgsSpatialIndex()
        self.step_distance = 3.280839895013123
        self.small_neighbor_distance = 25
        self.tiny_neighbor_distance = 15
        self.big_neighbor_distance = 100
        self.max_cluster_size = 425
        self.min_cluster_size = 75
        self.tiny_max_cluster_size = 425
        self.tiny_min_cluster_size = 25
        self.value_threshold = 40
        self.exclusion_limit = 0
        self.min_points = 25
        self.max_points = 85
        self.excluded_points = set()
        self.selected_points = set()
        self.visited_points = set()
        self.selected_points_shp = f"{self.road_finder_dir}{proj_num}_SELECTED_POINTS.shp"
        self.excluded_points_shp = f"{self.road_finder_dir}{proj_num}_EXCLUDED_POINTS.shp"
        self.crs = QgsCoordinateReferenceSystem(26910)
        self.fiona_crs = from_epsg(26910)

    def run(self):
        QgsMessageLog.logMessage("Starting Road Finder Algorithm", "RoadFinder")
        slope = gdal.Open(self.slope_raster, gdal.GA_ReadOnly)
        transform = slope.GetGeoTransform()
        x_origin = transform[0]
        y_origin = transform[3]
        pixel_width = transform[1]
        pixel_height = -transform[5]
        band = slope.GetRasterBand(1)
        slope_array = band.ReadAsArray()

        crs = QgsCoordinateReferenceSystem(slope.GetProjection())
        schema = {
            'geometry': 'Point',
            'properties': {'Value': 'float'}
        }

        # ranges = [(0, 24), (24, 32), (32, 40), (40, 45), (0, 45)]
        # filenames = ["OUTPUT_POINTS_0-24", "OUTPUT_POINTS_24-32",
        #              "OUTPUT_POINTS_32-40", "OUTPUT_POINTS_40-45", "OUTPUT_POINTS_45"]
        ranges = [(0, 35)]
        filenames = ["OUTPUT_POINTS_35"]

        for value_range, filename in zip(ranges, filenames):
            filtered_points = f"{self.road_finder_dir}{filename}.shp"
            self.get_points(slope_array, value_range, filtered_points, self.fiona_crs, schema, x_origin, y_origin, pixel_width, pixel_height)

        filtered_layer = QgsVectorLayer(filtered_points, "Filtered Points", "ogr")

        # Create buffer around streams
        params = {
            'INPUT': self.streams_shp,
            'DISTANCE': 8,
            'OUTPUT': 'memory:'
        }
        buffer_result = processing.run("native:buffer", params, feedback=self.feedback)
        buffer_layer = buffer_result['OUTPUT']

        # Process each shapefile to exclude points within the buffer
        for value_range, filename in zip(ranges, filenames):
            output_shp_path = f"{self.road_finder_dir}{filename}_BUFFER_EXCLUSION.shp"

            params = {
                'INPUT': filtered_layer,
                'PREDICATE': [2],  # 2 corresponds to does not intersect
                'INTERSECT': buffer_layer,
                'OUTPUT': output_shp_path
            }
            processing.run("qgis:extractbylocation", params, feedback=self.feedback)

        road_point_layer = QgsVectorLayer(output_shp_path, "Road Points", "ogr")
        feature_dict = {f.id(): f for f in road_point_layer.getFeatures()}
        for feature in road_point_layer.getFeatures():
            self.spatial_index.insertFeature(feature)

        # for feature in road_point_layer.getFeatures():
        #     if feature.id() not in self.excluded_points:
        #         self.cluster_check(feature.id(), feature_dict, self.small_neighbor_distance, self.max_cluster_size,
        #                            self.min_cluster_size, self.value_threshold, self.min_points, self.max_points,
        #                            self.exclusion_limit)

        for feature in road_point_layer.getFeatures():
            if feature.id() not in self.excluded_points:
                self.cluster_check(feature.id(), feature_dict, self.tiny_neighbor_distance, self.tiny_max_cluster_size,
                                   self.tiny_min_cluster_size, self.value_threshold, self.min_points, self.max_points,
                                   self.exclusion_limit)

        self.write_shapefile(self.selected_points, road_point_layer, self.selected_points_shp, crs)
        self.write_shapefile(self.excluded_points, road_point_layer, self.excluded_points_shp, crs)

        del road_point_layer

        return True

    def cluster_check(self, fid, feature_dict, neighbor_distance, max_cluster_size, min_cluster_size, value_threshold,
                      min_points, max_points, exclusion_limit):
        geometry = feature_dict[fid].geometry()
        if geometry.type() == QgsWkbTypes.PointGeometry:
            point_ft = geometry.asPoint()
            point_xy = QgsPointXY(point_ft.x(), point_ft.y())
            if fid not in self.excluded_points and fid not in self.selected_points:
                neighbor_points = self.spatial_index.nearestNeighbor(point_xy, neighbors=1000,
                                                                     maxDistance=neighbor_distance)
                neighbor_ids = set(neighbor_points) - self.visited_points

                if not min_points < len(neighbor_ids) <= max_points:
                    if len(neighbor_ids) > max_cluster_size or len(neighbor_ids) < min_cluster_size:
                        for neighbor in neighbor_ids:
                            if neighbor not in self.excluded_points and neighbor not in self.selected_points:
                                self.excluded_points.update({neighbor})
                    else:
                        for neighbor in neighbor_ids:
                            if neighbor not in self.excluded_points and neighbor not in self.selected_points:
                                self.selected_points.update({neighbor})
                else:
                    # Only add points that are below the value threshold
                    for neighbor in neighbor_ids:
                        neighbor_feature = feature_dict[neighbor]
                        neighbor_value = neighbor_feature['Value']  # Replace 'Value' with your actual field name
                        if neighbor_value < value_threshold:
                            self.selected_points.update({neighbor})

                # Mark as visited
                # self.visited_points.update(neighbor_ids)
        else:
            QgsMessageLog.logMessage(f"Feature ID {fid} does not have point geometry", level=Qgis.Warning)

    def get_points(self, raster_array, value_range, output_path, crs, schema, x_origin, y_origin, pixel_width, pixel_height):
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

    def write_shapefile(self, point_ids, layer, output_path, crs):
        fields = layer.fields()  # Get fields from the layer
        writer = QgsVectorFileWriter(output_path, 'UTF-8', fields,
                                     QgsWkbTypes.Point, crs, 'ESRI Shapefile')
        try:
            if writer.hasError() != QgsVectorFileWriter.NoError:
                raise Exception(f"Error when creating shapefile: {writer.errorMessage()}")

            for fid in point_ids:
                feature = layer.getFeature(fid)
                if feature:
                    writer.addFeature(feature)
        except Exception as e:
            QgsMessageLog.logMessage(str(e), level=Qgis.Critical)
        finally:
            # This ensures that the writer and its resources are cleaned up
            del writer

        QgsMessageLog.logMessage(f"Shapefile {output_path} written successfully.", level=Qgis.Info)

    def finished(self, result):
        if result:
            QgsMessageLog.logMessage('Task "{}" finished successfully'.format(self.description()), 'RoadFinder')
        else:
            QgsMessageLog.logMessage('Task "{}" did not finish successfully'.format(self.description()), 'RoadFinder')

    def cancel(self):
        QgsMessageLog.logMessage('Task "{}" was canceled'.format(self.description()), 'RoadFinder')
        super().cancel()


class DemRaster(QgsTask):
    def __init__(self, source, parcel, destination, buffer_dem):
        super().__init__("DEM Raster Processing", QgsTask.CanCancel)
        self.source = source
        self.parcel = parcel
        self.destination = destination
        self.buffer_dem = buffer_dem
        self.window = None
        self.raster_data = None
        self.src_crs = None
        self.epsg_code = None

    def run(self):
        with rasterio.open(self.source) as src:
            src_transform = src.transform
            src_nodata = src.nodata
            self.src_crs = src.crs

            # Calculate the buffer
            project_parcel = gpd.read_file(self.parcel)
            poly = project_parcel.iloc[0]
            buffer = poly.geometry.buffer(self.buffer_dem)

            # Transform the buffer to the same CRS as the raster
            buffer_gdf = gpd.GeoDataFrame(index=[0], geometry=[buffer])
            buffer_gdf = buffer_gdf.set_crs('epsg:2225')
            buffer_gdf = buffer_gdf.to_crs(self.src_crs)

            # Get the bounds of the buffer
            left, bottom, right, top = buffer_gdf.bounds.iloc[0]

            # Get the window of the raster that intersects with the buffer
            self.window = rasterio.windows.from_bounds(left=left, bottom=bottom, right=right, top=top,
                                                  transform=src_transform)

            # Read the raster data within the window
            self.raster_data = src.read(1, window=self.window)

            # Mask the NaN values
            mask = ~np.isnan(self.raster_data)
            rows, cols = np.where(mask)

            # If there are no NaN values, the bounds will remain the same
            if not mask.all():
                left = np.min(cols)
                right = np.max(cols)
                top = np.min(rows)
                bottom = np.max(rows)

                # Apply the window transformation to get the bounds in the raster's coordinate system
                left, top = src_transform * (left, top)
                right, bottom = src_transform * (right, bottom)

            # Create the window using the new bounds
            self.window = rasterio.windows.from_bounds(left=left, bottom=bottom, right=right, top=top,
                                                  transform=src_transform)

            # Read the data again with the new window
            self.raster_data = src.read(1, window=self.window)

            # Set the NoData values to NaN
            raster_data = np.where(self.raster_data == src_nodata, np.nan, self.raster_data)

            # Get the width and height of the clipped raster
            out_width = self.window.width
            out_height = self.window.height

            # Calculate the transform of the clipped raster
            src_transform = rasterio.transform.from_bounds(left, bottom, right, top, out_width, out_height)
            self.epsg_code = src.crs.to_string()

            return True

    def finished(self, result):
        if result:
            QgsMessageLog.logMessage("Digital Elevation Model (DEM) processing complete.")
            dem_finished = True

            # Save the clipped raster data to a new file
            with rasterio.open(self.destination, 'w', driver='GTiff', width=self.window.width, height=self.window.height,
                               count=1, dtype=self.raster_data.dtype, crs=self.src_crs, transform=self.src_transform,
                               nodata=np.nan) as dst:
                dst.write(self.raster_data, 1)

            if ':' in self.epsg_code:
                epsg_in = int(self.epsg_code.split(":")[-1])
            else:
                crs_obj = QgsCoordinateReferenceSystem.fromWkt(self.epsg_code)
                if crs_obj.isValid():
                    epsg_in = crs_obj.postgisSrid()
                else:
                    QgsMessageLog.logMessage(f"Could not parse CRS from: {self.epsg_code}", level=Qgis.Critical)
                    return None
        else:
            QgsMessageLog.logMessage("Task was canceled or failed.")






















