# -*- coding: utf-8 -*-


__author__ = 'Tyler Martin'
__date__ = '2023-06-16'
__copyright__ = '(C) 2023 by Tyler Martin'
__revision__ = '$Format:%H$'

from osgeo import gdal, osr, ogr
import shutil
import subprocess
import datetime
import time
from PyQt5 import sip
import pyproj
import json
import sys
from PyQt5 import sip
import gc
from urllib.parse import urlsplit, unquote
from requests.exceptions import ChunkedEncodingError, RequestException
import requests
import zipfile
import rasterio
import ezdxf
from rasterio import windows, merge
import rasterio.coords
import geopandas as gpd
import numpy as np
import skimage
import skimage.measure
from shapely.wkt import dumps
import os
import re
from functools import partial
import time
from time import sleep
import logging
import qgis
from qgis import processing
from qgis.utils import iface
from qgis.core import (
    Qgis,
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsCoordinateTransformContext,
    QgsExpression,
    QgsFields,
    QgsFeature,
    QgsFeatureRequest,
    QgsGeometry,
    QgsLayerTreeLayer,
    QgsLayerTreeUtils,
    QgsLayoutItemLegend,
    QgsLayoutItemMap,
    QgsLayoutItemScaleBar,
    QgsLayoutExporter,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsMessageLog,
    QgsPointXY,
    QgsPrintLayout,
    QgsProject,
    QgsProcessingAlgorithm,
    QgsProcessingAlgRunnerTask,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsPrintLayout,
    QgsRasterPipe,
    QgsRasterLayer,
    QgsRectangle,
    QgsRasterFileWriter,
    QgsSpatialIndex,
    QgsTask,
    QgsUnitTypes,
    QgsVector,
    QgsVectorLayer,
    QgsVectorFileWriter,
    QgsWkbTypes,
)
from qgis.gui import (
    QgsMapCanvas,
)
from qgis.PyQt.QtCore import (
    QCoreApplication,
    QVariant,
    Qt,
    pyqtSignal,
    QTimer,
    QRegExp,
    QObject,
)
from qgis.PyQt.QtGui import (
    QPixmap,
    QColor,
    QRegExpValidator
)
from qgis.PyQt.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QDesktopWidget,
    QLineEdit,
    QListWidget,
    QGroupBox,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QMessageBox,
    QHBoxLayout,
    QProgressBar,
    QTextEdit,
    QApplication,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
    QStyle,
)

from .source_variables import *
from .gui import *
from .projinit_tools import *

global project_file, home_test, test_file, test_mode, laptop_mode, selected_files_status, selected_site_data_status, \
    selected_raster_status, file_path_loc, destination_gis, multiple_apn, apn_list, prj_folder, proj_apn, proj_name, \
    proj_num, proj_test, proj_type, dxf_choice, map_choice, folder_choice, buffer_radius, buffer_parcels, buffer_dem, \
    source_shp, destination_shp, qgis_path, r_layer1, destination_ras, dwg_folder, output_dst, proposal_check, \
    raster_file, input_epsg, dem1m, layer, buffer_layer, dst_file, layer_name, parcel_center, goog_geo_dst, \
    destination_dxf, destination_map, project, naip_temp, crs, year_dbl, mem_layer, goog_task, dem_radius_buffer, \
    output_epsg, goog_layer, raster_task, contour_task, hillshade_dst, flow_accumulation_dst


