# Variable definition file for source files

import datetime
from qgis.core import QgsProject, QgsCoordinateReferenceSystem

global selected_dst, adjacent_dst, buffer_dst, surrounding_dst, road_dst, streams_dst, city_dst, zoning_dst, \
    gplan_dst, planning_dst, service_dst, public_dst, williamson_dst, fire_dst, coastal_dst, fema_dst, \
    slope_stab_dst, slope_stab_bay, alquist_pri_dst, ag_lands_dst, bio_res_dst, liquefaction_dst, airport_comp_dst, \
    airport_rnwy_dst, airport_point_dst, tiger_rds_cnty_dst, tiger_rds_dst, forest_srvc_rds_dst, legacy_humco_cl_dst, \
    rail_dst, trail_dst, timber_harvest_dst, soils_dst, slope_30_dst, slope_15_dst, fire_risk_dst, tsunami_dst, \
    woodland_dst, invasive_dst, faultline_dst, bedrock_dst, wetlands_dst, millcreek_wetlands_dst, fire_station_dst, \
    fire_hydrants_dst, structures_dst, temp_min_dst, temp_max_dst, mintemp_dst, maxtemp_dst, precip_annual, \
    precip_jan, precip_feb, precip_mar, precip_apr, precip_may, precip_jun, precip_jul, precip_aug, precip_sep, \
    precip_oct, precip_nov, precip_dec, destination_1m_dem, destination_1m_simms, destination_1m_klam, \
    destination_1m_horse, destination_dem, goog_geo_dst, goog_geo2225, naip_dst, naip_temp, slope_per, slope_deg, \
    map_dst, position_x, position_y, group2, dem_radius_buffer, progress_window

# Boolean variables affecting source variable creation
home_test = True  # Are we testing this at the outside of the office?
test_file = False  # Are we in the test file or the live file?
test_mode = False  # Do we need to hurry up on processing?
laptop_mode = False  # Are we doing this on the laptop?
local_mode = False  # Are we using the local copy of the code on the laptop

today = datetime.datetime.now()
project = QgsProject.instance()
crs = QgsCoordinateReferenceSystem("EPSG:2225")

# Source and destination base variables
source_shp = 'P:/_Information/OP_PROJECT_CREATOR/Source/' if not home_test else 'D:/Source/'  # Directory for source files
source_zip = f'{source_shp}ZIP File Update Check/'  # Directory for source file zip folders
config_file_path = f'{source_zip}saved_filenames.json'  # Path to file storing names of zip for updating source data
apn_path = f'{source_shp}APN_list.txt'  # Path to file storing APN list for checking parcel validity
source_lay = f'{source_shp}LayerStyles/'  # Source directory for layer styles
source_dwg = f'{source_shp}_New Client Template_E23-XXXX_CLIENT NAME/dwg/'  # Source directory for dwg folder template
output_dst_default = 'O:/' if not home_test else 'D:/Destination/'  # Directory for data and project folder output for default operation
output_dst_test = 'P:/_Information/_TEST PROJECTS/' if not home_test else 'D:/Destination/TEST/'  # Directory for test/experimental projects
prop_path_loc = f'P:/_Proposals/{str(today.year)}/' if not home_test else f'D:/Destination/_Proposals/{str(today.year)}/'  # Proposal file directory

# Source for raster data files
raster_src = f'{source_shp}DEM_Files/' if not laptop_mode else 'C:/Users/lbdas/_ENGINEERING CODING FILE CACHE/DEM_Files/'  # Raster source folder
dem_1m_bound = f'{raster_src}1M_USGS_DEM-Vector Footprint.shp'
simms_bound = f'{raster_src}SIMMS FIRE-Vector Footprint.shp'
klam_bound = f'{raster_src}KLAMATH-Vector Footprint.shp'
horse_bound = f'{raster_src}HORSE_LINTO-Vector Footprint.shp'
source_1m_dem = f'{raster_src}1M_USGS_DEM.tif'
source_simms = f'{raster_src}SIMMS_1M_FEET.tif'
source_klam = f'{raster_src}KLAMATH_1M_FEET.tif'
source_horse = f'{raster_src}HORSE_LINTO_1M_FEET.tif'
source_dem = f'{raster_src}USGS_10M_FEET.tif'
naip_jp2 = f'{raster_src}NAIP_JP2/'
naip_src = f'{raster_src}NAIP_2022/NAIP_2022_SID.sid'
flow_accumulation_src = f'{raster_src}USGS-1M_FLOW_ACCUMULATION.tif'
flow_accumulation_simms = f'{raster_src}SIMMS_FLOW ACCUMULATION.tif'
flow_accumulation_klam = f'{raster_src}KLAMATH FLOW ACCUMULATION.tif'
flow_accumulation_horse = f'{raster_src}HORSE_FLOW ACCUMULATION.tif'

# Source for vector data files
parcel_src = f'{source_shp}Parcels/HumCo_Parcels.shp'
road_src = f'{source_shp}Roads/HumCo_Road_CL.shp'
stream_src = f'{source_shp}Streams/HumCo_Streams.shp'
naip_tiles = f'{source_shp}NAIP_JP2/NAIP_TILE-INDEX_2022-2225.shp'
source_horse_stream = f'{source_shp}Streams/HORSE_VECTOR-2225.shp'
source_klam_stream = f'{source_shp}Streams/KLAMATH_FINAL_VECTOR-2225.shp'
source_simms_stream = f'{source_shp}Streams/SIMMS_FINAL_VECTOR-2225.shp'
source_1m_dem_stream = f'{source_shp}Streams/1M_USGS_DEM_FINAL_VECTOR-2225.shp'

# Source for layer styles
uri_v1 = f'{source_lay}streams.qml'
uri_v2 = f'{source_lay}road_cl.qml'
uri_v3 = f'{source_lay}buffer.qml'
uri_v4 = f'{source_lay}surround.qml'
uri_v5 = f'{source_lay}adjacent.qml'
uri_v6 = f'{source_lay}proj_par.qml'
uri_v7 = f'{source_lay}contours2.qml'
uri_v8 = f'{source_lay}contours10.qml'
uri_v9 = f'{source_lay}contours20.qml'
uri_v10 = f'{source_lay}contours40.qml'
uri_v11 = f'{source_lay}contours100.qml'
uri_v12 = f'{source_lay}liquefaction.qml'
uri_v13 = f'{source_lay}bio.qml'
uri_v14 = f'{source_lay}ag_lands.qml'
uri_v15 = f'{source_lay}alquist_priolo.qml'
uri_v16 = f'{source_lay}bay_slope.qml'
uri_v17 = f'{source_lay}county_slope.qml'
uri_v18 = f'{source_lay}municipal.qml'
uri_v19 = f'{source_lay}zoning.qml'
uri_v20 = f'{source_lay}planning_area.qml'
uri_v21 = f'{source_lay}service_districts.qml'
uri_v22 = f'{source_lay}public_lands.qml'
uri_v23 = f'{source_lay}williamson_act.qml'
uri_v24 = f'{source_lay}fire_district.qml'
uri_v25 = f'{source_lay}coastal.qml'
uri_v26 = f'{source_lay}flood.qml'
uri_v28 = f'{source_lay}stations.qml'
uri_v29 = f'{source_lay}hydrants.qml'
uri_v30 = f'{source_lay}structures.qml'
uri_v31 = f'{source_lay}min_81-10.qml'
uri_v32 = f'{source_lay}max_81-10.qml'
uri_v33 = f'{source_lay}mintemp.qml'
uri_v34 = f'{source_lay}maxtemp.qml'
uri_v35 = f'{source_lay}precip_all.qml'
uri_v48 = f'{source_lay}wetlands.qml'
uri_v49 = f'{source_lay}bed_geo.qml'
uri_v50 = f'{source_lay}faults.qml'
uri_v51 = f'{source_lay}invasive.qml'
uri_v52 = f'{source_lay}woodland.qml'
uri_v53 = f'{source_lay}tsunami.qml'
uri_v54 = f'{source_lay}fire_risk.qml'
uri_v55 = f'{source_lay}slope15.qml'
uri_v56 = f'{source_lay}slope30.qml'
uri_v57 = f'{source_lay}soils.qml'
uri_v58 = f'{source_lay}timber.qml'
uri_v59 = f'{source_lay}trails.qml'
uri_v60 = f'{source_lay}rails.qml'
uri_v61 = f'{source_lay}legacy.qml'
uri_v62 = f'{source_lay}frst_serv.qml'
uri_v63 = f'{source_lay}census_roads.qml'
uri_v64 = f'{source_lay}census_roads_cnty.qml'
uri_v65 = f'{source_lay}airport.qml'
uri_v66 = f'{source_lay}runway.qml'
uri_v67 = f'{source_lay}compat_airport.qml'
uri_v68 = f'{source_lay}woodland_fire.qml'
uri_v69 = f'{source_lay}road_points_1.qml'
uri_v70 = f'{source_lay}road_points_2.qml'
uri_v71 = f'{source_lay}road_points_3.qml'
uri_v72 = f'{source_lay}road_points_4.qml'
uri_v73 = f'{source_lay}road_points_5.qml'
percent_style = f'{source_lay}slope_percent.qml'