class procplug1Algorithm(QgsProcessingAlgorithm):
    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.
    dialog = None
    finished_processing = pyqtSignal()
    final_dialog = FinalDialog()

    global selected_files_status, prj_folder, file_path_loc, destination_gis

    # INPUT_PARAM1 = 'apn_list' # need to go through code for proj_apn and alter to do lists
    INPUT_PARAM2 = 'client_name'
    INPUT_PARAM3 = 'proj_num'
    INPUT_PARAM4 = 'other_proj'
    INPUT_PARAM5 = 'proj_type'
    INPUT_PARAM6 = 'dxf_choice'
    INPUT_PARAM7 = 'map_choice'
    INPUT_PARAM8 = 'folder_choice'
    INPUT_PARAM9 = 'road_choice'
    INFO_TEXT = 'proj_info'
    OP_PROJECT_FILE = 'OP_PROJECT_FILE'

    def initAlgorithm(self, config, **kwargs):
        pass

    def processAlgorithm(self, parameters, context, feedback, **kwargs):
        global project_file, home_test, test_file, test_mode, laptop_mode, proj_apn, proj_name, proj_num, proj_test, \
            proj_type, dxf_choice, map_choice, folder_choice, selected_files_status, buffer_radius, apn_list, \
            buffer_parcels, buffer_dem, prj_folder, file_path_loc, destination_gis

        buffer_radius = 0
        buffer_parcels = 0
        buffer_dem = 0

        self.dialog = CustomInputDialog()

        result = self.dialog.exec()

        QApplication.processEvents()

        if result == QDialog.Rejected:  # Check for rejection
            return {}  # return an empty dictionary or handle as needed

        if result == QDialog.Accepted:  # Handle the accepted result
            params = self.dialog.get_parameters()
            apn_list = params['apn_list']
            proj_name = params['proj_name']
            proj_num = params['proj_num']
            proj_test = params['proj_test']
            proj_type = params['proj_type']
            dxf_choice = params['dxf_choice']
            map_choice = params['map_choice']
            buffer_radius = params['buffer_radius']
            buffer_parcels = params['buffer_parcels']
            buffer_dem = params['buffer_dem']
            folder_choice = params['folder_choice']
            road_choice = params['road_choice']

        # Project parameters
        today = datetime.datetime.now()

        def execute_code():
            # noinspection PyGlobalUndefined
            global source_shp, destination_shp, qgis_path, r_layer1, destination_ras, dwg_folder, prj_folder, \
                output_dst, proposal_check, raster_file, input_epsg, dem1m, layer, buffer_layer, project_file, \
                dst_file, layer_name, home_test, parcel_center, goog_geo_dst, destination_dxf, destination_map, \
                apn_list, proj_name, proj_num, proj_test, proj_type, dxf_choice, map_choice, folder_choice, home_test, \
                test_file, test_mode, laptop_mode, project, naip_temp, selected_files_status, crs, proj_apn, \
                buffer_radius, buffer_parcels, buffer_dem, file_path_loc, destination_gis, year_dbl, selected_dst,\
                adjacent_dst, buffer_dst, surrounding_dst, road_dst, streams_dst, city_dst, zoning_dst, precip_sep, \
                gplan_dst, planning_dst, service_dst, public_dst, williamson_dst, fire_dst, coastal_dst, fema_dst, \
                slope_stab_dst, slope_stab_bay, alquist_pri_dst, ag_lands_dst, bio_res_dst, liquefaction_dst, \
                airport_rnwy_dst, airport_point_dst, tiger_rds_cnty_dst, tiger_rds_dst, forest_srvc_rds_dst, \
                rail_dst, trail_dst, timber_harvest_dst, soils_dst, slope_30_dst, slope_15_dst, fire_risk_dst, \
                woodland_dst, invasive_dst, faultline_dst, bedrock_dst, wetlands_dst, millcreek_wetlands_dst, \
                fire_hydrants_dst, structures_dst, temp_min_dst, temp_max_dst, mintemp_dst, maxtemp_dst, \
                precip_jan, precip_feb, precip_mar, precip_apr, precip_may, precip_jun, precip_jul, precip_aug, \
                precip_oct, precip_nov, precip_dec, destination_1m_dem, destination_1m_simms, destination_1m_klam, \
                destination_1m_horse, destination_dem, goog_geo_dst, goog_geo2225, naip_dst, naip_temp, slope_per, \
                map_dst, src_layer, merged_geometry, road_points_first, road_points_second, road_points_third, \
                road_points_fourth, road_points_all, road_points_all_exclude, road_finder_path, flow_accumulation_dst, \
                dem_task_1, dem_task_2, dem_task_3, tsunami_dst, airport_comp_dst, legacy_humco_cl_dst, \
                fire_station_dst, slope_deg, precip_annual, dem_radius_buffer, hillshade_dst

            progress_window = ProgressWindow()
            progress_window.show()  # Show the window first

            progress_window.show_message("Initializing project files and checking to see if project exists")

            final_dialog_instance = FinalDialog()

            QApplication.processEvents()

            proj_name = proj_name.strip()
            proj_num = proj_num.strip()
            buffer_radius = max(50, min(buffer_radius, 5000))
            buffer_parcels = max(50, min(buffer_parcels, 5000))
            buffer_dem = max(50, min(buffer_dem, 5000))

            progress_window.set_progress(2)

            if not proj_test:
                output_dst = output_dst_default
                contract_path_loc = f'{output_dst}Projects_Civil3D/'
            else:
                output_dst = output_dst_test
                check_folder_create(output_dst)
                contract_path_loc = f'{output_dst}'
                progress_window.show_message(f"Generating project files in {output_dst}")

            check_folder_create(prop_path_loc)

            if not proj_type:
                file_path_loc = f'{contract_path_loc}{str(today.year)[-2:]}-'
                progress_window.show_message("Creating new contracted project")
                progress_window.show_message("Creating project folders")
            else:
                file_path_loc = prop_path_loc
                proj_num_last = find_highest_proposal_number(file_path_loc)
                proposal_num = proj_num_last + 1
                year_dbl = str(today.year)
                year_dbl_clip = year_dbl[-2:]
                proj_num = f'E{year_dbl_clip}-{proposal_num}'
                progress_window.show_message("Creating proposal file")
                progress_window.show_message("Creating project folders")

            prj_folder = f"{file_path_loc}{proj_num}_{proj_name}/"
            destination_gis = f"{prj_folder}gis/"
            destination_shp = f"{destination_gis}PROJECT SHAPEFILES/"
            destination_ras = f"{destination_gis}GEOREF_RASTER/"
            destination_dxf = f"{prj_folder}dwg/"
            destination_map = f"{prj_folder}image/"

            folder_exists, project_path = check_folder_prj(proj_num, proj_name, prj_folder, source_shp)
            destination_gis = f"{project_path}/gis_new/" if folder_exists and not proj_test else f"{prj_folder}gis/"
            destination_shp = f"{destination_gis}PROJECT SHAPEFILES/"
            destination_ras = f"{destination_gis}GEOREF_RASTER/"
            destination_dxf = f"{project_path}/dwg/" if folder_exists and not proj_test else f"{prj_folder}dwg/"
            destination_map = f"{project_path}/image/" if folder_exists and not proj_test else f"{prj_folder}image/"
            check_folder_create(destination_gis)
            check_folder_create(destination_shp)
            check_folder_create(destination_ras)
            if dxf_choice: check_folder_create(destination_dxf)
            if map_choice: check_folder_create(destination_map)
            if folder_exists and not proj_test:
                progress_window.show_message("Project folder already exists, output will be in 'gis_new'")

            # Define the output location for the shapefiles
            selected_dst = f'{destination_shp}{proj_num}_Project_Parcel-2225.shp'
            adjacent_dst = f'{destination_shp}{proj_num}_Adjacent_Parcels-2225.shp'
            buffer_dst = f'{destination_shp}{proj_num}_Buffer_Parcels-2225.shp'
            surrounding_dst = f'{destination_shp}{proj_num}_Surrounding Parcels-2225.shp'
            road_dst = f'{destination_shp}{proj_num}_Road_Centerline-2225.shp'
            streams_dst = f'{destination_shp}{proj_num}_Streams-2225.shp'
            streams_cnty_dst = f'{destination_shp}{proj_num}_Streams_County-2225.shp'
            city_dst = f'{destination_shp}{proj_num}_City_Limits-2225.shp'
            zoning_dst = f'{destination_shp}{proj_num}_Zoning-2225.shp'
            gplan_dst = f'{destination_shp}{proj_num}_General_Plan_Land_Use-2225.shp'
            planning_dst = f'{destination_shp}{proj_num}_Planning-2225.shp'
            service_dst = f'{destination_shp}{proj_num}_Service_Districts-2225.shp'
            public_dst = f'{destination_shp}{proj_num}_Public_Lands-2225.shp'
            williamson_dst = f'{destination_shp}{proj_num}_Williamson_Act-2225.shp'
            fire_dst = f'{destination_shp}{proj_num}_Fire_Districts-2225.shp'
            coastal_dst = f'{destination_shp}{proj_num}_Coastal_Zone-2225.shp'
            fema_dst = f'{destination_shp}{proj_num}_Flood Zone-2225.shp'
            slope_stab_dst = f'{destination_shp}{proj_num}_Slope_Stability-2225.shp'
            slope_stab_bay = f'{destination_shp}{proj_num}_Slope_Stability_BAY-2225.shp'
            alquist_pri_dst = f'{destination_shp}{proj_num}_AlquistPriolo_Zone-2225.shp'
            ag_lands_dst = f'{destination_shp}{proj_num}_AgLands-2225.shp'
            bio_res_dst = f'{destination_shp}{proj_num}_Biological_Resources-2225.shp'
            liquefaction_dst = f'{destination_shp}{proj_num}_Liquefaction_Area-2225.shp'
            mask_temp_dst = f'{destination_shp}{proj_num}_mask_temp.shp'

            # RoadFinder stuff for output locations
            road_finder_path = f'{destination_shp}ROAD_FINDER_TEST/'
            road_points_first = f'{road_finder_path}{proj_num}_OUTPUT_POINTS_0-24.shp'
            road_points_second = f'{road_finder_path}{proj_num}_OUTPUT_POINTS_24-32.shp'
            road_points_third = f'{road_finder_path}{proj_num}_OUTPUT_POINTS_32-40.shp'
            road_points_fourth = f'{road_finder_path}{proj_num}_OUTPUT_POINTS_40-45.shp'
            road_points_all = f'{road_finder_path}{proj_num}_OUTPUT_POINTS_45.shp'
            road_points_first_exclude = f'{road_finder_path}{proj_num}_OUTPUT_POINTS_0-24_BUFFER EXCLUSION.shp'
            road_points_second_exclude = f'{road_finder_path}{proj_num}_OUTPUT_POINTS_24-32_BUFFER EXCLUSION.shp'
            road_points_third_exclude = f'{road_finder_path}{proj_num}_OUTPUT_POINTS_32-40_BUFFER EXCLUSION.shp'
            road_points_fourth_exclude = f'{road_finder_path}{proj_num}_OUTPUT_POINTS_40-45_BUFFER EXCLUSION.shp'
            road_points_all_exclude = f'{road_finder_path}{proj_num}_OUTPUT_POINTS_45_BUFFER EXCLUSION.shp'

            # New datasets
            airport_comp_dst = f'{destination_shp}{proj_num}_Airport_Compatibility_Zone-2225.shp'
            airport_rnwy_dst = f'{destination_shp}{proj_num}_Airport_Runway-2225.shp'
            airport_point_dst = f'{destination_shp}{proj_num}_Airports-2225.shp'
            tiger_rds_cnty_dst = f'{destination_shp}{proj_num}_RoadCL-US_CENSUS_TIGER_DATA-Cnty-2225.shp'
            tiger_rds_dst = f'{destination_shp}{proj_num}_RoadCL-US_CENSUS_TIGER_DATA-2225.shp'
            forest_srvc_rds_dst = f'{destination_shp}{proj_num}_RoadCL-Forest_Service-2225.shp'
            legacy_humco_cl_dst = f'{destination_shp}{proj_num}_RoadCL_Legacy-HumCnty-2225.shp'
            rail_dst = f'{destination_shp}{proj_num}_HumCo_Railway-2225.shp'
            trail_dst = f'{destination_shp}{proj_num}_HumCo_Trails-2225.shp'
            timber_harvest_dst = f'{destination_shp}{proj_num}_Timber_Harvest_Areas-2225.shp'
            soils_dst = f'{destination_shp}{proj_num}_Soil_Classification-2225.shp'
            slope_30_dst = f'{destination_shp}{proj_num}_Slope_30%-2225.shp'
            slope_15_dst = f'{destination_shp}{proj_num}_Slope_15%-2225.shp'
            fire_risk_dst = f'{destination_shp}{proj_num}_Fire_Risk-2225.shp'
            tsunami_dst = f'{destination_shp}{proj_num}_Tsunami_Zone-2225.shp'
            woodland_dst = f'{destination_shp}{proj_num}_Woodland_Areas-2225.shp'
            invasive_dst = f'{destination_shp}{proj_num}_Invasive_Plants-2225.shp'
            faultline_dst = f'{destination_shp}{proj_num}_Earthquake_Fault_Lines-2225.shp'
            bedrock_dst = f'{destination_shp}{proj_num}_Bedrock-2225.shp'
            wetlands_dst = f'{destination_shp}{proj_num}_Wetlands-2225.shp'
            millcreek_wetlands_dst = f'{destination_shp}{proj_num}_Mill_Creek_Wetlands-2225.shp'
            fire_station_dst = f'{destination_shp}{proj_num}_Fire_Stations-2225.shp'
            fire_hydrants_dst = f'{destination_shp}{proj_num}_Fire_Hydrants-2225.shp'
            structures_dst = f'{destination_shp}{proj_num}_HumCo_Structures-2225.shp'
            temp_min_dst = f'{destination_shp}{proj_num}_Temp_1981-2010_MIN-2225.shp'
            temp_max_dst = f'{destination_shp}{proj_num}_Temp_1981-2010_MAX-2225.shp'
            mintemp_dst = f'{destination_shp}{proj_num}_Minimum_Temp-2225.shp'
            maxtemp_dst = f'{destination_shp}{proj_num}_Maximum_Temp-2225.shp'
            precip_annual = f'{destination_shp}{proj_num}_Annual_Precipitation-2225.shp'
            precip_jan = f'{destination_shp}{proj_num}_Mnthly_Precip-JAN-2225.shp'
            precip_feb = f'{destination_shp}{proj_num}_Mnthly_Precip-FEB-2225.shp'
            precip_mar = f'{destination_shp}{proj_num}_Mnthly_Precip-MAR-2225.shp'
            precip_apr = f'{destination_shp}{proj_num}_Mnthly_Precip-APR-2225.shp'
            precip_may = f'{destination_shp}{proj_num}_Mnthly_Precip-MAY-2225.shp'
            precip_jun = f'{destination_shp}{proj_num}_Mnthly_Precip-JUN-2225.shp'
            precip_jul = f'{destination_shp}{proj_num}_Mnthly_Precip-JUL-2225.shp'
            precip_aug = f'{destination_shp}{proj_num}_Mnthly_Precip-AUG-2225.shp'
            precip_sep = f'{destination_shp}{proj_num}_Mnthly_Precip-SEP-2225.shp'
            precip_oct = f'{destination_shp}{proj_num}_Mnthly_Precip-OCT-2225.shp'
            precip_nov = f'{destination_shp}{proj_num}_Mnthly_Precip-NOV-2225.shp'
            precip_dec = f'{destination_shp}{proj_num}_Mnthly_Precip-DEC-2225.shp'

            # Define the output location for the rasters and map file
            destination_1m_dem = f'{destination_ras}{proj_num}_1M_USGS_DEM-CLIPPED.tif'
            destination_1m_simms = f'{destination_ras}{proj_num}_1M_SIMMS-FIRE 2012_DEM-CLIPPED.tif'
            destination_1m_klam = f'{destination_ras}{proj_num}_1M_KLAMATH DEM-CLIPPED.tif'
            destination_1m_horse = f'{destination_ras}{proj_num}_1M_HORSE_LINTO DEM-CLIPPED.tif'
            destination_dem = f'{destination_ras}{proj_num}_HumCo_10M_DEM-CLIPPED-2225.tif'
            goog_geo_dst = f'{destination_ras}{proj_num}_goog_temp.tif'
            goog_geo2225 = f'{destination_ras}{proj_num}_GOOG SATELLITE_GEOREF-2225.tif'
            naip_dst = f'{destination_ras}{proj_num}_NAIP-2225.tif'
            naip_temp = f'{destination_ras}{proj_num}_naip_temp.tif'
            slope_per = f'{destination_ras}{proj_num}_SLOPE(PERCENT).tif'
            slope_deg = f'{destination_ras}{proj_num}_SLOPE(DEGREE).tif'
            hillshade_dst = f'{destination_ras}{proj_num}_HILLSHADE-RELIEF.tif'
            flow_accumulation_dst = f'{destination_ras}{proj_num}_FLOW_ACCUMULATION.tif'
            map_dst = f'{destination_map}PROJECT_OVERVIEW_MAP.png'

            # Load the remaining shapefiles for Humboldt County
            file_list = [
                ('City Limits', 'City Limits.shp', city_dst),
                ('Humboldt County Zoning', 'HumCo_Zoning.shp', zoning_dst),
                ('General Plan Land Use', 'Land Use.shp', gplan_dst),
                ('Community Planning Areas', 'HumCo_Planning.shp', planning_dst),
                ('Community Service Districts', 'HumCo_Service_Districts.shp', service_dst),
                ('Public Lands', 'HumCo_Public_Lands.shp', public_dst),
                ('Williamson Act Lands', 'HumCo_Williamson_Act.shp', williamson_dst),
                ('Fire District', 'HumCo_Fire_Districts.shp', fire_dst),
                ('Coastal Zone', 'HumCo_Coastal_Zone.shp', coastal_dst),
                ('Flood Zone', 'HumCo_FEMA.shp', fema_dst),
                ('Slope Stability (COUNTY)', 'SlopeStability_HUM.shp', slope_stab_dst),
                ('Slope Stability (HUMBOLDT BAY)', 'SlopeStab_BAY.shp', slope_stab_bay),
                ('Alquist-Priolo Zones', 'AlquistPriolo.shp', alquist_pri_dst),
                ('Agricultural Lands', 'AgLands.shp', ag_lands_dst),
                ('Biological Resource Areas', 'Bio_Res.shp', bio_res_dst),
                ('Liquefaction Zones', 'Liquefaction.shp', liquefaction_dst),
                ('Airport Compatibility Zone', 'Airport_Comp.shp', airport_comp_dst),
                ('Airport Locations', 'Airports.shp', airport_point_dst),
                ('Airport Runways', 'AirportRunway.shp', airport_rnwy_dst),
                ('US Census Road Data (County Corrected)', 'TIGER_RoadCL.shp', tiger_rds_cnty_dst),
                ('US Census Road Data', 'TIGER_Roads.shp', tiger_rds_dst),
                ('Forest Service Roads', 'USFS_Roads.shp', forest_srvc_rds_dst),
                ('Legacy Humboldt County Road Linework', 'LegacyRoadLines.shp', legacy_humco_cl_dst),
                ('Railways', 'HumCo_Rail.shp', rail_dst),
                ('Hiking Trails', 'HumCo_Trails.shp', trail_dst),
                ('Timber Harvest Areas', 'TimberHarvest.shp', timber_harvest_dst),
                ('Soil Classification', 'HumCo_Soils.shp', soils_dst),
                ('Slopes Greater than 30%', 'slope30.shp', slope_30_dst),
                ('Slopes Less than 15%', 'slope15.shp', slope_15_dst),
                ('Wildland Fire Risk', 'Fire_Risk.shp', fire_risk_dst),
                ('Tsunami Inundation Zone', 'tsunami.shp', tsunami_dst),
                ('Woodland Cover', 'Woodland.shp', woodland_dst),
                ('Invasive Plant Species', 'InvasivePlants.shp', invasive_dst),
                ('Earthquake Fault Lines', 'HumCo_FaultLines.shp', faultline_dst),
                ('Underlying Bedrock Composition', 'GeoClass.shp', bedrock_dst),
                ('Mapped Wetlands', 'Wetlands.shp', wetlands_dst),
                ('Mill Creek Wetlands', 'MillCreekWetlands.shp', millcreek_wetlands_dst),
                ('Fire Stations', 'FireStations.shp', fire_station_dst),
                ('Fire Hydrants', 'FireHydrants.shp', fire_hydrants_dst),
                ('Structures', 'HumCo_Structures.shp', structures_dst),
                ('Minimum Temperature', 'TempMin.shp', mintemp_dst),
                ('Maximum Temperature', 'TempMax.shp', maxtemp_dst),
                ('Minimum Temperature (1981-2010)', 'TempMin_1981-2010.shp', temp_min_dst),
                ('Maximum Temperature (1981-2010)', 'TempMax_1981-2010.shp', temp_max_dst),
                ('Annual Precipitation (1981-2010)', 'Annual.shp', precip_annual),
                ('Monthly Precipitation - January (1981-2010)', 'January.shp', precip_jan),
                ('Monthly Precipitation - February (1981-2010)', 'February.shp', precip_feb),
                ('Monthly Precipitation - March (1981-2010)', 'March.shp', precip_mar),
                ('Monthly Precipitation - April (1981-2010)', 'April.shp', precip_apr),
                ('Monthly Precipitation - May (1981-2010)', 'May.shp', precip_may),
                ('Monthly Precipitation - June (1981-2010)', 'June.shp', precip_jun),
                ('Monthly Precipitation - July (1981-2010)', 'July.shp', precip_jul),
                ('Monthly Precipitation - August (1981-2010)', 'August.shp', precip_aug),
                ('Monthly Precipitation - September (1981-2010)', 'September.shp', precip_sep),
                ('Monthly Precipitation - October (1981-2010)', 'October.shp', precip_oct),
                ('Monthly Precipitation - November (1981-2010)', 'November.shp', precip_nov),
                ('Monthly Precipitation - December (1981-2010)', 'December.shp', precip_dec),
            ]

            log_file = f'{destination_gis}log_file.log'
            logger = logging.getLogger('my_logger')
            handler = logging.FileHandler(log_file)
            logger.addHandler(handler)

            src_layer = None
            naip_final_layer = None
            stream_vector = None
            streams_cnty = None
            streams = None
            dem1m_layer_name = None
            raster_task = None
            bckgrnd_layer_task = None
            dem_processing_task = None
            dem_streams_task = None
            group3 = None
            rlayer2 = None


            progress_window.set_progress(3)
            progress_window.show_message("File initialization complete. Creating QGIS project instance.")

            # Set CRS of currently open file
            project = QgsProject.instance()
            project.setCrs(crs)
            project.setDirty(False)

            # Set save options
            save_opt = QgsVectorFileWriter.SaveVectorOptions()
            save_opt.driverName = 'ESRI Shapefile'
            save_opt.onlySelectedFeatures = True
            save_opt.fileEncoding = 'utf-8'

            # Create the layer group
            root1 = project.layerTreeRoot()
            if road_choice:
                group4 = root1.addGroup("ROAD POINTS FROM DEM (EXPERIMENTAL)")
                group4.setItemVisibilityChecked(False)
                road_point_grp = group4.addGroup("ROAD POINTS")
                road_point_grp.setItemVisibilityChecked(False)
                road_point_exclude_grp = group4.addGroup("ROAD POINTS (STREAMS EXCLUDED)")
                road_point_exclude_grp.setItemVisibilityChecked(False)
            if selected_site_data_status["Site Contours"]:
                group3 = root1.addGroup("TOPOGRAPHY (CONTOURS)")
                group3.setItemVisibilityChecked(False)
            group1 = root1.addGroup("ADDITIONAL DATA LAYERS")
            group1.setItemVisibilityChecked(True)
            group2 = root1.addGroup("SATELLITE IMAGERY")
            group2.setItemVisibilityChecked(True)

            civil_group = group1.addGroup("TRANSPORTATION & CIVIL INFRASTRUCTURE")
            civil_group.setItemVisibilityChecked(False)
            nat_res_group = group1.addGroup("NATURAL, HYDROLOGICAL, & GEOLOGICAL RESOURCES")
            nat_res_group.setItemVisibilityChecked(False)
            muni_group = group1.addGroup("MUNICIPAL BOUNDARIES")
            muni_group.setItemVisibilityChecked(False)
            haz_group = group1.addGroup("NATURAL HAZARDS")
            haz_group.setItemVisibilityChecked(False)
            env_group = group1.addGroup("CLIMATE DATA")
            env_group.setItemVisibilityChecked(True)
            temp_group = env_group.addGroup("TEMPERATURE")
            temp_group.setItemVisibilityChecked(False)
            prec_group = env_group.addGroup("PRECIPITATION")
            prec_group.setItemVisibilityChecked(False)

            # Google Earth goes in to the project
            url = "mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
            uri = "type=xyz&zmin=0&zmax=23&url=https://" + requests.utils.quote(url)
            goog_layer = QgsRasterLayer(uri, 'Google Satellite', 'wms')
            if not goog_layer.isValid():
                QgsMessageLog.logMessage(f"WARNING ------------------------------------------ LAYER FAILED TO LOAD")
                QgsMessageLog.logMessage("Error summary: ", goog_layer.error().summary())
                QgsMessageLog.logMessage("Detailed error message: ", goog_layer.error().message())
                QgsMessageLog.logMessage(goog_layer.error())
            else:
                project.addMapLayer(goog_layer, False)
                group2.insertChildNode(0, QgsLayerTreeLayer(goog_layer))
                project.layerTreeRoot().findLayer(goog_layer.id()).setExpanded(False)

            # Add background vector layers to project
            layer_info = [
                # Transportation & Civil Infrastructure
                (fire_hydrants_dst, "FIRE HYDRANT", uri_v29, civil_group),
                (fire_station_dst, "FIRE STATION", uri_v28, civil_group),
                (structures_dst, "STRUCTURE (KNOWN TO FEMA)", uri_v30, civil_group),
                (tiger_rds_cnty_dst, "US CENSUS BUREAU ROAD DATA-COUNTY CORRECTED", uri_v64, civil_group),
                (tiger_rds_dst, "US CENSUS BUREAU ROAD DATA", uri_v63, civil_group),
                (forest_srvc_rds_dst, "FOREST SERVICE ROADS", uri_v62, civil_group),
                (legacy_humco_cl_dst, "HUMBOLDT COUNTY LEGACY ROAD CENTERLINE DATA", uri_v61, civil_group),
                (rail_dst, "RAILWAYS", uri_v60, civil_group),
                (trail_dst, "HIKING TRAILS", uri_v59, civil_group),
                (airport_point_dst, "AIRPORTS", uri_v65, civil_group),
                (airport_rnwy_dst, "AIRPORT RUNWAYS", uri_v66, civil_group),
                (airport_comp_dst, "AIRPORT COMPATIBILITY ZONE", uri_v67, civil_group),

                # Natural, Hydrological, & Geological Resources
                (bio_res_dst, "BIOLOGICAL RESOURCE AREAS", uri_v13, nat_res_group),
                (invasive_dst, "KNOWN INVASIVE PLANT SPECIES", uri_v51, nat_res_group),
                (wetlands_dst, "MAPPED WETLANDS", uri_v48, nat_res_group),
                (millcreek_wetlands_dst, "MILL CREEK WETLANDS", uri_v48, nat_res_group),
                (timber_harvest_dst, "TIMBER HARVEST AREAS", uri_v58, nat_res_group),
                (woodland_dst, "WOODLAND LAND COVER", uri_v52, nat_res_group),
                (slope_30_dst, "AREAS GREATER THAN 30% SLOPE", uri_v56, nat_res_group),
                (slope_15_dst, "AREAS LESS THAN 15% SLOPE", uri_v55, nat_res_group),
                (faultline_dst, "EARTHQUAKE FAULT LINES", uri_v50, nat_res_group),
                (soils_dst, "SOIL TYPES (USE MUKEY TO FIND IN NRCS HYDRIC SOILS LIST)", uri_v57, nat_res_group),
                (bedrock_dst, "BEDROCK CLASSIFICATION", uri_v49, nat_res_group),

                # Municipal Boundaries
                (coastal_dst, "COASTAL ZONE", uri_v25, muni_group),
                (williamson_dst, "WILLIAMSON ACT LANDS", uri_v23, muni_group),
                (ag_lands_dst, "AGRICULTURAL LANDS", uri_v14, muni_group),
                (public_dst, "PUBLIC LANDS", uri_v22, muni_group),
                (city_dst, "CITY BOUNDARY", uri_v18, muni_group),
                (planning_dst, "COMMUNITY PLANNING AREAS", uri_v20, muni_group),
                (gplan_dst, "GENERAL PLAN LAND USE", uri_v24, muni_group),
                (service_dst, "COMMUNITY SERVICE DISTRICTS", uri_v21, muni_group),
                (fire_dst, "FIRE DISTRICT", uri_v24, muni_group),
                (zoning_dst, "HUMBOLDT COUNTY ZONING", uri_v19, muni_group),

                # Natural Hazards
                (fema_dst, "FLOOD ZONE", uri_v26, haz_group),
                (tsunami_dst, "TSUNAMI INUNDATION ZONE", uri_v53, haz_group),
                (slope_stab_bay, "SLOPE STABILITY (HUMBOLDT BAY)", uri_v16, haz_group),
                (slope_stab_dst, "SLOPE STABILITY (COUNTY)", uri_v17, haz_group),
                (alquist_pri_dst, "ALQUIST-PRIOLO ZONES", uri_v15, haz_group),
                (liquefaction_dst, "LIQUEFACTION AREAS", uri_v12, haz_group),
                (fire_risk_dst, "WILDLAND FIRE RISK", uri_v68, haz_group),

                # Climate data
                # Temperature
                (temp_min_dst, "MINIMUM TEMPERATURE ()", uri_v31, temp_group),
                (temp_max_dst, "MAXIMUM TEMPERATURE ()", uri_v32, temp_group),
                (mintemp_dst, "MINIMUM TEMPERATURE (1981-2010)", uri_v33, temp_group),
                (maxtemp_dst, "MAXIMUM TEMPERATURE (1981-2010)", uri_v34, temp_group),

                # Precipitation
                (precip_annual, "ANNUAL PRECIPITATION (1981-2010)", uri_v35, prec_group),
                (precip_jan, "MONTHLY PRECIPITATION: JANUARY (1981-2010)", uri_v35, prec_group),
                (precip_feb, "MONTHLY PRECIPITATION: FEBRUARY (1981-2010)", uri_v35, prec_group),
                (precip_mar, "MONTHLY PRECIPITATION: MARCH (1981-2010)", uri_v35, prec_group),
                (precip_apr, "MONTHLY PRECIPITATION: APRIL (1981-2010)", uri_v35, prec_group),
                (precip_may, "MONTHLY PRECIPITATION: MAY (1981-2010)", uri_v35, prec_group),
                (precip_jun, "MONTHLY PRECIPITATION: JUNE (1981-2010)", uri_v35, prec_group),
                (precip_jul, "MONTHLY PRECIPITATION: JULY (1981-2010)", uri_v35, prec_group),
                (precip_aug, "MONTHLY PRECIPITATION: AUGUST (1981-2010)", uri_v35, prec_group),
                (precip_sep, "MONTHLY PRECIPITATION: SEPTEMBER (1981-2010)", uri_v35, prec_group),
                (precip_oct, "MONTHLY PRECIPITATION: OCTOBER (1981-2010)", uri_v35, prec_group),
                (precip_nov, "MONTHLY PRECIPITATION: NOVEMBER (1981-2010)", uri_v35, prec_group),
                (precip_dec, "MONTHLY PRECIPITATION: DECEMBER (1981-2010)", uri_v35, prec_group),
            ]

            if road_choice:
                layer_info.extend([
                    (road_points_first, "ROAD POINTS WITH SLOPE LESS THAN 24", uri_v69, road_point_grp),
                    (road_points_second, "ROAD POINTS WITH SLOPE 24-32", uri_v70, road_point_grp),
                    (road_points_third, "ROAD POINTS WITH SLOPE 32-40", uri_v71, road_point_grp),
                    (road_points_fourth, "ROAD POINTS WITH SLOPE 40-45", uri_v72, road_point_grp),
                    (road_points_all, "ROAD POINTS WITH SLOPE LESS THAN 45", uri_v73, road_point_grp),
                    (road_points_first_exclude, "ROAD POINTS WITH SLOPE LESS THAN 24 (STREAM EXCLUDED)", uri_v69,
                     road_point_exclude_grp),
                    (road_points_second_exclude, "ROAD POINTS WITH SLOPE 24-32 (STREAM EXCLUDED)", uri_v70,
                     road_point_exclude_grp),
                    (road_points_third_exclude, "ROAD POINTS WITH SLOPE 32-40 (STREAM EXCLUDED)", uri_v71,
                     road_point_exclude_grp),
                    (road_points_fourth_exclude, "ROAD POINTS WITH SLOPE 40-45 (STREAM EXCLUDED)", uri_v72,
                     road_point_exclude_grp),
                    (road_points_all_exclude, "ROAD POINTS WITH SLOPE LESS THAN 45 (STREAM EXCLUDED)", uri_v73,
                     road_point_exclude_grp),
                ])

            parcels = QgsVectorLayer(parcel_src, "HumCo Parcels", "ogr")
            parcels.setCrs(crs)
            roads = QgsVectorLayer(road_src, "HumCo Roads", "ogr")
            roads.setCrs(crs)

            progress_window.set_progress(4)
            progress_window.show_message("Collecting parcel geospatial data and exporting")

            # Initialize variables
            merged_geometry = QgsGeometry()

            # Loop through APNs to select and merge geometries
            for apn in apn_list:
                expr = QgsExpression(f"\"APN_12\"='{str(apn)}'")
                request = QgsFeatureRequest(expr)
                features = parcels.getFeatures(request)

                for feature in features:
                    if merged_geometry.isEmpty():
                        merged_geometry = feature.geometry()
                    else:
                        merged_geometry = merged_geometry.combine(feature.geometry())
                parcels.selectByExpression(expr.expression(), QgsVectorLayer.AddToSelection)

            # Ensure the output CRS is EPSG:2225, export the selected parcel, add to project
            crs = QgsCoordinateReferenceSystem("EPSG:2225")
            _writer = QgsVectorFileWriter.writeAsVectorFormatV3(parcels, selected_dst,
                                                                QgsProject.instance().transformContext(), save_opt)
            self.selected_parcel = QgsVectorLayer(selected_dst, "PROJECT PARCEL", "ogr")
            del _writer

            progress_window.set_progress(5)

            # Create buffer zones based on merged geometry for project data extraction
            surrounding_parcel_buffer = 5000
            parcel_center = merged_geometry.centroid()
            selected_parcel_buffer = merged_geometry.buffer(buffer_parcels, 4)
            surrounding_buffer = merged_geometry.buffer(surrounding_parcel_buffer, 4)
            selected_parcel_vector_buffer = merged_geometry.buffer(buffer_radius, 4)
            dem_radius_buffer = merged_geometry.buffer(buffer_dem, 4)
            map_buffer = merged_geometry.buffer(50, 4)

            progress_window.set_progress(6)

            if not test_mode:
                raster_task = RasterExtraction(True, True, False, goog_layer, dem_radius_buffer,
                                               goog_geo_dst, goog_geo2225, naip_temp, naip_dst)
                QgsApplication.taskManager().addTask(raster_task)

            progress_window.show_message("Processing DEM data")

            progress_window.set_progress(10)

            if selected_site_data_status["Streams"]:
                # Get the DEM file path
                raster_file, stream_flags, input_epsg, dem1m, dem1m_layer_name, dem_layers = (
                    dem_raster_source(merged_geometry))

                # Assign the correct stream vector file path based on the DEM flags
                stream_vector = assign_stream_vector(stream_flags)

                if stream_vector:  # Ensure that a stream source has been assigned
                    streams = QgsVectorLayer(stream_vector, "DEM Synthesized Streams", "ogr")
                    streams.setCrs(crs)
                    streams_cnty = QgsVectorLayer(stream_src, "HumCo Streams", "ogr")
                    streams_cnty.setCrs(crs)
                else:
                    streams_cnty = QgsVectorLayer(stream_src, "HumCo Streams", "ogr")
                    streams_cnty.setCrs(crs)

            # Gather adjacent parcels and export to new shapefile, add to project
            selected_geometry_wkt = merged_geometry.asWkt()
            buffered_geometry = merged_geometry.buffer(75, 8)
            buffered_geometry_wkt = buffered_geometry.asWkt()
            parcels.selectByExpression(
                f"(touches($geometry, geom_from_wkt('{selected_geometry_wkt}')) OR "
                f"intersects($geometry, geom_from_wkt('{buffered_geometry_wkt}')))"
            )

            # Initialize a list to hold the IDs of features to deselect
            deselect_ids = []

            # Iterate through selected features to find those that match APNs in apn_list
            for feature in parcels.selectedFeatures():
                if feature['APN_12'] in apn_list:
                    deselect_ids.append(feature.id())

            progress_window.set_progress(12)

            # Deselect those features
            parcels.deselect(deselect_ids)

            if parcels.selectedFeatureCount() > 0:
                _writer = QgsVectorFileWriter.writeAsVectorFormatV3(parcels, adjacent_dst, QgsProject.instance().
                                                                    transformContext(), save_opt)
                self.adjacent_parcels = QgsVectorLayer(adjacent_dst, "ADJACENT PARCELS", "ogr")
                del _writer

            adjacent_apns = [feature['APN_12'] for feature in self.adjacent_parcels.getFeatures()]
            adjacent_apns_str = ",".join([f"'{apn}'" for apn in adjacent_apns])
            apn_list_str = ', '.join(str(apn) for apn in apn_list)

            max_iterations = 10  # Prevent infinite loop by setting a maximum number of iterations
            iterations = 0

            self.surrounding_parcels = None

            # Loop until features are selected or the max_iterations is reached
            while iterations < max_iterations:
                # Perform the selection by expression
                parcels.selectByExpression(
                    f"intersects($geometry, buffer(geom_from_wkt('{selected_parcel_buffer.asWkt()}'), {selected_parcel_buffer})) "
                    f"AND NOT touches($geometry, geom_from_wkt('{merged_geometry.asWkt()}')) "
                    f"AND \"APN_12\" != '{apn_list_str}' AND \"APN_12\" NOT IN ({adjacent_apns_str})"
                )

                # Check if any features were selected
                if parcels.selectedFeatureCount() > 0:
                    break  # Exit loop if features are selected
                else:
                    # Increase the buffer size by 1000 units if no features were selected
                    surrounding_parcel_buffer += 1000
                    iterations += 1

                    selected_parcel_buffer = merged_geometry.buffer(buffer_parcels, 4)

            if parcels.selectedFeatureCount() > 0:
                _writer = QgsVectorFileWriter.writeAsVectorFormatV3(parcels, surrounding_dst, QgsProject.instance().
                                                                    transformContext(), save_opt)
                self.surrounding_parcels = QgsVectorLayer(surrounding_dst, "SURROUNDING PARCELS", "ogr")
                del _writer

            buffer_polygon = selected_parcel_vector_buffer.buffer(buffer_radius, 6)

            progress_window.set_progress(18)
            if not sip.isdeleted(progress_window):
                progress_window.show_message("Exporting roads and streams")

            # Create the buffer polygon layer and add features
            buffer_polygon_layer = QgsVectorLayer("Polygon?crs=epsg:2225", "Buffer", "memory")
            features = [QgsFeature() for _ in range(1)]  # Create an empty QgsFeature list
            features[0].setGeometry(buffer_polygon)  # Set the geometry for the first feature
            buffer_polygon_layer.dataProvider().addFeatures(features)
            ogr.UseExceptions()

            progress_window.set_progress(24)

            MESSAGE_CATEGORY = 'Road Export'

            # Clip the roads layer using the buffer polygon
            def roads_finished(context, successful, results):
                if not successful:
                    QgsMessageLog.logMessage('Road export task was unsuccessful!',
                                             MESSAGE_CATEGORY, Qgis.Warning)
                output_layer = context.getMapLayer(results['OUTPUT'])
                if output_layer and output_layer.isValid():
                    QgsMessageLog.logMessage('Road export task finished successfully!',
                                             MESSAGE_CATEGORY, Qgis.Info)

            alg_roads = QgsApplication.processingRegistry().algorithmById("qgis:clip")
            context_roads = QgsProcessingContext()
            feedback_roads = QgsProcessingFeedback()
            clip_params = {
                'INPUT': roads,
                'OVERLAY': buffer_polygon_layer,
                'OUTPUT': road_dst,
            }
            road_task = QgsProcessingAlgRunnerTask(alg_roads, clip_params, context_roads, feedback_roads)
            road_task.executed.connect(partial(roads_finished, context_roads))
            # task_manager.add_task(road_task)
            QgsApplication.taskManager().addTask(road_task)

            progress_window.set_progress(28)

            MESSAGE_CATEGORY = 'Stream Export'

            # Define the parameters and run the clipping operation for county streams
            def cnty_streams_finished(context, successful, results):
                if not successful:
                    QgsMessageLog.logMessage('County streams export task was unsuccessful!',
                                             MESSAGE_CATEGORY, Qgis.Warning)
                output_layer = context.getMapLayer(results['OUTPUT'])
                if output_layer and output_layer.isValid():
                    QgsMessageLog.logMessage('County streams export task finished successfully!',
                                             MESSAGE_CATEGORY, Qgis.Info)

            alg_streams_cnty = QgsApplication.processingRegistry().algorithmById("qgis:clip")
            context_streams_cnty = QgsProcessingContext()
            feedback_streams_cnty = QgsProcessingFeedback()
            clip_params_cnty = {
                'INPUT': streams_cnty,
                'OVERLAY': buffer_polygon_layer,
                'OUTPUT': streams_cnty_dst,
            }
            cnty_streams_task = QgsProcessingAlgRunnerTask(
                alg_streams_cnty, clip_params_cnty, context_streams_cnty, feedback_streams_cnty)
            cnty_streams_task.executed.connect(partial(cnty_streams_finished, context_streams_cnty))
            # task_manager.add_task(cnty_streams_task)
            QgsApplication.taskManager().addTask(cnty_streams_task)

            progress_window.set_progress(32)

            # If there's a DEM-specific streams layer, clip it as well
            self.dem_streams_proj = None
            if stream_vector:
                def dem_streams_finished(context, successful, results):
                    if not successful:
                        QgsMessageLog.logMessage('DEM based streams export task was unsuccessful!',
                                                 MESSAGE_CATEGORY, Qgis.Warning)
                        return  # Exit if the task was not successful

                    # Use the get method to avoid KeyError if 'OUTPUT' is not present
                    output_layer = context.getMapLayer(results.get('OUTPUT'))
                    if output_layer is None and os.path.exists(streams_dst):
                        QgsMessageLog.logMessage('No stream output layer found after running the algorithm.',
                                                 MESSAGE_CATEGORY, Qgis.Critical)
                        return  # Exit if there's no output layer

                    if output_layer.isValid() or os.path.exists(streams_dst):
                        QgsMessageLog.logMessage('DEM based streams export task finished successfully!',
                                                 MESSAGE_CATEGORY, Qgis.Info)
                    else:
                        QgsMessageLog.logMessage('Output layer is not valid.',
                                                 MESSAGE_CATEGORY, Qgis.Critical)

                alg_streams_dem = QgsApplication.processingRegistry().algorithmById("qgis:clip")
                context_streams_dem = QgsProcessingContext()
                feedback_streams_dem = QgsProcessingFeedback()
                clip_params_dem = {
                    'INPUT': streams,
                    'OVERLAY': buffer_polygon_layer,
                    'OUTPUT': streams_dst,
                }
                dem_streams_task = QgsProcessingAlgRunnerTask(
                    alg_streams_dem, clip_params_dem, context_streams_dem, feedback_streams_dem)
                dem_streams_task.executed.connect(partial(dem_streams_finished, context_streams_dem))
                QgsApplication.taskManager().addTask(dem_streams_task)

            progress_window.set_progress(36)

            QgsProject.instance().removeMapLayer(parcels.id())
            QgsProject.instance().removeMapLayer(roads.id())
            QgsProject.instance().removeMapLayer(streams_cnty.id())
            if dem1m: QgsProject.instance().removeMapLayer(streams.id())

            if not sip.isdeleted(progress_window):
                progress_window.set_progress(42)

            # Get the list of selected background shapefiles
            # Filter the selected files
            selected_file_list = [(name, src, dst) for name, src, dst in file_list if selected_files_status.get(name)]

            if not sip.isdeleted(progress_window):
                progress_window.set_progress(46)
            if not sip.isdeleted(progress_window):
                progress_window.show_message("Processing background data layers")

            parcel_selector = selected_parcel_buffer.asWkt()

            contexts = []
            feedbacks = []

            for layer_name, src_filename, dst_filename in selected_file_list:
                src_file = f'{source_shp}{layer_name}/{src_filename}'
                dst_file = dst_filename

                params = {
                    'INPUT': src_file,
                    'OVERLAY': buffer_polygon_layer,
                    'OUTPUT': dst_file
                }

                # Create a unique context and feedback for each task
                context = QgsProcessingContext()
                feedback = QgsProcessingFeedback()

                # Append the context and feedback to the lists to keep references
                contexts.append(context)
                feedbacks.append(feedback)

                alg = QgsApplication.processingRegistry().algorithmById('qgis:clip')
                if alg is None:
                    QgsMessageLog.logMessage("Clip algorithm not found", Qgis.Critical)
                    continue

                bckgrnd_layer_task = QgsProcessingAlgRunnerTask(alg, params, contexts[-1], feedbacks[-1])
                QgsApplication.taskManager().addTask(bckgrnd_layer_task)

            layer_list = []

            if selected_raster_status["Digital Elevation Model Raster"] and selected_raster_status["Slope Raster"]:
                dem_processing_task = SlopeExtractor(
                    dem1m,  # Boolean flag indicating whether to use the 1m DEM or the 10m DEM
                    raster_file,  # The path to the raster file
                    slope_per,  # The path to the output slope percent file
                    slope_deg,  # The path to the output slope degree file
                    percent_style,  # The named style to load for the slope percent raster
                    group2,  # The layer tree group to insert the layers into
                    dem1m_layer_name,  # The name of the DEM layer in the project
                    destination_dem,  # The path to the output DEM file
                    hillshade_dst  # The path to the output hillshade file
                )
                dem_processing_task.addSubTask(dem_task_1, [], QgsTask.ParentDependsOnSubTask)
                QgsApplication.taskManager().addTask(dem_processing_task)

            # if not test_mode and not raster_task_finished:
                # if raster_task.isActive(): raster_task.waitForFinished(160000)

            if not sip.isdeleted(progress_window): progress_window.set_progress(55)
            if not sip.isdeleted(progress_window): progress_window.show_message("Adding exported shapefile data to project")

            if not test_mode:
                raster_task.waitForFinished(60000)
            if selected_raster_status["Digital Elevation Model Raster"] and selected_site_data_status["Site Contours"]:
                contour_task.waitForFinished(60000)
            if selected_site_data_status["Road Centerlines"]:
                # if road_task.isActive(): road_task.waitForFinished(160000)
                road_task.waitForFinished(160000)
            if selected_site_data_status["Streams"]:
                # if cnty_streams_task.isActive(): cnty_streams_task.waitForFinished(160000)
                cnty_streams_task.waitForFinished(160000)
            if selected_files_status:
                # if bckgrnd_layer_task.isActive(): bckgrnd_layer_task.waitForFinished(160000)
                bckgrnd_layer_task.waitForFinished(160000)
            if selected_raster_status["Digital Elevation Model Raster"] and selected_raster_status["Slope Raster"]:
                # if dem_processing_task.isActive(): dem_processing_task.waitForFinished(160000)
                dem_processing_task.waitForFinished(160000)
            if stream_vector:
                # if dem_streams_task.isActive(): dem_streams_task.waitForFinished(160000)
                dem_streams_task.waitForFinished(160000)
                if road_choice:
                    check_folder_create(road_finder_path)
                    road_point_task = RoadFinder(
                        slope_deg,  # The path to the slope raster
                        road_finder_path,  # The path to the road finder final destination
                        streams_dst,  # The path to the streams
                        road_points_all_exclude,  # The path to the road file as a string
                        proj_num
                    )
                    QgsApplication.taskManager().addTask(road_point_task)
                    road_point_task.waitForFinished(240000)
            else:
                if road_choice:
                    check_folder_create(road_finder_path)
                    road_point_task = RoadFinder(
                        slope_deg,  # The path to the slope raster
                        road_finder_path,  # The path to the road finder final destination
                        streams_cnty_dst,  # The path to the streams
                        road_points_all_exclude,  # The path to the road file as a string
                        proj_num
                    )
                    QgsApplication.taskManager().addTask(road_point_task)
                    road_point_task.waitForFinished(240000)

            # if map_choice and not test_mode and all(selected_site_data_status):
            #     map_task = MapCreator(project, map_dst, goog_layer, self.selected_parcel)
            #     QgsApplication.taskManager().addTask(map_task)

            if not sip.isdeleted(progress_window):
                progress_window.set_progress(69)

            # Create the map PNG image for use in projects
            if map_choice and not test_mode and all(selected_site_data_status):
                manager = project.layoutManager()
                layout_name = 'Overview Map'
                layouts_list = manager.printLayouts()

                # remove any duplicate layouts
                for layout in layouts_list:
                    if layout.name() == layout_name: manager.removeLayout(layout)

                layout = QgsPrintLayout(project)
                layout.initializeDefaults()
                layout.setName(layout_name)
                manager.addLayout(layout)

                # Get reference to Google Satellite layer and Project Parcel
                google_layer = QgsProject.instance().mapLayersByName('Google Satellite')[0]
                project_parcel_layer = self.selected_parcel
                adjacent_parcels_layer = self.adjacent_parcels
                surrounding_parcels_layer = self.surrounding_parcels
                road_centerline_layer = self.road_centerline
                streams_layer = self.streams
                contour_20ft_layer = self.contour_20ft
                contour_100ft_layer = self.contour_100ft

                # Define the layers for the legend
                legend_layers = ["PROJECT PARCEL", "ADJACENT PARCELS", "SURROUNDING PARCELS", "ROAD CENTERLINE",
                                 "STREAMS", "CONTOURS-20FT", "CONTOURS-100FT"]

                # Get other layers by their names
                other_layers = []
                for layer_name in legend_layers:
                    layer_list = QgsProject.instance().mapLayersByName(layer_name)
                    if layer_list:
                        other_layers.append(layer_list[0])
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
                map.setLayers(other_layers + [google_layer])
                map.setRect(0, 0, page_size.width(), page_size.height())

                # Get the bounding box of the feature
                bbox = project_parcel_layer.extent()

                # Width and height of the bounding box in feet
                bbox_width_ft = bbox.width()  # EPSG:2225
                bbox_height_ft = bbox.height()  # EPSG:2225
                if test_file:
                    if not sip.isdeleted(progress_window):
                        progress_window.show_message(f"bounding box width = {bbox_width_ft}")
                if test_file:
                    if not sip.isdeleted(progress_window):
                        progress_window.show_message(f"bounding box height = {bbox_height_ft}")

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
                    if not sip.isdeleted(progress_window):
                        progress_window.set_progress(75)

                    if map_max_width_ft > bbox_width_ft and map_max_height_ft > bbox_height_ft:
                        # Calculate the centroid of the project parcel layer for map extent placement
                        features = project_parcel_layer.getFeatures()
                        geometry_union = QgsGeometry().unaryUnion([feature.geometry() for feature in features])
                        bbox = geometry_union.boundingBox()
                        center_point = bbox.center()

                        # Grab the scale number
                        fin_scale = scales[element + 1]
                        if not sip.isdeleted(progress_window):
                            progress_window.show_message(f"Map scale is 1 in. = {fin_scale} ft.")

                        # Get the size of the map item in layout units
                        map_size = map.rect().size()
                        map_width = map_size.width()
                        map_height = map_size.height()
                        if test_file:
                            if not sip.isdeleted(progress_window):
                                progress_window.show_message(f"map center is {center_point.x()}, {center_point.y()}")

                        map_render_height = map_height_inches * fin_scale
                        map_render_width = map_width_inches * fin_scale

                        # Get the coordinates for map size
                        west_x = center_point.x() - map_render_width / 2
                        south_y = center_point.y() - map_render_height / 2
                        east_x = center_point.x() + map_render_width / 2
                        north_y = center_point.y() + map_render_height / 2

                        if test_file:
                            if not sip.isdeleted(progress_window):
                                progress_window.show_message(f"map corners are {west_x}, {south_y}, {east_x}, {north_y}")

                        # Calculate the new extent based on the center point and the size of the map
                        new_extent = QgsRectangle(west_x, south_y, east_x, north_y)
                        layout.addLayoutItem(map)

                        # Set map extent and scale
                        map.setExtent(new_extent)

                        conversion_factor = map.mapUnitsToLayoutUnits()
                        if test_file:
                            if not sip.isdeleted(progress_window):
                                progress_window.show_message(f"conversion factor is {conversion_factor}")
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

                        if not sip.isdeleted(progress_window):
                            progress_window.set_progress(86)

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
                        if test_file:
                            if not sip.isdeleted(progress_window):
                                progress_window.show_message(f"element = {element}")
                        continue

                # Create legend
                legend = QgsLayoutItemLegend(layout)
                legend.setTitle("LEGEND")
                layout.addLayoutItem(legend)
                legend.setAutoUpdateModel(False)
                legend.model().rootGroup().clear()

                # Add the layers and add to map
                for layer in other_layers: legend.model().rootGroup().addLayer(layer)
                legend.setLinkedMap(map)
                legend.setItemOpacity(0.55)
                legend.refresh()

                layout = manager.layoutByName(layout_name)
                exporter = QgsLayoutExporter(layout)

                settings = QgsLayoutExporter.ImageExportSettings()
                settings.dpi = 150

                exporter.exportToImage(map_dst, settings)

            # Make the DXF file for the project
            if dxf_choice:
                # Copy the original DWG to a new location
                original_pl = f'{source_dwg}XXXX_PL.dxf'
                copy_dwg_pl = f'{destination_dxf}{proj_num}_PL-temp.dxf'
                shutil.copy2(original_pl, copy_dwg_pl)

                original_topo = f'{source_dwg}XXXX_TOPO-E.dxf'
                copy_dwg_topo = f'{destination_dxf}{proj_num}_TOPO-temp.dxf'
                shutil.copy2(original_topo, copy_dwg_topo)

                # Convert the copy to DXF
                dxf_pl = f'{destination_dxf}{proj_num}_PL-QGIS CREATED.dxf'
                doc_pl = ezdxf.readfile(copy_dwg_pl)
                doc_pl.saveas(dxf_pl)
                os.remove(copy_dwg_pl)

                dxf_topo = f'{destination_dxf}{proj_num}_TOPO-QGIS CREATED.dxf'
                doc_topo = ezdxf.readfile(copy_dwg_topo)
                doc_topo.saveas(dxf_topo)
                os.remove(copy_dwg_topo)

                # Get the project instance
                project = QgsProject.instance()

                # Lists of layer names
                pl_layer_qgis = ["SURROUNDING PARCELS", "ADJACENT PARCELS", "PROJECT PARCEL"]
                pl_layer_dxf = ["SURROUNDING", "ADJACENT", "BOUNDARY"]

                topo_layer_qgis = ["CONTOURS-100FT", "CONTOURS-40FT", "CONTOURS-20FT", "CONTOURS-10FT", "CONTOURS-2FT",
                                   "STREAMS", "ROAD CENTERLINE"]

                # Process pl_layer_qgis and pl_layer_dxf
                for i, layer_name in enumerate(pl_layer_qgis):
                    source_layer = project.mapLayersByName(layer_name)[0]
                    if not source_layer:
                        QgsMessageLog.logMessage(f'Source layer with name {layer_name} not found in the project!')
                        continue

                    target_layer = QgsVectorLayer(f"{dxf_pl}|layername={pl_layer_dxf[i]}", f"target_{layer_name}",
                                                  "ogr")
                    if not target_layer.isValid():
                        QgsMessageLog.logMessage(f'Target layer with name {layer_name} failed to load!')
                        continue

                    target_layer.startEditing()
                    for feature in source_layer.getFeatures():
                        new_feature = QgsFeature(target_layer.fields())
                        new_feature.setAttributes(feature.attributes())
                        new_feature.setGeometry(feature.geometry())
                        target_layer.addFeature(new_feature)
                    target_layer.commitChanges()

                if not sip.isdeleted(progress_window):
                    progress_window.set_progress(96)
                if not sip.isdeleted(progress_window):
                    progress_window.show_message("Creating DXF files for PL and TOPO-E")

                # Export to PL
                # pl_color = QColor.fromRgb(255, 0, 0)  # red
                pl_color = QColor('red')
                # adj_color = QColor.fromRgb(0, 255, 127)  # springgreen
                adj_color = QColor('springgreen')
                # surr_color = QColor.fromRgb(255, 255, 255)  # white
                surr_color = QColor('white')

                pl_path = f'{destination_dxf}{proj_num}_PL-CREATED BY QGIS.dxf'
                layer_settings = [
                    {
                        'name': 'SURROUNDING PARCELS',
                        # 'color': '0, 0, 0',
                        'color': 255,
                        'penwidth': 0.0,
                        'linetype': 'CONTINUOUS'
                    },
                    {
                        'name': 'ADJACENT PARCELS',
                        # 'color': '0, 255, 127',
                        'color': 110,
                        'penwidth': 0.0,
                        'linetype': 'CONTINUOUS'
                    },
                    {
                        'name': 'PROJECT PARCEL',
                        # 'color': '255, 0, 0',
                        'color': 1,
                        'penwidth': 0.0,
                        'linetype': 'CONTINUOUS'
                    },
                ]
                # export_layers_to_dxf(layer_settings, pl_path)

                # Export to TOPO-E
                road_color = QColor('magenta')
                topo_path = f'{destination_dxf}{proj_num}_TOPO-E-CREATED BY QGIS.dxf'
                layer_settings = [
                    {
                        'name': 'CONTOURS-100FT',
                        # 'color': '128, 128, 128',
                        'color': 8,
                        'penwidth': 0.0,
                        'linetype': 'DASHED'
                    },
                    {
                        'name': 'CONTOURS-40FT',
                        # 'color': '128, 128, 128',
                        'color': 9,
                        'penwidth': 0.0,
                        'linetype': 'DASHED'
                    },
                    {
                        'name': 'CONTOURS-20FT',
                        # 'color': '192, 192, 192',
                        'color': 252,
                        'penwidth': 0.0,
                        'linetype': 'DASHED'
                    },
                    {
                        'name': 'CONTOURS-10FT',
                        # 'color': '192, 192, 192',
                        'color': 252,
                        'penwidth': 0.0,
                        'linetype': 'DASHED'
                    },
                    {
                        'name': 'CONTOURS-2FT',
                        # 'color': '192, 192, 192',
                        'color': 252,
                        'penwidth': 0.0,
                        'linetype': 'DASHED2'
                    },
                    {
                        'name': 'STREAMS',
                        # 'color': '0, 0, 255',
                        'color': 4,
                        'penwidth': 0.0,
                        'linetype': 'CONTINUOUS'
                    },
                    {
                        'name': 'ROAD CENTERLINE',
                        # 'color': road_color,
                        'color': 6,
                        'penwidth': 0.0,
                        'linetype': 'CONTINUOUS'
                    },
                ]
                # export_layers_to_dxf(layer_settings, topo_path)

            for path, name, style, group in layer_info:
                if os.path.exists(path):
                    layer = QgsVectorLayer(path, name, "ogr")
                    if layer.featureCount() > 0:
                        # Load the new shapefile
                        layer.setCrs(crs)
                        layer.loadNamedStyle(style)
                        layer.triggerRepaint()
                        project.addMapLayer(layer, False)
                        layer_list.append(layer)
                        group.addLayer(layer)

            if os.path.exists(streams_dst):
                self.dem_streams_proj = QgsVectorLayer(streams_dst, "DEM STREAMS", "ogr")
                self.dem_streams_proj.setCrs(crs)
                self.dem_streams_proj.loadNamedStyle(uri_v1)
                self.dem_streams_proj.triggerRepaint()
            if os.path.exists(streams_cnty_dst):
                self.county_streams_proj = QgsVectorLayer(streams_cnty_dst, "COUNTY STREAMS", "ogr")
                self.county_streams_proj.setCrs(crs)
                self.county_streams_proj.loadNamedStyle(uri_v1)
                self.county_streams_proj.triggerRepaint()
            if os.path.exists(road_dst):
                self.roads_proj = QgsVectorLayer(road_dst, "ROAD CENTERLINE", "ogr")
                self.roads_proj.setCrs(crs)
                self.roads_proj.loadNamedStyle(uri_v2)
                self.roads_proj.triggerRepaint()
            if os.path.exists(surrounding_dst):
                self.surrounding_parcels.setCrs(crs)
                self.surrounding_parcels.loadNamedStyle(uri_v4)
                self.surrounding_parcels.triggerRepaint()
            if os.path.exists(adjacent_dst):
                self.adjacent_parcels.setCrs(crs)
                self.adjacent_parcels.loadNamedStyle(uri_v5)
                self.adjacent_parcels.triggerRepaint()
            if os.path.exists(selected_dst):
                self.selected_parcel.setCrs(crs)
                self.selected_parcel.loadNamedStyle(uri_v6)
                self.selected_parcel.triggerRepaint()
            if os.path.exists(goog_geo2225):
                rlayer2 = QgsRasterLayer(goog_geo2225, "Parcel Overview-GOOG")
                if not rlayer2.isValid():
                    QgsMessageLog.logMessage(
                        f"Failed to load {goog_geo2225}. Is the path correct? Is the format supported?")
                else:
                    # Set the CRS for the raster layer if needed
                    rlayer2.setCrs(QgsCoordinateReferenceSystem(crs))
                    rlayer2.triggerRepaint()
                    project.addMapLayer(rlayer2, False)
                    group2.insertChildNode(1, QgsLayerTreeLayer(rlayer2))
                    project.layerTreeRoot().findLayer(rlayer2.id()).setExpanded(False)
            if os.path.exists(naip_dst):
                naip_final_layer = QgsRasterLayer(naip_dst, "NAIP Imagery-Parcel Overview")
                if not naip_final_layer.isValid():
                    QgsMessageLog.logMessage(
                        f"Failed to load {naip_dst}. Is the path correct? Is the format supported?")
                else:
                    # Set the CRS for the raster layer if needed
                    naip_final_layer.setCrs(QgsCoordinateReferenceSystem(crs))
                    naip_final_layer.triggerRepaint()
                    project.addMapLayer(naip_final_layer, False)
                    group2.insertChildNode(2, QgsLayerTreeLayer(naip_final_layer))
                    project.layerTreeRoot().findLayer(naip_final_layer.id()).setExpanded(False)
            if dem1m:
                r_layer1 = QgsRasterLayer(raster_file, dem1m_layer_name)
                if r_layer1.isValid():
                    r_layer1.triggerRepaint()
                    project.addMapLayer(r_layer1, False)
                    group2.insertChildNode(3, QgsLayerTreeLayer(r_layer1))
                    project.layerTreeRoot().findLayer(r_layer1.id()).setExpanded(False)

                    rlayer4 = QgsRasterLayer(slope_deg, "SLOPE (DEGREE)")
                    if rlayer4.isValid():
                        rlayer4.triggerRepaint()
                        project.addMapLayer(rlayer4, False)
                        group2.insertChildNode(4, QgsLayerTreeLayer(rlayer4))
                        project.layerTreeRoot().findLayer(rlayer4.id()).setExpanded(False)

                    rlayer5 = QgsRasterLayer(slope_per, "SLOPE (PERCENT)")
                    if rlayer5.isValid():
                        rlayer5.triggerRepaint()
                        project.addMapLayer(rlayer5, False)
                        group2.insertChildNode(5, QgsLayerTreeLayer(rlayer5))
                        project.layerTreeRoot().findLayer(rlayer5.id()).setExpanded(False)
                        rlayer5.loadNamedStyle(percent_style)

                    rlayer6 = QgsRasterLayer(hillshade_dst, "HILLSHADE")
                    if rlayer6.isValid():
                        rlayer6.triggerRepaint()
                        project.addMapLayer(rlayer6, False)
                        group2.insertChildNode(6, QgsLayerTreeLayer(rlayer6))
                        project.layerTreeRoot().findLayer(rlayer6.id()).setExpanded(False)

                    rlayer7 = QgsRasterLayer(flow_accumulation_dst, "FLOW ACCUMULATION")
                    if rlayer7.isValid():
                        rlayer7.triggerRepaint()
                        project.addMapLayer(rlayer7, False)
                        group2.insertChildNode(7, QgsLayerTreeLayer(rlayer7))
                        project.layerTreeRoot().findLayer(rlayer7.id()).setExpanded(False)
            else:
                r_layer1 = QgsRasterLayer(destination_dem, "10M HUM_CO USGS DEM (1/3 ARC-SECOND)")
                if r_layer1.isValid():
                    r_layer1.triggerRepaint()
                    project.addMapLayer(r_layer1, False)
                    group2.insertChildNode(3, QgsLayerTreeLayer(r_layer1))
                    project.layerTreeRoot().findLayer(r_layer1.id()).setExpanded(False)


            if os.path.exists(naip_temp):
                try:
                    os.remove(naip_temp)
                    QgsMessageLog.logMessage(f"File {naip_temp} deleted successfully.")
                except OSError as e:
                    QgsMessageLog.logMessage(
                        f"Error deleting file {naip_temp}: {e.strerror}. File may be in use or permissions issue.")
            if self.dem_streams_proj is not None:
                if self.dem_streams_proj.isValid() and selected_site_data_status["Streams"]:
                    if self.dem_streams_proj.featureCount() > 0:
                        project.addMapLayer(self.dem_streams_proj)
            if self.county_streams_proj.isValid() and selected_site_data_status["Streams"]:
                if self.county_streams_proj.featureCount() > 0:
                    project.addMapLayer(self.county_streams_proj)
            if self.roads_proj.isValid() and selected_site_data_status["Road Centerlines"]:
                if self.roads_proj.featureCount() > 0:
                    project.addMapLayer(self.roads_proj)
            if self.surrounding_parcels is not None:
                if self.surrounding_parcels.isValid() and selected_site_data_status["Surrounding Parcels"]:
                    if self.surrounding_parcels.featureCount() > 0:
                        project.addMapLayer(self.surrounding_parcels)
            if self.adjacent_parcels.isValid() and selected_site_data_status["Adjacent Parcels"]:
                if self.adjacent_parcels.featureCount() > 0:
                    project.addMapLayer(self.adjacent_parcels)

            project.addMapLayer(self.selected_parcel)

            # Contour time

            intervals = [2, 10, 20, 40, 100, 200]
            contour_files = [
                f"{destination_shp}{proj_num}_CONTOURS_{interval}ft-{output_epsg}.shp" for interval in
                intervals
            ]
            contour_names = [f"CONTOURS-{interval}FT" for interval in intervals]

            contour_1 = f"{destination_shp}{proj_num}_CONTOURS_2ft-2225.shp"
            contour_2 = f"{destination_shp}{proj_num}_CONTOURS_10ft-2225.shp"
            contour_3 = f"{destination_shp}{proj_num}_CONTOURS_20ft-2225.shp"
            contour_4 = f"{destination_shp}{proj_num}_CONTOURS_40ft-2225.shp"
            contour_5 = f"{destination_shp}{proj_num}_CONTOURS_100ft-2225.shp"
            contour_6 = f"{destination_shp}{proj_num}_CONTOURS_200ft-2225.shp"

            contour_files = [
                (contour_1, "CONTOURS-2FT", uri_v7),
                (contour_2, "CONTOURS-10FT", uri_v8),
                (contour_3, "CONTOURS-20FT", uri_v9),
                (contour_4, "CONTOURS-40FT", uri_v10),
                (contour_5, "CONTOURS-100FT", uri_v11),
                (contour_6, "CONTOURS-200FT", uri_v11),
            ]
            index = 0
            contour_layers = []

            # Add contour layers to the project
            for contour_file, contour_name, style in contour_files:
                if os.path.exists(contour_file): contour_layers.append((contour_file, contour_name, style))

            for file_path, name, style in contour_layers:
                layer = QgsVectorLayer(file_path, name, "ogr")
                if layer.isValid():
                    index = index + 1
                    project.addMapLayer(layer, False)
                    layer.loadNamedStyle(style, True)
                    group3.insertChildNode(index, QgsLayerTreeLayer(layer))

            def zoom_to_layer():
                global mem_layer
                for filename in os.listdir(destination_shp):
                    if filename.startswith(f'{proj_num}_PROJECT PARCEL') \
                            and not selected_site_data_status["Project Parcel"]:
                        os.remove(os.path.join(destination_shp, filename))
                    if filename.startswith(f'{proj_num}_ADJACENT') \
                            and not selected_site_data_status["Adjacent Parcels"]:
                        os.remove(os.path.join(destination_shp, filename))
                    if filename.startswith(f'{proj_num}_SURROUNDING') \
                            and not selected_site_data_status["Surrounding Parcels"]:
                        os.remove(os.path.join(destination_shp, filename))
                    if filename.startswith(f'{proj_num}_STREAMS') \
                            and not selected_site_data_status["Streams"]:
                        os.remove(os.path.join(destination_shp, filename))
                    if filename.startswith(f'{proj_num}_ROAD') \
                            and not selected_site_data_status["Road Centerlines"]:
                        os.remove(os.path.join(destination_shp, filename))
                    if filename.startswith(f'{proj_num}_CONTOURS') \
                            and not selected_site_data_status["Site Contours"]:
                        os.remove(os.path.join(destination_shp, filename))
                for dirpath, dirnames, filenames in os.walk('your_directory'):
                    for filename in filenames:
                        if 'temp.' in filename:
                            try:
                                os.remove(os.path.join(dirpath, filename))
                            except PermissionError as e:
                                QgsMessageLog.logMessage(f"Error: {e}. File {filename} may be in use.")

                # Create a buffer to focus the map canvas
                mem_layer = QgsVectorLayer("Polygon?crs=epsg:2225", "temp_buffer", "memory")
                provider = mem_layer.dataProvider()
                provider.addAttributes([QgsField("id", QVariant.Int)])
                mem_layer.updateFields()
                for feature in self.adjacent_parcels.getFeatures():
                    new_feature = QgsFeature()
                    geom = feature.geometry()
                    buffer_geom = geom.buffer(0.001, 5)

                    new_feature.setGeometry(buffer_geom)
                    new_feature.setAttributes([feature.id()])
                    provider.addFeatures([new_feature])

                project.addMapLayer(mem_layer, False)

                # Check if the object still exists before accessing it
                if mem_layer and not sip.isdeleted(mem_layer):
                    iface.mapCanvas().setExtent(mem_layer.extent())
                    iface.mapCanvas().refresh()

                    # Make sure to disconnect the signal only if it's connected and the object is valid
                    iface.mapCanvas().renderComplete.disconnect(zoom_to_layer)
                    if mem_layer:  # Check again to be extra sure
                        project.removeMapLayer(mem_layer.id())
                        mem_layer = None  # Clear the reference

            iface.mapCanvas().renderComplete.connect(zoom_to_layer)

            # Remove temporary map layers
            if project.mapLayer(buffer_polygon_layer.id()):
                project.removeMapLayer(buffer_polygon_layer.id())

            if not sip.isdeleted(progress_window):
                progress_window.set_progress(98)
            if not sip.isdeleted(progress_window):
                progress_window.show_message("Adding remaining layers and saving project file to disk")

            project_file = f"{destination_gis}{proj_name}_PROJECT MASTER.qgz"

            # handler.close()
            logger.removeHandler(handler)

            # save_status = project.write(project_file)
            save_status = True
            project.write(project_file)

            if not save_status:
                QgsMessageLog.logMessage(f"Error saving project to {project_file}", 'MyPlugin', qgis.Critical)

            if not sip.isdeleted(progress_window):
                progress_window.set_progress(99)
            if not sip.isdeleted(progress_window):
                progress_window.show_message("Project creation complete")
            if os.path.exists(naip_dst):
                if naip_final_layer:
                    check_layers(naip_final_layer)
            if os.path.exists(goog_geo2225):
                if rlayer2:
                    check_layers(rlayer2)

            if not sip.isdeleted(progress_window):
                progress_window.close()
            # final_dialog_instance.show_final(prj_folder)
            final_dialog_instance.showFinalSignal.emit(prj_folder)

            # position_x, position_y = where_qgis()

            return {project_file}

        global file_path_loc
        output_dst = None
        prop_path_loc = None
        if not proj_test:
            if not home_test: output_dst = "O:/"
            if home_test: output_dst = "D:/Destination/"
        else:
            if not home_test: output_dst = "P:/_Information/_TEST PROJECTS/"
            if home_test: output_dst = "D:/Destination/"
        contract_path_loc = f'{output_dst}Projects_Civil3D/'
        if not home_test: prop_path_loc = f'P:/_Proposals/{str(today.year)}/'
        if home_test: prop_path_loc = f'D:/Destination/_Proposals/{str(today.year)}'

        if not proj_type:
            file_path_loc = f'{contract_path_loc}{str(today.year)[-2:]}-'
        else:
            file_path_loc = prop_path_loc
        prj_folder = f"{file_path_loc}{proj_num}_{proj_name}/"

        def check_layers(layer):
            # Get the current project instance
            project = QgsProject.instance()

            # Check if the layer is valid
            if not layer.isValid():
                QgsMessageLog.logMessage(f"The layer {layer.name()} is not valid and cannot be added to the project.")
                return

            # Check if the layer with the specified ID is already in the project
            if layer.id() not in project.mapLayers():
                # The layer is not in the project, add it
                project.addMapLayer(layer)
                QgsMessageLog.logMessage(f"Layer {layer.name()} has been added to the project.")
            else:
                # The layer is already in the project
                QgsMessageLog.logMessage(f"Layer {layer.name()} is already in the project.")

        # Now, for the program modules...
        # Search through the /_Proposals/ folder, find the highest project number, and create a new proposal
        def find_highest_proposal_number(folder_path):
            proposal_numbers = []
            for filename in os.listdir(folder_path):
                if filename.startswith("E23-"):
                    proposal_number = int(filename.split("-")[1].split("_")[0])
                    proposal_numbers.append(proposal_number)
            return max(proposal_numbers)

        def check_folder_create(folder_name):
            if not os.path.exists(folder_name): os.makedirs(folder_name)

        def check_folder_prj(num_proj, name_client, folder_name, src):
            # Append underscore to proj_num
            num_proj += "_"
            project_dir = None

            # Search for project in directory 'O:/Projects_Civil3D/'
            if not home_test: project_dir = 'O:/Projects_Civil3D/'
            if home_test: project_dir = 'D:/Destination/Projects_Civil3D/'
            project_exists = False
            project_path = None  # variable to store the exact project path
            for filename in os.listdir(project_dir):
                if num_proj in filename and name_client in filename:
                    project_exists = True
                    project_path = os.path.join(project_dir, filename)  # get the exact project path
                    break

            if project_exists:
                # If project exists, do not copy template, instead update folder_name
                folder_name = project_path
                gis_new_path = os.path.join(folder_name, "gis_new")
                check_folder_create(gis_new_path)
            if folder_choice and not project_exists:
                check_folder_create(destination_shp)
                check_folder_create(destination_ras)
                if dxf_choice: check_folder_create(destination_dxf)
                if map_choice: check_folder_create(destination_map)
            if not folder_choice and not project_exists:
                # If project does not exist, copy the template to create a new project
                new_prj_src = f'{src}_New Client Template_E23-XXXX_CLIENT NAME'
                shutil.copytree(new_prj_src, folder_name)

                # Get the current time in seconds since the epoch
                current_time = datetime.datetime.now().timestamp()

                # Update the "date modified" for the destination folder and all its contents
                for root, dirs, files in os.walk(folder_name):
                    for dir_ in dirs:
                        os.utime(os.path.join(root, dir_), (current_time, current_time))
                    for file in files:
                        os.utime(os.path.join(root, file), (current_time, current_time))

                # Update the "date modified" for the top-level folder as well
                os.utime(folder_name, (current_time, current_time))

            return project_exists, project_path  # return a boolean and the project folder path

        def export_layers_to_dxf(layer_settings, dest_path):
            # Set the CRS to EPSG:2225
            crs = QgsCoordinateReferenceSystem("EPSG:2225")

            # Create a list to hold the layers
            layers = []

            # Loop through the layer_settings and add each layer to the list
            for settings in layer_settings:
                layer = QgsProject.instance().mapLayersByName(settings['name'])
                if not layer:
                    continue
                layer = layer[0]

                # Set the style options for the layer
                style_options = [
                    f'LayerColor={settings["color"]}',
                    f'LayerPenWidth={settings["penwidth"]}',
                    f'LayerLineType={settings["linetype"]}'
                ]

                # Export the layer to a temporary DXF file with the style options
                temp_dxf = f'{destination_dxf}temp_{settings["name"]}.dxf'
                options = QgsVectorFileWriter.SaveVectorOptions()
                options.driverName = 'DXF'
                options.layerOptions = style_options
                options.dstCrs = crs
                QgsVectorFileWriter.writeAsVectorFormatV3(layer, temp_dxf, QgsProject.instance().transformContext(),
                                                          options)

                # Add the temporary DXF file to the list
                layers.append(temp_dxf)

            # Merge the temporary DXF files into a single DXF file
            output_dxf = dest_path
            with open(output_dxf, 'w') as outfile:
                for temp_dxf in layers:
                    with open(temp_dxf, 'r') as infile:
                        outfile.write(infile.read())

        def get_dem_raster(task, source, parcel, destination):
            self.buffer_dem = buffer_dem
            with rasterio.open(source) as src:
                src_transform = src.transform
                src_nodata = src.nodata
                src_crs = src.crs

                # Calculate the buffer
                self.project_parcel = gpd.read_file(parcel)
                poly = self.project_parcel.iloc[0]
                buffer = poly.geometry.buffer(self.buffer_dem)

                # Transform the buffer to the same CRS as the raster
                buffer_gdf = gpd.GeoDataFrame(index=[0], geometry=[dem_radius_buffer])
                buffer_gdf = buffer_gdf.set_crs('epsg:2225')
                buffer_gdf = buffer_gdf.to_crs(src_crs)

                # Get the bounds of the buffer
                left, bottom, right, top = buffer_gdf.bounds.iloc[0]

                # Get the window of the raster that intersects with the buffer
                window = rasterio.windows.from_bounds(left=left, bottom=bottom, right=right, top=top,
                                                      transform=src_transform)

                # Read the raster data within the window
                raster_data = src.read(1, window=window)

                # Mask the NaN values
                mask = ~np.isnan(raster_data)
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
                window = rasterio.windows.from_bounds(left=left, bottom=bottom, right=right, top=top,
                                                      transform=src_transform)

                # Read the data again with the new window
                raster_data = src.read(1, window=window)

                # Set the NoData values to NaN
                raster_data = np.where(raster_data == src_nodata, np.nan, raster_data)

                # Get the width and height of the clipped raster
                out_width = window.width
                out_height = window.height

                # Calculate the transform of the clipped raster
                src_transform = rasterio.transform.from_bounds(left, bottom, right, top, out_width, out_height)

                # Save the clipped raster data to a new file
                with rasterio.open(destination, 'w', driver='GTiff', width=window.width, height=window.height,
                                   count=1, dtype=raster_data.dtype, crs=src_crs, transform=src_transform,
                                   nodata=np.nan) as dst:
                    dst.write(raster_data, 1)

                epsg_code = src.crs.to_string()
                if ':' in epsg_code:
                    epsg_in = int(epsg_code.split(":")[-1])
                else:
                    crs_obj = QgsCoordinateReferenceSystem.fromWkt(epsg_code)
                    if crs_obj.isValid():
                        epsg_in = crs_obj.postgisSrid()
                    else:
                        QgsMessageLog.logMessage(f"Could not parse CRS from: {epsg_code}", level=Qgis.Critical)
                        return None

                return epsg_in

        def dem_raster_source(merged):
            # Initialize DEM flags
            # Initialize DEM flags
            dem_flags = {
                'dem1m': False,
                'dem1m_simms': False,
                'dem1m_klam': False,
                'dem1m_horse': False
            }
            dem_layers = {
                'dem1m': (destination_1m_dem, source_1m_dem, flow_accumulation_src,
                          "USGS 3DEP HIGH-RESOLUTION DEM (1-METER)"),
                'dem1m_simms': (destination_1m_simms, source_simms, flow_accumulation_simms,
                                "USFS 2012 SIMMS FIRE DEM (1-METER)"),
                'dem1m_klam': (destination_1m_klam, source_klam, flow_accumulation_klam,
                               "USFS 2013 BLUFF CREEK DEM (1-METER)"),
                'dem1m_horse': (destination_1m_horse, source_horse, flow_accumulation_horse,
                                "NCALM SEED GRANT 2019 DEM (0.5-METER)")
            }

            def dem_task_finished(exception, result=None):
                if exception is None:
                    if result is None:
                        QgsMessageLog.logMessage(
                            'Completed with no exception and no result ' \
                            '(probably manually canceled by the user)',
                            MESSAGE_CATEGORY, Qgis.Warning)

                    else:
                        QgsMessageLog.logMessage(
                            'Task {name} completed\n'
                            'Total: {total} ( with {iterations} '
                            'iterations)'.format(
                                name=result['task'],
                                total=result['total'],
                                iterations=result['iterations']),
                            MESSAGE_CATEGORY, Qgis.Info)
                else:
                    QgsMessageLog.logMessage("Exception: {}".format(exception),
                                             MESSAGE_CATEGORY, Qgis.Critical)
                    raise exception

            # Helper function to check intersection
            def check_dem_intersection(file_path, dem_key):
                gdf = gpd.read_file(file_path)
                for _, row in gdf.iterrows():
                    shapely_polygon = row['geometry']
                    polygon_wkt = dumps(shapely_polygon)
                    polygon_qgs = QgsGeometry.fromWkt(polygon_wkt)
                    if parcel_center.within(polygon_qgs) or merged.intersects(polygon_qgs):
                        dem_flags[dem_key] = True
                        break
                del gdf

            # Check which DEM the parcel is in
            check_dem_intersection(dem_1m_bound, 'dem1m')
            check_dem_intersection(simms_bound, 'dem1m_simms')
            check_dem_intersection(klam_bound, 'dem1m_klam')
            check_dem_intersection(horse_bound, 'dem1m_horse')

            # Determine the appropriate DEM layer
            raster_file, input_epsg, flow_acc_src, dem1m_layer_name = None, None, None, None
            for dem_key, status in dem_flags.items():
                if status:
                    raster_file, source_file, flow_acc_src, dem1m_layer_name = dem_layers[dem_key]
                    dem1m = True

                    dem_task_1 = RasterExtraction(
                        do_goog=False,
                        do_naip=False,
                        do_dem=True,
                        goog_layer=None,
                        dem_radius_buffer=buffer_dem,
                        goog_geo_dst=None,
                        goog_geo2225=None,
                        naip_temp=None,
                        naip_dst=None,
                        dem_layer=source_dem,
                        dem_dst=raster_file,
                        flow_src=flow_acc_src
                    )

                    params = {
                        'INPUT': raster_file,
                        'SLOPE_FORMAT': 'percent',
                        'OUTPUT': slope_per
                    }

                    context_slope_per = QgsProcessingContext()
                    feedback_slope_per = QgsProcessingFeedback()

                    alg = QgsApplication.processingRegistry().algorithmById('qgis:slope')
                    if alg is None:
                        QgsMessageLog.logMessage("DEM Processing: Slope algorithm not found", level=Qgis.Critical)
                    # else:
                    slope_percent_task = QgsProcessingAlgRunnerTask(alg, params, context_slope_per, feedback_slope_per)
                    slope_percent_task.addSubTask(dem_task_1, [], QgsTask.ParentDependsOnSubTask)

                    params = {
                        'INPUT': raster_file,
                        'OUTPUT': slope_deg
                    }

                    context_slope_deg = QgsProcessingContext()
                    feedback_slope_deg = QgsProcessingFeedback()

                    alg = QgsApplication.processingRegistry().algorithmById('qgis:slope')
                    if alg is None:
                        QgsMessageLog.logMessage("DEM Processing: Slope algorithm not found", level=Qgis.Critical)
                    # else:
                    slope_degree_task = QgsProcessingAlgRunnerTask(alg, params, context_slope_deg, feedback_slope_deg)
                    slope_degree_task.addSubTask(dem_task_1, [], QgsTask.ParentDependsOnSubTask)

                    params = {
                        'INPUT': raster_file,
                        'OUTPUT': hillshade_dst
                    }

                    context_hillshade = QgsProcessingContext()
                    feedback_hillshade = QgsProcessingFeedback()

                    alg = QgsApplication.processingRegistry().algorithmById('native:hillshade')
                    if alg is None:
                        QgsMessageLog.logMessage("DEM Processing: Hillshade algorithm not found", level=Qgis.Critical)
                    # else:
                    hillshade_task = QgsProcessingAlgRunnerTask(alg, params, context_hillshade, feedback_hillshade)
                    hillshade_task.addSubTask(dem_task_1, [], QgsTask.ParentDependsOnSubTask)

                    MESSAGE_CATEGORY = 'ContoursTask'
                    output_epsg = 2225

                    def create_contours(task):
                        if (selected_raster_status["Digital Elevation Model Raster"]
                                and selected_site_data_status["Site Contours"]):
                            intervals = [2, 10, 20, 40, 100, 200]
                            for interval in intervals:
                                # Define the parameters for the contour algorithm
                                params = {
                                    'INPUT': raster_file,
                                    'BAND': 1,
                                    'INTERVAL': interval,
                                    'FIELD_NAME': 'ELEV',
                                    'CREATE_3D': True,
                                    'OUTPUT': f"{destination_shp}{proj_num}_CONTOURS_{interval}ft-{output_epsg}.shp"
                                }
                                # Execute the algorithm
                                result = processing.run("gdal:contour", params, feedback=QgsProcessingFeedback())

                                # Check if task was canceled
                                if task.isCanceled():
                                    return None

                    def contour_task_finished(exception, destination_shp, proj_num, output_epsg, project, group3,
                                              style_uris,
                                              result=None):
                        contours_finished = True
                        pass

                    # Create the task from the function
                    contour_task = QgsTask.fromFunction('Create Contours', create_contours,
                                                        on_finished=contour_task_finished)
                    # Add the contour task to the task manager
                    if selected_raster_status["Digital Elevation Model Raster"] and selected_site_data_status[
                        "Site Contours"]:
                        contour_task.addSubTask(slope_percent_task, [dem_task_1])
                        contour_task.addSubTask(slope_degree_task, [dem_task_1])
                        contour_task.addSubTask(hillshade_task, [dem_task_1])

                    QgsApplication.taskManager().addTask(contour_task)
                    break
            else:  # This else corresponds to the for loop, it executes if no break was hit
                raster_file = destination_dem
                dem1m = False
                dem_task_1 = DemRaster(
                    source_dem,
                    selected_dst,
                    raster_file,
                    buffer_dem,
                )
                dem1m_layer_name = "10M HUM_CO USGS DEM (1/3 ARC-SECOND)"

                MESSAGE_CATEGORY = 'ContoursTask'
                output_epsg = 2225

                def create_contours(task):
                    if (selected_raster_status["Digital Elevation Model Raster"]
                            and selected_site_data_status["Site Contours"]):
                        intervals = [2, 10, 20, 40, 100, 200]
                        for interval in intervals:
                            # Define the parameters for the contour algorithm
                            params = {
                                'INPUT': raster_file,
                                'BAND': 1,
                                'INTERVAL': interval,
                                'FIELD_NAME': 'ELEV',
                                'CREATE_3D': True,
                                'OUTPUT': f"{destination_shp}{proj_num}_CONTOURS_{interval}ft-{output_epsg}.shp"
                            }
                            # Execute the algorithm
                            result = processing.run("gdal:contour", params, feedback=QgsProcessingFeedback())

                            # Check if task was canceled
                            if task.isCanceled():
                                return None

                def contour_task_finished(exception, destination_shp, proj_num, output_epsg, project, group3,
                                          style_uris,
                                          result=None):
                    contours_finished = True
                    pass

                # Create the task from the function
                contour_task = QgsTask.fromFunction('Create Contours', create_contours,
                                                    on_finished=contour_task_finished)
                contour_task.addSubTask(dem_task_1, [], QgsTask.ParentDependsOnSubTask)
                QgsApplication.taskManager().addTask(contour_task)


            return raster_file, dem_flags, input_epsg, dem1m, dem1m_layer_name, dem_layers

        def assign_stream_vector(dem_flags):
            # Maps the dem_flag to the corresponding stream vector file path
            stream_vector_map = {
                'dem1m': source_1m_dem_stream,
                'dem1m_simms': source_simms_stream,
                'dem1m_klam': source_klam_stream,
                'dem1m_horse': source_horse_stream
            }

            for dem_key, is_selected in dem_flags.items():
                if is_selected:
                    return stream_vector_map.get(dem_key)

            # If none are selected, you may want to return a default or handle this case separately
            return None

        project_file_loc = execute_code()

        project_file = f"{destination_gis}{proj_num}{proj_name}_PROJECT MASTER.qgz"

        QgsProject.instance().write(project_file)

        for dirpath, dirnames, filenames in os.walk(prj_folder):
            for filename in filenames:
                if 'temp.' in filename:
                    try:
                        os.remove(os.path.join(dirpath, filename))
                    except OSError as e:
                        QgsMessageLog.logMessage("Error during file deletion. Please delete temporary files manually.")

        return {self.OP_PROJECT_FILE: project_file_loc}

    def end_dialog(self, prj_folder):
        FinalDialog.show_final(prj_folder)

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Omsberg & Preston Project Creator'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return ''

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return procplug1Algorithm()