selected_files_status = \
    {file_name: True for file_name in ["City Limits", "Humboldt County Zoning", "General Plan Land Use", "Community "
                                       "Planning Areas", "Community Service Districts", "Public Lands", "Williamson "
                                       "Act Lands", "Fire District", "Coastal Zone", "Flood Zone", "Slope Stability "
                                       "(COUNTY)", "Slope Stability (HUMBOLDT BAY)", "Alquist-Priolo Zones",
                                       "Agricultural Lands", "Biological Resource Areas", "Liquefaction Zones",
                                       "Airport Compatibility Zone", "Airport Locations", "Airport Runways", "US "
                                       "Census Road Data (County Corrected)", "US Census Road Data", "Forest Service "
                                       "Roads", "Legacy Humboldt County Road Linework", "Railways", "Hiking Trails",
                                       "Timber Harvest Areas", "Soil Classification", "Slopes Greater than 30%",
                                       "Slopes Less than 15%", "Wildland Fire Risk", "Tsunami Inundation Zone",
                                       "Woodland Cover", "Invasive Plant Species", "Earthquake Fault Lines",
                                       "Underlying Bedrock Composition", "Mapped Wetlands", "Mill Creek Wetlands",
                                       "Fire Stations", "Fire Hydrants", "Structures", "Minimum Temperature",
                                       "Maximum Temperature", "Minimum Temperature (1981-2010)", "Maximum Temperature"
                                                                                                 " (1981-2010)",
                                       "Annual Precipitation (1981-2010)", "Monthly Precipitation - January "
                                       "(1981-2010)", "Monthly Precipitation - February (1981-2010)",
                                       "Monthly Precipitation - March (1981-2010)", "Monthly Precipitation - "
                                       "April (1981-2010)", "Monthly Precipitation - May (1981-2010)",
                                       "Monthly Precipitation - June (1981-2010)", "Monthly Precipitation - July "
                                       "(1981-2010)", "Monthly Precipitation - August (1981-2010)",
                                       "Monthly Precipitation - September (1981-2010)", "Monthly Precipitation - "
                                       "October (1981-2010)", "Monthly Precipitation - November (1981-2010)",
                                       "Monthly Precipitation - December (1981-2010)"]}
selected_site_data_status = {file_name: True for file_name in ["Project Parcel", "Adjacent Parcels", "Surrounding "
                                                                                                     "Parcels",
                                                               "Road Centerlines", "Streams", "Site "
                                                                                              "Contours"]}
selected_raster_status = {file_name: True for file_name in ["Google Earth Aerial", "2022 NAIP Aerial", "Digital "
                                                                                                       "Elevation "
                                                                                                       "Model Raster",
                                                            "Slope Raster"]}

goog_finished = False
naip_finished = False
contours_finished = False
raster_task_finished = False
dem_finished = False

# Generate destination variables for the project after user input is received
def generate_dst(dst_shp, dst_ras, dst_map, proj_num):
    global selected_dst, adjacent_dst, buffer_dst, surrounding_dst, road_dst, streams_dst, city_dst, zoning_dst, \
        gplan_dst, planning_dst, service_dst, public_dst, williamson_dst, fire_dst, coastal_dst, fema_dst, \
        slope_stab_dst, slope_stab_bay, alquist_pri_dst, ag_lands_dst, bio_res_dst, liquefaction_dst, airport_comp_dst, \
        airport_rnwy_dst, airport_point_dst, tiger_rds_cnty_dst, tiger_rds_dst, forest_srvc_rds_dst, legacy_humco_cl_dst, \
        rail_dst, trail_dst, timber_harvest_dst, soils_dst, slope_30_dst, slope_15_dst, fire_risk_dst, tsunami_dst, \
        woodland_dst, invasive_dst, faultline_dst, bedrock_dst, wetlands_dst, millcreek_wetlands_dst, fire_station_dst, \
        fire_hydrants_dst, structures_dst, temp_min_dst, temp_max_dst, mintemp_dst, maxtemp_dst, precip_annual, \
        precip_jan, precip_feb, precip_mar, precip_apr, precip_may, precip_jun, precip_jul, precip_aug, precip_sep, \
        precip_oct, precip_nov, precip_dec, destination_1m_dem, destination_1m_simms, destination_1m_klam, \
        destination_1m_horse, destination_dem, goog_geo_dst, goog_geo2225, naip_dst, naip_temp, slope_per, slope_deg, \
        map_dst

    # Define the output location for the shapefiles
    selected_dst = f'{dst_shp}{proj_num}_Project_Parcel-2225.shp'
    adjacent_dst = f'{dst_shp}{proj_num}_Adjacent_Parcels-2225.shp'
    buffer_dst = f'{dst_shp}{proj_num}_Buffer_Parcels-2225.shp'
    surrounding_dst = f'{dst_shp}{proj_num}_Surrounding Parcels-2225.shp'
    road_dst = f'{dst_shp}{proj_num}_Road_Centerline-2225.shp'
    streams_dst = f'{dst_shp}{proj_num}_Streams-2225.shp'
    city_dst = f'{dst_shp}{proj_num}_City_Limits-2225.shp'
    zoning_dst = f'{dst_shp}{proj_num}_Zoning-2225.shp'
    gplan_dst = f'{dst_shp}{proj_num}_General_Plan_Land_Use-2225.shp'
    planning_dst = f'{dst_shp}{proj_num}_Planning-2225.shp'
    service_dst = f'{dst_shp}{proj_num}_Service_Districts-2225.shp'
    public_dst = f'{dst_shp}{proj_num}_Public_Lands-2225.shp'
    williamson_dst = f'{dst_shp}{proj_num}_Williamson_Act-2225.shp'
    fire_dst = f'{dst_shp}{proj_num}_Fire_Districts-2225.shp'
    coastal_dst = f'{dst_shp}{proj_num}_Coastal_Zone-2225.shp'
    fema_dst = f'{dst_shp}{proj_num}_Flood Zone-2225.shp'
    slope_stab_dst = f'{dst_shp}{proj_num}_Slope_Stability-2225.shp'
    slope_stab_bay = f'{dst_shp}{proj_num}_Slope_Stability_BAY-2225.shp'
    alquist_pri_dst = f'{dst_shp}{proj_num}_AlquistPriolo_Zone-2225.shp'
    ag_lands_dst = f'{dst_shp}{proj_num}_AgLands-2225.shp'
    bio_res_dst = f'{dst_shp}{proj_num}_Biological_Resources-2225.shp'
    liquefaction_dst = f'{dst_shp}{proj_num}_Liquefaction_Area-2225.shp'
    airport_comp_dst = f'{dst_shp}{proj_num}_Airport_Compatibility_Zone-2225.shp'
    airport_rnwy_dst = f'{dst_shp}{proj_num}_Airport_Runway-2225.shp'
    airport_point_dst = f'{dst_shp}{proj_num}_Airports-2225.shp'
    tiger_rds_cnty_dst = f'{dst_shp}{proj_num}_RoadCL-US_CENSUS_TIGER_DATA-Cnty-2225.shp'
    tiger_rds_dst = f'{dst_shp}{proj_num}_RoadCL-US_CENSUS_TIGER_DATA-2225.shp'
    forest_srvc_rds_dst = f'{dst_shp}{proj_num}_RoadCL-Forest_Service-2225.shp'
    legacy_humco_cl_dst = f'{dst_shp}{proj_num}_RoadCL_Legacy-HumCnty-2225.shp'
    rail_dst = f'{dst_shp}{proj_num}_HumCo_Railway-2225.shp'
    trail_dst = f'{dst_shp}{proj_num}_HumCo_Trails-2225.shp'
    timber_harvest_dst = f'{dst_shp}{proj_num}_Timber_Harvest_Areas-2225.shp'
    soils_dst = f'{dst_shp}{proj_num}_Soil_Classification-2225.shp'
    slope_30_dst = f'{dst_shp}{proj_num}_Slope_30%-2225.shp'
    slope_15_dst = f'{dst_shp}{proj_num}_Slope_15%-2225.shp'
    fire_risk_dst = f'{dst_shp}{proj_num}_Fire_Risk-2225.shp'
    tsunami_dst = f'{dst_shp}{proj_num}_Tsunami_Zone-2225.shp'
    woodland_dst = f'{dst_shp}{proj_num}_Woodland_Areas-2225.shp'
    invasive_dst = f'{dst_shp}{proj_num}_Invasive_Plants-2225.shp'
    faultline_dst = f'{dst_shp}{proj_num}_Earthquake_Fault_Lines-2225.shp'
    bedrock_dst = f'{dst_shp}{proj_num}_Bedrock-2225.shp'
    wetlands_dst = f'{dst_shp}{proj_num}_Wetlands-2225.shp'
    millcreek_wetlands_dst = f'{dst_shp}{proj_num}_Mill_Creek_Wetlands-2225.shp'
    fire_station_dst = f'{dst_shp}{proj_num}_Fire_Stations-2225.shp'
    fire_hydrants_dst = f'{dst_shp}{proj_num}_Fire_Hydrants-2225.shp'
    structures_dst = f'{dst_shp}{proj_num}_HumCo_Structures-2225.shp'
    temp_min_dst = f'{dst_shp}{proj_num}_Temp_1981-2010_MIN-2225.shp'
    temp_max_dst = f'{dst_shp}{proj_num}_Temp_1981-2010_MAX-2225.shp'
    mintemp_dst = f'{dst_shp}{proj_num}_Minimum_Temp-2225.shp'
    maxtemp_dst = f'{dst_shp}{proj_num}_Maximum_Temp-2225.shp'
    precip_annual = f'{dst_shp}{proj_num}_Annual_Precipitation-2225.shp'
    precip_jan = f'{dst_shp}{proj_num}_Mnthly_Precip-JAN-2225.shp'
    precip_feb = f'{dst_shp}{proj_num}_Mnthly_Precip-FEB-2225.shp'
    precip_mar = f'{dst_shp}{proj_num}_Mnthly_Precip-MAR-2225.shp'
    precip_apr = f'{dst_shp}{proj_num}_Mnthly_Precip-APR-2225.shp'
    precip_may = f'{dst_shp}{proj_num}_Mnthly_Precip-MAY-2225.shp'
    precip_jun = f'{dst_shp}{proj_num}_Mnthly_Precip-JUN-2225.shp'
    precip_jul = f'{dst_shp}{proj_num}_Mnthly_Precip-JUL-2225.shp'
    precip_aug = f'{dst_shp}{proj_num}_Mnthly_Precip-AUG-2225.shp'
    precip_sep = f'{dst_shp}{proj_num}_Mnthly_Precip-SEP-2225.shp'
    precip_oct = f'{dst_shp}{proj_num}_Mnthly_Precip-OCT-2225.shp'
    precip_nov = f'{dst_shp}{proj_num}_Mnthly_Precip-NOV-2225.shp'
    precip_dec = f'{dst_shp}{proj_num}_Mnthly_Precip-DEC-2225.shp'

    # Define the output location for the rasters and map file
    destination_1m_dem = f'{dst_ras}{proj_num}_1M_USGS_DEM-CLIPPED.tif'
    destination_1m_simms = f'{dst_ras}{proj_num}_1M_SIMMS-FIRE 2012_DEM-CLIPPED.tif'
    destination_1m_klam = f'{dst_ras}{proj_num}_1M_KLAMATH DEM-CLIPPED.tif'
    destination_1m_horse = f'{dst_ras}{proj_num}_1M_HORSE_LINTO DEM-CLIPPED.tif'
    destination_dem = f'{dst_ras}{proj_num}_HumCo_10M_DEM-CLIPPED-2225.tif'
    goog_geo_dst = f'{dst_ras}{proj_num}_goog_temp.tif'
    goog_geo2225 = f'{dst_ras}{proj_num}_GoogleGeoRef-2225.tif'
    naip_dst = f'{dst_ras}{proj_num}_NAIP-2225.tif'
    naip_temp = f'{dst_ras}{proj_num}_naip_temp.tif'
    slope_per = f'{dst_ras}{proj_num}_SLOPE(PERCENT).tif'
    slope_deg = f'{dst_ras}{proj_num}_SLOPE(DEGREE).tif'
    map_dst = f'{dst_map}PROJECT_OVERVIEW_MAP.png'








