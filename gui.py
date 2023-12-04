from PyQt5 import sip
from qgis.PyQt.QtCore import (
    Qt,
    QTimer,
    QRegExp,
)
from qgis.PyQt.QtGui import (
    QPixmap,
    QRegExpValidator
)
from qgis.PyQt.QtWidgets import (
    QWidget,
    QLineEdit,
    QListWidget,
    QHBoxLayout,
    QGroupBox,
    QCheckBox,
    QDialogButtonBox,
    QProgressBar,
    QSizePolicy,
    QTextEdit
)
from qgis.core import (
    QgsExpression,
    QgsProcessingException,
)
from qgis.gui import (
    QgsMapCanvas,
)
from .projinit_tools import *

global project_file, home_test, test_file, test_mode, laptop_mode, selected_files_status, selected_site_data_status, \
    selected_raster_status, file_path_loc, destination_gis, multiple_apn, apn_list, prj_folder, proj_apn, proj_name, \
    proj_num, proj_test, proj_type, dxf_choice, map_choice, folder_choice, buffer_radius, buffer_parcels, buffer_dem, \
    source_shp, destination_shp, qgis_path, r_layer1, destination_ras, dwg_folder, output_dst, proposal_check, \
    raster_file, input_epsg, dem1m, layer, buffer_layer, dst_file, layer_name, parcel_center, goog_geo_dst, \
    destination_dxf, destination_map, project, naip_temp, crs, year_dbl, mem_layer, goog_task


class CustomInputWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_update_instance = DataUpdate()
        self.canvas = QgsMapCanvas()
        self.extra_tools_dialog = None
        self.closeDialogSignal = pyqtSignal()

        global multiple_apn, apn_list
        main_layout = QVBoxLayout()
        multiple_apn = False
        apn_list = []

        # Create a QHBoxLayout for the image and input fields
        image_and_inputs_layout = QHBoxLayout()

        pixmap = QPixmap('P:/_Information/OP_PROJECT_CREATOR/Source/op_logo.png') if not home_test \
            else QPixmap('D:/Source/op_logo.png')

        label = QLabel()
        label.setPixmap(pixmap.scaled(660, 550, Qt.KeepAspectRatio))
        label.setAlignment(Qt.AlignCenter)
        image_and_inputs_layout.addWidget(label)

        info_box = QGroupBox("")
        info_box.setStyleSheet("QGroupBox { border: 1px solid gray; }")
        image_and_inputs_layout.addWidget(info_box)

        input_layout = QVBoxLayout()
        user_input_left_layout = QVBoxLayout()
        user_input_right_layout = QVBoxLayout()
        user_input_layout = QHBoxLayout()
        apn_center_layout = QVBoxLayout()
        apn_right_layout = QVBoxLayout()
        apn_layout = QHBoxLayout()

        button_layout = QHBoxLayout()

        self.read_me_button = QPushButton("P R O G R A M\nI N F O R M A T I O N")
        self.read_me_button.setFixedWidth(125)
        self.read_me_button.clicked.connect(self.show_read_me)
        button_layout.addWidget(self.read_me_button)

        self.downloadButton = QPushButton("U P D A T E\nG I S   D A T A")
        self.downloadButton.setFixedWidth(110)
        run_update = self.data_update_instance.run
        open_dialog = self.data_update_instance.update_dialog
        self.downloadButton.clicked.connect(run_update)

        button_layout.addWidget(self.downloadButton)

        input_layout.addLayout(button_layout)

        spacer = QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        input_layout.addSpacerItem(spacer)

        self.input1 = QLineEdit('')
        self.input1.setFixedWidth(70)
        user_input_left_layout.addWidget(QLabel('Project APN:'))
        apn_center_layout.addWidget(self.input1)
        reg_ex = QRegExp("[0-9-]*")
        input_validator = QRegExpValidator(reg_ex)
        self.input1.setValidator(input_validator)
        # self.input1.editingFinished.connect(self.handle_editing_finished)
        QTimer.singleShot(0, lambda: self.input1.setFocus() if sip.isdeleted(self.input1) is False else None)

        # Add a button to save the additional APNs
        self.add_apn_button = QPushButton("Multiple Parcels")
        self.add_apn_button.setFixedWidth(85)
        self.add_apn_button.clicked.connect(self.open_apn_dialog)
        apn_right_layout.addWidget(self.add_apn_button)

        apn_layout.addLayout(apn_center_layout)
        apn_layout.addLayout(apn_right_layout)
        user_input_right_layout.addLayout(apn_layout)

        self.input2 = QLineEdit(str(''))
        self.input2.setFixedWidth(161)
        user_input_left_layout.addWidget(QLabel('Client Name:'))
        user_input_right_layout.addWidget(self.input2)

        self.input3 = QLineEdit('')
        self.input3.setFixedWidth(161)
        user_input_left_layout.addWidget(QLabel('Project Number:'))
        user_input_right_layout.addWidget(self.input3)

        user_input_layout.addLayout(user_input_left_layout)
        user_input_layout.addLayout(user_input_right_layout)
        input_layout.addLayout(user_input_layout)

        spacer = QSpacerItem(0, 15, QSizePolicy.Minimum, QSizePolicy.Expanding)
        input_layout.addSpacerItem(spacer)

        button_info = QVBoxLayout()
        button_layout3 = QHBoxLayout()
        button_layout2 = QHBoxLayout()
        button_layout1 = QHBoxLayout()
        button_layout4 = QHBoxLayout()

        button_layout3.addWidget(QLabel('Layer Selection:'))

        # Create custom button for basic site data layers
        self.basic_site_data_button = QPushButton("Project Site\nBase Map")
        self.basic_site_data_button.clicked.connect(self.open_basic_site_data_selection_dialog)
        button_layout2.addWidget(self.basic_site_data_button)

        # Create custom button for raster data export
        self.raster_data_button = QPushButton("Raster\nSelection")
        self.raster_data_button.clicked.connect(self.open_raster_data_selection_dialog)
        button_layout2.addWidget(self.raster_data_button)

        # Create custom button for municipal boundary background data layers
        self.municipal_select_button = QPushButton("Municipal\nBoundaries")
        self.municipal_select_button.clicked.connect(self.open_municipal_selection_dialog)
        button_layout2.addWidget(self.municipal_select_button)

        # Create custom button for transportation & civil infrastructure background data layers
        self.civil_select_button = QPushButton("Transportation &&\nCivil Infrastructure")
        self.civil_select_button.clicked.connect(self.open_civil_selection_dialog)
        button_layout1.addWidget(self.civil_select_button)

        # Create custom button for natural, hydrological, & geological background data layers
        self.natural_select_button = QPushButton("Natural, Hydrological &&\nGeological Resources")
        self.natural_select_button.clicked.connect(self.open_natural_selection_dialog)
        button_layout1.addWidget(self.natural_select_button)

        # Create custom button for natural hazard background data layers
        self.hazard_select_button = QPushButton("Natural\nHazards")
        self.hazard_select_button.clicked.connect(self.open_hazard_selection_dialog)
        button_layout4.addWidget(self.hazard_select_button)

        # Create custom button for background data layers
        self.climate_select_button = QPushButton("Climate\nData")
        self.climate_select_button.clicked.connect(self.open_climate_selection_dialog)
        button_layout4.addWidget(self.climate_select_button)

        button_info.addLayout(button_layout3)
        button_info.addLayout(button_layout2)
        button_info.addLayout(button_layout1)
        button_info.addLayout(button_layout4)

        input_layout.addLayout(button_info)

        spacer = QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        input_layout.addSpacerItem(spacer)

        # Add buffer entry
        buffer_left = QVBoxLayout()
        buffer_center = QVBoxLayout()
        buffer_right = QVBoxLayout()
        buffer_params_layout = QHBoxLayout()

        radius_label = QLabel('Base Data Extraction Radius (ft):')
        # radius_label.setAlignment(Qt.AlignRight)
        self.buffer_radius_input = QLineEdit('1500')
        self.buffer_radius_input.setFixedWidth(60)
        self.buffer_radius_input.setAlignment(Qt.AlignCenter)
        buffer_left.addWidget(radius_label)
        buffer_center.addWidget(self.buffer_radius_input)

        parcels_label = QLabel('Background Data Extraction Radius (ft):')
        # parcels_label.setAlignment(Qt.AlignRight)
        self.buffer_parcels_input = QLineEdit('1500')
        self.buffer_parcels_input.setFixedWidth(60)
        self.buffer_parcels_input.setAlignment(Qt.AlignCenter)
        buffer_left.addWidget(parcels_label)
        buffer_center.addWidget(self.buffer_parcels_input)

        dem_label = QLabel('DEM/Aerial Extraction Radius (ft):')
        # dem_label.setAlignment(Qt.AlignRight)
        self.buffer_dem_input = QLineEdit('1500')
        self.buffer_dem_input.setFixedWidth(60)
        self.buffer_dem_input.setAlignment(Qt.AlignCenter)
        buffer_left.addWidget(dem_label)
        buffer_center.addWidget(self.buffer_dem_input)

        buffer_params_layout.addLayout(buffer_left)
        buffer_params_layout.addLayout(buffer_center)
        buffer_params_layout.addLayout(buffer_right)
        input_layout.addLayout(buffer_params_layout)

        spacer = QSpacerItem(0, 15, QSizePolicy.Minimum, QSizePolicy.Expanding)
        input_layout.addSpacerItem(spacer)

        image_and_inputs_layout.addLayout(input_layout)
        main_layout.addLayout(image_and_inputs_layout)

        # Create a vertical layout for checkboxes
        checkboxes_layout = QHBoxLayout()
        checkboxes_layout1 = QVBoxLayout()
        checkboxes_layout2 = QVBoxLayout()

        self.checkBox1 = QCheckBox('PROPOSAL')
        checkboxes_layout1.addWidget(self.checkBox1)

        self.checkBox2 = QCheckBox('TEST RUN')
        checkboxes_layout1.addWidget(self.checkBox2)

        self.checkBox3 = QCheckBox('CREATE DXF FOR PL AND TOPO-E (MINIMAL FUNCTIONALITY)')
        # checkboxes_layout.addWidget(self.checkBox3)

        self.checkBox4 = QCheckBox('CREATE OVERVIEW MAP')
        checkboxes_layout1.addWidget(self.checkBox4)

        self.checkBox5 = QCheckBox('CREATE ONLY NECESSARY FOLDERS')
        checkboxes_layout1.addWidget(self.checkBox5)

        self.checkBox6 = QCheckBox('EXTRACT ROAD POINT DATA (EXPERIMENTAL)')
        checkboxes_layout1.addWidget(self.checkBox6)

        checkboxes_layout.addLayout(checkboxes_layout1)
        checkboxes_layout.addLayout(checkboxes_layout2)

        input_layout.addLayout(checkboxes_layout)  # Add checkboxes layout to the input layout

        spacer = QSpacerItem(0, 15, QSizePolicy.Minimum, QSizePolicy.Expanding)
        input_layout.addSpacerItem(spacer)

        self.setLayout(main_layout)

    def open_basic_site_data_selection_dialog(self):
        global selected_site_data_status
        self.file_dialog = SiteDataSelectionDialog(self, selected_site_data_status)
        result = self.file_dialog.exec_()
        if result == QDialog.Accepted:
            selected_site_data_status = {file: checkbox.isChecked() for file, checkbox in
                                         self.file_dialog.file_status.items()}

    def open_file_selection_dialog(self):
        global selected_files_status
        self.file_dialog = FileSelectionDialog(self, selected_files_status)
        result = self.file_dialog.exec_()
        if result == QDialog.Accepted:
            selected_files_status.update(
                {file: checkbox.isChecked() for file, checkbox in self.file_dialog.file_status.items()})

    def open_civil_selection_dialog(self):
        global selected_files_status
        self.file_dialog = TranspoCivilSelectionDialog(self, selected_files_status)
        result = self.file_dialog.exec_()
        if result == QDialog.Accepted:
            selected_files_status.update(
                {file: checkbox.isChecked() for file, checkbox in self.file_dialog.file_status.items()})

    def open_natural_selection_dialog(self):
        global selected_files_status
        self.file_dialog = NaturalSelectionDialog(self, selected_files_status)
        result = self.file_dialog.exec_()
        if result == QDialog.Accepted:
            selected_files_status.update(
                {file: checkbox.isChecked() for file, checkbox in self.file_dialog.file_status.items()})

    def open_municipal_selection_dialog(self):
        global selected_files_status
        self.file_dialog = MunicipalSelectionDialog(self, selected_files_status)
        result = self.file_dialog.exec_()
        if result == QDialog.Accepted:
            selected_files_status.update(
                {file: checkbox.isChecked() for file, checkbox in self.file_dialog.file_status.items()})

    def open_hazard_selection_dialog(self):
        global selected_files_status
        self.file_dialog = HazardSelectionDialog(self, selected_files_status)
        result = self.file_dialog.exec_()
        if result == QDialog.Accepted:
            selected_files_status.update(
                {file: checkbox.isChecked() for file, checkbox in self.file_dialog.file_status.items()})

    def open_climate_selection_dialog(self):
        global selected_files_status
        self.file_dialog = ClimateSelectionDialog(self, selected_files_status)
        result = self.file_dialog.exec_()
        if result == QDialog.Accepted:
            selected_files_status.update(
                {file: checkbox.isChecked() for file, checkbox in self.file_dialog.file_status.items()})

    def open_apn_dialog(self):
        global multiple_apn, apn_list, input_1_test
        current_text = self.input1.text()
        input_1_test = False
        if len(current_text) >= 1:
            input_1_test = True
            fixed_text, is_apn = APNDialog.apn_verify(current_text)
            if is_apn:
                input_1_test = True
                self.input1.clear()
                apn_list.append(fixed_text)
                self.apn_dialog = APNDialog(apn_list)
        else:
            no_apn = []
            self.apn_dialog = APNDialog(no_apn)
        if self.apn_dialog.exec_() == QDialog.Accepted:
            self.input1.setPlaceholderText('Multiple APNs entered...')
            self.input1.setReadOnly(True)
            multiple_apn = True

    def open_raster_data_selection_dialog(self):
        global selected_raster_status
        self.file_dialog = RasterSelectionDialog(self, selected_raster_status)
        result = self.file_dialog.exec_()
        if result == QDialog.Accepted:
            selected_raster_status = {file: checkbox.isChecked() for file, checkbox in
                                      self.file_dialog.file_status.items()}

    def show_read_me(self):
        info_text = "O M S B E R G   &   P R E S T O N\nPROJECT CREATOR AND GEOSPATIAL DATA EXTRACTOR\n\nThis plugin" \
                    " was written to streamline the creation of projects at Omsberg & Preston, and to standardize " \
                    "project geospatial data collection and organization. All new proposal and project files " \
                    "should be created using this plugin. \n\nUpon execution of the plugin, all available geospatial " \
                    "data that intersects or overlays a given APN(s) in Humboldt County will be extracted. A QGIS " \
                    "project file (*.qgz) will be created containing all available shapefile and raster layers. As " \
                    "a default, all shapefile and raster layers are enabled. Please utilize the layer selection " \
                    "buttons only if you need to make any changes to this default. Default operation will create a " \
                    "new project folder in O:/Projects_Civil3D from the new client template for Omsberg & Preston, " \
                    "and extract all available geospatial data to the project's 'gis' folder, clipped to buffer " \
                    "extents. Before executing the plugin, ensure that the correct project type has been chosen (is " \
                    "it a proposal or test file?), and that the correct options for the intended use are " \
                    "selected (do you want specific layers or to create an overview map?). In the case that the " \
                    "project already exists in Projects_Civil3D, the program will create another folder called " \
                    "'gis_new' within the existing project folder for the client. \n\nAll operations and " \
                    "functionality are explained below, in the order they appear in the user interface " \
                    "layout:\nFor each project, the user is required to enter the project APN(s), the client " \
                    "name, and the project number. APN(s) may be entered in any fashion, but must contain at " \
                    "least 9 digits. Project can consist of multiple parcels (multiple APNs), but they must be " \
                    "contiguous (shared boundary lines). For projects with multiple parcels, click the 'Input " \
                    "multiple parcels' button. For single parcel projects, simply input the parcel number in the " \
                    "APN input box. The plugin will verify all user input for validity, and will verify that " \
                    "each entered APN exists in Humboldt County. The plugin will then extract all relevant " \
                    "geospatial data from a multitude of sources. Please see the end of this help dialog for a " \
                    "list of the current geospatial datasource layers. If any source data layer does not exist " \
                    "in the final output for a particular project, then that project does not coincide with any " \
                    "data from said layer (i.e. if the layer 'Earthquake Faults' is absent, then the project does " \
                    "not have any known fault lines in the immediate vicinity).\n\nLayers may be excluded (or " \
                    "included) using the buttons under 'Layer Selection'. Clicking these buttons will show the " \
                    "user a list of layers under each subheading. The subheadings are as follows:\n(1) Project " \
                    "Site Base Map: The project basics. This includes the project parcel itself, adjacent parcels, " \
                    "roads, streams, etc.\n(2) Raster Selection: Any raster data or imagery. This encompasses " \
                    "digital elevation models and aerial imagery.\n(3) Transportation & Civil Infrastructure: Fire " \
                    "hydrants, structures, additional road data, railways, airport locations, etc.\n(4) Natural, " \
                    "Hydrological, and Geological Resources: Any natural features. From wetlands and invasive " \
                    "plant species to earthquake fault lines and bedrock composition.\n(5) Municipal Boundaries: " \
                    "All lines drawn in the sand by human legislative action. Zoning, city limits, etc.\n(6) " \
                    "Natural Hazards: Any known hazards such as flood zones, slope stability, earthquake statistics, " \
                    "etc.\n(7) Climate Data: Available historic temperature and precipitation data from 1981-2010.\n" \
                    "\nData collection extent buffer radius for each data type may also be chosen by the user. This " \
                    "radius is measured extending from the property line of the project parcel. The default is 1500 " \
                    "feet, and may be left alone in most cases. In some cases the user may choose to shorten the radii" \
                    " for larger parcels, or extend them if more regional data is desired. The buffer radius is " \
                    "straightforward: A buffer of 50' will output data within 50' of the property line. Be sure to " \
                    "use a buffer distance sufficient to fill the viewport in the AutoCAD or other design file as " \
                    "needed\n\nThe user may also alter the default operation of the plugin with a few final" \
                    " considerations as follows: (1) checking the 'PROPOSAL' box will create the project folder in " \
                    "the current year folder in P:/_Proposals/; (2) 'TEST RUN' will allow the user to run the plugin " \
                    "on any APN they please, with the output being found in P:/_Information/_TEST PROJECTS; (3) " \
                    "choosing to create an overview map will create a standardized project overview in the 'Image'" \
                    " folder of the project; (4) 'CREATE ONLY NECESSARY FOLDERS' will create only the 'gis' folder in " \
                    "the folder output location. The folders 'dwg' and 'image' will be created in the case that those " \
                    "options are selected.\n\nThe plugin will automatically update the " \
                    "locally stored shapefile source data when the update button is pressed. This button will " \
                    "download the newest shapefile data from Humboldt County's GIS Database and update all relevant " \
                    "project data thereforth. This button will update the locally stored copies of the shapefiles " \
                    "that Humboldt County (at the time of this writing) regularly updates (parcels, road " \
                    "centerlines, general plan land use, zoning, etc.).\n\nImportant Points:\n* All files are " \
                    "exported in EPSG:2225 (CA State Plane Zone 1)\n* Minimum buffer values are 50' and maximum " \
                    "are 5000'\nWHEN PERFORMING ANY MANUAL SOURCE DATA UPDATE OR MAINTENANCE:\n(source data can be " \
                    "found in P:/OP_PROJECT_CREATOR/Source/)\n * When replacing existing shapefile data, ensure that " \
                    "all new filenames match previous shapefile source data filenames exactly.\n * The new files MUST " \
                    "be loaded into QGIS manually and converted to coordinate reference system EPSG:2225, as Humboldt" \
                    " County issues the files in a different coordinate reference system.\n\n\n\nPlease do not hesitite" \
                    " to contact Tyler Martin for any bugs, questions, or suggestions: (949) 525 1624\n\nVersion 1.7.2" \
                    "\nUpdated: September 30, 2023\n\n\n\nC u r r e n t   D a t a s o u r c e   L a y e r s :\nHUMBOLDT" \
                    " COUNTY:\nParcels\nRoad Centerline\nFire Hydrants\nFire Stations\nLegacy Road Centerline\nAirport " \
                    "Locations, Runways, Compatibility Zone\nBiological Resource Areas\nSlopes Greater than 30%\nSlopes" \
                    " Less than 15%\nMill Creek Wetlands\nEarthquake Fault Lines\nAlquist-Priolo (Liquefaction) Zones\n" \
                    "Coastal Zone\nWilliamson Act Lands\nPublic Lands\nCity Limits\nAgricultural Lands\nCommunity " \
                    "Planning Areas\nGeneral Plan Land Use\nCommunity Service Districts\nFire Districts\nZoning\nSlope " \
                    "Stability (Bay and County-wide)\n\nUS GOVERNMENT:\nCDFW Blue Line Streams\nCDFW Invasive " \
                    "Plant Species\nUSGS Digital Elevation Data\nUSGS Geologic Bedrock Data\nFEMA Structures\n" \
                    "FEMA Flood Zones\nUS Census Road Data\nUSFS Forest Roads\nUSFS Woodland Cover\nUSFS Timber " \
                    "Harvest Data\nUSFS Wildland Fire Risk\nNRCS Soil Classification Data\nNOAA Tsunami Inundation " \
                    "Zones\nNOAA Digital Elevation Data\nNOAA Temperature and Precipitation Data\n\nPRIVATE:\n" \
                    "Google Earth Imagery"

        info_dialog = QDialog()
        info_dialog.setWindowTitle("Read Me")
        info_dialog.setGeometry(150, 150, 1100, 700)

        layout = QVBoxLayout()

        info_text_edit = QTextEdit()
        info_text_edit.setPlainText(info_text)
        info_text_edit.setReadOnly(True)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(info_dialog.close)

        layout.addWidget(info_text_edit)
        layout.addWidget(ok_button)

        info_dialog.setLayout(layout)
        info_dialog.exec_()

    @staticmethod
    def return_apn_list(self):
        return apn_list


class APNDialog(QDialog):
    global apn_list

    def __init__(self, apn_list, parent=None):
        super().__init__(parent)
        global multiple_apn
        self.setWindowTitle("Add APNs")
        self.apn_list = apn_list

        # Create QLineEdit and buttons
        self.apn_input = QLineEdit()
        self.apn_input.setPlaceholderText('Enter APN and add to list:')

        reg_ex = QRegExp("[0-9]*")
        input_validator = QRegExpValidator(reg_ex)
        self.apn_input.setValidator(input_validator)
        self.apn_input.returnPressed.connect(self.add_apn)

        self.add_button = QPushButton('Add APN')
        self.add_button.clicked.connect(self.add_apn)

        self.remove_button = QPushButton('Remove APN')
        self.remove_button.clicked.connect(self.remove_apn)

        # Create QListWidget
        self.apn_list_widget = QListWidget()
        for apn in apn_list:
            self.apn_list_widget.addItems(apn)

        # Create OK and Cancel buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.try_accept)
        self.button_box.rejected.connect(self.reject)

        # Arrange widgets
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)

        layout = QVBoxLayout()
        layout.addWidget(QLabel('Enter additional APNs'))
        layout.addWidget(self.apn_input)
        layout.addLayout(button_layout)
        layout.addWidget(self.apn_list_widget)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

    @staticmethod
    def apn_verify(list_apn):
        apn_pattern = r'^\d{3}-\d{3}-\d{3}-0{3}$'
        proj_pattern = r'^\d{4}$|^\d{4}-\d{1,2}$|^\d{3}-\d{1,2}$'

        apn_valid = False

        def load_printkeys(parcel_list):
            with open(parcel_list, "r") as f:
                return set(line.strip() for line in f)

        source_ = "P:/_Information/OP_PROJECT_CREATOR/Source/" if not home_test else "D:/Source/"

        valid_apn_list = load_printkeys(f'{source_}APN_list.txt')

        sanitized_apns = []
        final_apns = []
        apn_valid = False  # Initialize this variable

        for apn in list_apn:
            clean_apn = APNDialog.sanitize_input(str(apn))
            sanitized_apns.append(clean_apn)

        for sanitized_apn in sanitized_apns:
            if not re.match(apn_pattern, sanitized_apn):
                QMessageBox.critical(None, 'ERROR', f'Invalid input format for APN {sanitized_apn}.')
                return sanitized_apns, apn_valid

            if sanitized_apn not in valid_apn_list:
                QMessageBox.critical(None, 'ERROR',
                                     f"Parcel APN {sanitized_apn} does not exist in Humboldt County. \n\nPlease"
                                     f" check input or, if you are sure this is an error and the APN is correct,"
                                     f" press 'Update GIS Data' on the main user input screen to update the "
                                     f"APN checksum list to the most recent version.")
                return sanitized_apns, apn_valid

            if sanitized_apn in valid_apn_list:
                apn_valid = True
                final_apns.append(sanitized_apn)  # Appends the sanitized APN to the list

        return final_apns, apn_valid

    @staticmethod
    def verify_contiguous(list_apn):
        sanitized_apns = []
        if len(list_apn) >= 1:
            sanitized_apns, is_apn = APNDialog.apn_verify(list_apn)
            if not is_apn:
                QMessageBox.critical(None, 'ERROR',
                                     f"Parcel APN {list_apn[0]} does not exist in Humboldt County. Please"
                                     f" check input or press 'Update GIS Data' on the main user input screen.")
                return
            else:
                return sanitized_apns

        # Initialize a dictionary to store APN and their geometries
        apn_geom_dict = {}
        adjacency_list = {}

        if not home_test:
            source_ = "P:/_Information/OP_PROJECT_CREATOR/Source/"
        else:
            source_ = "D:/Source/"

        parcel_ = f'{source_}Parcels/HumCo_Parcels.shp'
        parcels = QgsVectorLayer(parcel_, "HumCo Parcels", "ogr")

        # Populate the dictionary
        for apn in sanitized_apns:
            expr = QgsExpression(f"\"APN_12\"='{apn}'")
            request = QgsFeatureRequest(expr)
            for feature in parcels.getFeatures(request):
                apn_geom_dict[apn] = feature.geometry()
                adjacency_list[apn] = []

        # Build adjacency list
        for apn1, geom1 in apn_geom_dict.items():
            for apn2, geom2 in apn_geom_dict.items():
                if apn1 != apn2 and geom1.touches(geom2):
                    adjacency_list[apn1].append(apn2)

        # Implement DFS to check for contiguity
        visited = set()

        def dfs(node):
            visited.add(node)
            for neighbor in adjacency_list[node]:
                if neighbor not in visited:
                    dfs(neighbor)

        # Start DFS from the first APN in the list
        dfs(sanitized_apns[0])

        # Now check if all APNs are in the visited set
        is_contiguous = set(sanitized_apns) == visited

        if is_contiguous:
            if yes_input1: sanitized_apns = sanitized_apns.append(raw_apn)
            return sanitized_apns
        else:
            QMessageBox.critical(None, 'ERROR', "The Parcels are not contiguous. Please try again.")
            raise QgsProcessingException('Invalid Input')

    @staticmethod
    def sanitize_input(input_string):
        cleaned_string = "".join(filter(str.isdigit, input_string))
        # if len(cleaned_string) < 9: raise QgsProcessingException(f'Invalid input {input_string}, {cleaned_string}')

        while len(cleaned_string) < 12:
            cleaned_string += "0"
        formatted_string = f'{cleaned_string[:3]}-{cleaned_string[3:6]}-{cleaned_string[6:9]}-{cleaned_string[9:12]}'
        return formatted_string

    def add_apn(self):
        global apn_list, multiple_apn, fixed_apn
        current_text = self.apn_input.text()

        if len(current_text) > 0:  # Check if current_text has any text at all
            if len(current_text) >= 9 and current_text not in apn_list:
                current_apn = [current_text]
                fixed_apn = []
                fixed_apn, is_apn = APNDialog.apn_verify(current_apn)
                if is_apn:
                    apn_list.append(fixed_apn[0])
                    self.apn_list_widget.addItem(fixed_apn[0])
                    multiple_apn = True

                self.apn_input.clear()
                QTimer.singleShot(0, lambda: self.apn_input.setFocus())

    def remove_apn(self):
        global apn_list
        selected_items = self.apn_list_widget.selectedItems()
        for item in selected_items:
            self.apn_list_widget.takeItem(self.apn_list_widget.row(item))

    def try_accept(self):
        global apn_list  # Declare that we are using the global apn_list

        if not apn_list:
            QMessageBox.warning(self, 'Warning', 'No APNs entered. Please enter at least one APN.')
            return

        try:
            apn_list = self.verify_contiguous(apn_list)
            self.accept()
            QMessageBox.information(self, 'Success', 'APN List Accepted and Valid. APNs are contiguous.')
        except QgsProcessingException:
            QMessageBox.critical(self, 'Error', 'Invalid Input: APNs are not contiguous')


class FileSelectionDialog(QDialog):
    def __init__(self, parent=None, initial_status=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.file_status = {}
        for file_name in ["City Limits", "Humboldt County Zoning", "General Plan Land Use", "Community Planning Areas",
                          "Community Service Districts",
                          "Public Lands", "Williamson Act Lands", "Fire District", "Coastal Zone",
                          "Flood Zone", "Slope Stability (COUNTY)", "Slope Stability (HUMBOLDT BAY)",
                          "Alquist-Priolo Zones",
                          "Agricultural Lands", "Biological Resource Areas", "Liquefaction Zones"]:
            checkbox = QCheckBox(file_name)
            checkbox.setChecked(initial_status.get(file_name, False) if initial_status else False)
            layout.addWidget(checkbox)
            self.file_status[file_name] = checkbox

        spacer = QWidget()  # Create a spacer widget
        spacer.setFixedSize(1, 10)  # Set a fixed height for the spacer
        layout.addWidget(spacer)  # Add the spacer widget

        deselect_button = QPushButton("Deselect All")
        layout.addWidget(deselect_button)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

        deselect_button.clicked.connect(self.deselect_all_checkboxes)

    def deselect_all_checkboxes(self):
        for checkbox in self.file_status.values():
            checkbox.setChecked(False)


class TranspoCivilSelectionDialog(QDialog):
    def __init__(self, parent=None, initial_status=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.file_status = {}
        for file_name in ["Fire Hydrants", "Fire Stations", "Structures", "US Census Road Data (County Corrected)",
                          "US Census Road Data", "Forest Service Roads", "Legacy Humboldt County Road Linework",
                          "Railways", "Hiking Trails", "Airport Locations", "Airport Runways",
                          "Airport Compatibility Zone"]:
            checkbox = QCheckBox(file_name)
            checkbox.setChecked(initial_status.get(file_name, False) if initial_status else False)
            layout.addWidget(checkbox)
            self.file_status[file_name] = checkbox

        spacer = QWidget()  # Create a spacer widget
        spacer.setFixedSize(1, 10)  # Set a fixed height for the spacer
        layout.addWidget(spacer)  # Add the spacer widget

        deselect_button = QPushButton("Deselect All")
        layout.addWidget(deselect_button)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

        deselect_button.clicked.connect(self.deselect_all_checkboxes)

    def deselect_all_checkboxes(self):
        for checkbox in self.file_status.values():
            checkbox.setChecked(False)


class NaturalSelectionDialog(QDialog):
    def __init__(self, parent=None, initial_status=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.file_status = {}
        for file_name in ["Biological Resource Areas", "Invasive Plant Species", "Mapped Wetlands",
                          "Mill Creek Wetlands", "Timber Harvest Areas", "Woodland Cover", "Slopes Greater than 30%",
                          "Slopes Less than 15%", "Earthquake Fault Lines",
                          "Soil Classification", "Underlying Bedrock Composition"]:
            checkbox = QCheckBox(file_name)
            checkbox.setChecked(initial_status.get(file_name, False) if initial_status else False)
            layout.addWidget(checkbox)
            self.file_status[file_name] = checkbox

        spacer = QWidget()  # Create a spacer widget
        spacer.setFixedSize(1, 10)  # Set a fixed height for the spacer
        layout.addWidget(spacer)  # Add the spacer widget

        deselect_button = QPushButton("Deselect All")
        layout.addWidget(deselect_button)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

        deselect_button.clicked.connect(self.deselect_all_checkboxes)

    def deselect_all_checkboxes(self):
        for checkbox in self.file_status.values():
            checkbox.setChecked(False)


class MunicipalSelectionDialog(QDialog):
    def __init__(self, parent=None, initial_status=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.file_status = {}
        for file_name in ["Coastal Zone", "Williamson Act Lands", "Agricultural Lands", "Public Lands", "City Limits",
                          "Community Planning Areas", "General Plan Land Use", "Community Service Districts",
                          "Fire District", "Humboldt County Zoning"]:
            checkbox = QCheckBox(file_name)
            checkbox.setChecked(initial_status.get(file_name, False) if initial_status else False)
            layout.addWidget(checkbox)
            self.file_status[file_name] = checkbox

        spacer = QWidget()  # Create a spacer widget
        spacer.setFixedSize(1, 10)  # Set a fixed height for the spacer
        layout.addWidget(spacer)  # Add the spacer widget

        deselect_button = QPushButton("Deselect All")
        layout.addWidget(deselect_button)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

        deselect_button.clicked.connect(self.deselect_all_checkboxes)

    def deselect_all_checkboxes(self):
        for checkbox in self.file_status.values():
            checkbox.setChecked(False)


class HazardSelectionDialog(QDialog):
    def __init__(self, parent=None, initial_status=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.file_status = {}
        for file_name in ["Flood Zone", "Tsunami Inundation Zone", "Slope Stability (HUMBOLDT BAY)",
                          "Slope Stability (COUNTY)", "Alquist-Priolo Zones", "Liquefaction Zones",
                          "Wildland Fire Risk"]:
            checkbox = QCheckBox(file_name)
            checkbox.setChecked(initial_status.get(file_name, False) if initial_status else False)
            layout.addWidget(checkbox)
            self.file_status[file_name] = checkbox

        spacer = QWidget()  # Create a spacer widget
        spacer.setFixedSize(1, 10)  # Set a fixed height for the spacer
        layout.addWidget(spacer)  # Add the spacer widget

        deselect_button = QPushButton("Deselect All")
        layout.addWidget(deselect_button)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

        deselect_button.clicked.connect(self.deselect_all_checkboxes)

    def deselect_all_checkboxes(self):
        for checkbox in self.file_status.values():
            checkbox.setChecked(False)


class ClimateSelectionDialog(QDialog):
    def __init__(self, parent=None, initial_status=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.file_status = {}
        for file_name in ["Minimum Temperature", "Maximum Temperature", "Minimum Temperature (1981-2010)",
                          "Maximum Temperature (1981-2010)", "Annual Precipitation (1981-2010)", "Monthly "
                          "Precipitation - January (1981-2010)", "Monthly Precipitation - February (1981-2010)",
                          "Monthly Precipitation - March (1981-2010)", "Monthly Precipitation - "
                          "April (1981-2010)", "Monthly Precipitation - May (1981-2010)",
                          "Monthly Precipitation - June (1981-2010)", "Monthly Precipitation - July "
                          "(1981-2010)", "Monthly Precipitation - August (1981-2010)",
                          "Monthly Precipitation - September (1981-2010)", "Monthly Precipitation - "
                          "October (1981-2010)", "Monthly Precipitation - November (1981-2010)",
                          "Monthly Precipitation - December (1981-2010)"]:
            checkbox = QCheckBox(file_name)
            checkbox.setChecked(initial_status.get(file_name, False) if initial_status else False)
            layout.addWidget(checkbox)
            self.file_status[file_name] = checkbox

        spacer = QWidget()  # Create a spacer widget
        spacer.setFixedSize(1, 10)  # Set a fixed height for the spacer
        layout.addWidget(spacer)  # Add the spacer widget

        deselect_button = QPushButton("Deselect All")
        layout.addWidget(deselect_button)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

        deselect_button.clicked.connect(self.deselect_all_checkboxes)

    def deselect_all_checkboxes(self):
        for checkbox in self.file_status.values():
            checkbox.setChecked(False)


class SiteDataSelectionDialog(QDialog):
    def __init__(self, parent=None, initial_status=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.file_status = {}
        for file_name in ["Project Parcel", "Adjacent Parcels", "Surrounding Parcels", "Road Centerlines", "Streams",
                          "Site Contours"]:
            checkbox = QCheckBox(file_name)
            checkbox.setChecked(initial_status.get(file_name, True) if initial_status else True)
            layout.addWidget(checkbox)
            self.file_status[file_name] = checkbox

        spacer = QWidget()  # Create a spacer widget
        spacer.setFixedSize(1, 10)  # Set a fixed height for the spacer
        layout.addWidget(spacer)  # Add the spacer widget

        deselect_button = QPushButton("Deselect All")
        layout.addWidget(deselect_button)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

        deselect_button.clicked.connect(self.deselect_all_checkboxes)

    def deselect_all_checkboxes(self):
        for checkbox in self.file_status.values():
            checkbox.setChecked(False)


class RasterSelectionDialog(QDialog):
    def __init__(self, parent=None, initial_status=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.file_status = {}
        for file_name in ["Google Earth Aerial", "2022 NAIP Aerial", "Digital Elevation Model Raster",
                          "Slope Raster"]:
            checkbox = QCheckBox(file_name)
            checkbox.setChecked(initial_status.get(file_name, True) if initial_status else True)
            layout.addWidget(checkbox)
            self.file_status[file_name] = checkbox

        spacer = QWidget()  # Create a spacer widget
        spacer.setFixedSize(1, 10)  # Set a fixed height for the spacer
        layout.addWidget(spacer)  # Add the spacer widget

        deselect_button = QPushButton("Deselect All")
        layout.addWidget(deselect_button)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

        deselect_button.clicked.connect(self.deselect_all_checkboxes)

    def deselect_all_checkboxes(self):
        for checkbox in self.file_status.values():
            checkbox.setChecked(False)


class CustomInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowModality(Qt.NonModal)

        self.setWindowTitle("Omsberg & Preston: Project Creator and Geospatial Data Extractor")
        self.file_dialog = None
        self.canceled = False

        layout = QVBoxLayout()

        self.input_widget = CustomInputWidget(self)
        layout.addWidget(self.input_widget)

        # Add spacer for vertical spacing above OK and Cancel buttons
        spacer = QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addSpacerItem(spacer)

        # Add OK and Cancel buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

    def accept(self):
        global apn_list, multiple_apn, yes_input1, raw_apn
        if not multiple_apn:
            current_text = self.input_widget.input1.text()  # Pull from input1
            raw_apn = [current_text]
            raw_apn, is_apn = APNDialog.apn_verify(raw_apn)
            apn_list = raw_apn
            yes_input1 = False

            if is_apn:
                # APNDialog.verify_contiguous(raw_apn)
                yes_input1 = True
            else:
                return

        proj_pattern = r'^\d{4}$|^\d{4}-\d{1,2}$|^\d{3}-\d{1,2}$'

        input_widgets = {
            'input2': ('Invalid Input: Please enter client name', None),
            'input3': ('Invalid Input: Please enter project number', proj_pattern)
        }

        if not multiple_apn:
            input_widgets['input1'] = ('Invalid Input: Please enter project APN', None)

        for widget_name, (error_message, pattern) in input_widgets.items():
            widget_text = getattr(self.input_widget, widget_name).text()

            if not widget_text:
                QMessageBox.critical(self, 'Error', error_message)
                return

            if pattern and not re.match(pattern, widget_text):
                QMessageBox.critical(None, 'ERROR',
                                     'Invalid input format. Please check the entered client and project number.')
                return

        super().accept()


    def reject(self):
        self.canceled = True
        super().reject()

    def get_parameters(self):
        params = {
            'apn_list': apn_list,
            'proj_name': self.input_widget.input2.text(),
            'proj_num': self.input_widget.input3.text(),
            'proj_type': self.input_widget.checkBox1.isChecked(),
            'proj_test': self.input_widget.checkBox2.isChecked(),
            'dxf_choice': self.input_widget.checkBox3.isChecked(),
            'map_choice': self.input_widget.checkBox4.isChecked(),
            'folder_choice': self.input_widget.checkBox5.isChecked(),
            'road_choice': self.input_widget.checkBox6.isChecked(),
            'buffer_radius': int(self.input_widget.buffer_radius_input.text()),
            'buffer_parcels': int(self.input_widget.buffer_parcels_input.text()),
            'buffer_dem': int(self.input_widget.buffer_dem_input.text())
        }
        return params


class ProgressWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Processing...")

        layout = QVBoxLayout()

        # Add a QLabel for messages
        self.message_label = QLabel(self)
        self.message_label.setStyleSheet("QLabel { color : black; font-weight : bold; }")

        layout.addWidget(self.message_label)

        # Add a QProgressBar
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

        # Create a QHBoxLayout for the Cancel button and spacer
        button_layout = QHBoxLayout()

        # Create a spacer item
        spacer = QSpacerItem(0, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        # Add the spacer and the Cancel button to the QHBoxLayout
        button_layout.addItem(spacer)
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.setFixedSize(80, 40)  # Set button size
        self.cancel_button.clicked.connect(self.confirm_cancel)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.resize(100, 100)

        # Create a QTimer inside the ProgressWindow
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.update_progress_bar)

        self.value = 0
        # self.progress_bar.setValue(self.value)

    def start_timer(self):
        # self.timer.start(1500)  # Update every 1.5 seconds
        pass

    def stop_timer(self):
        # self.timer.stop()
        pass

    def update_progress_bar(self):
        QgsMessageLog.logMessage(f"Progress window updated to {self.value}")

        # Increment the progress bar's value by 3%
        self.value += 3
        if self.value <= 99:
            self.progress_bar.setValue(self.value)
            QApplication.processEvents()
        else:
            # If the progress is complete, set it to 100 and stop the timer
            self.progress_bar.setValue(99)
            self.timer.stop()

    def set_progress(self, value):
        """Update the progress bar with the given value (0-100)"""
        try:
            self.progress_bar.setValue(value)
        except RuntimeError as e:
            print(f"Caught exception: {e}")

    def show_message(self, message):
        """Display a message in the progress window"""
        self.message_label.setText(message)

    def confirm_cancel(self):
        QApplication.processEvents()
        reply = QMessageBox.question(self, 'Confirmation', 'Are you sure you want to cancel?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.close()


class FinalDialog(QDialog):
    # Define the signal at the class level
    showFinalSignal = pyqtSignal(str)

    def __init__(self, parent=iface.mainWindow()):
        super().__init__(parent)  # Make sure to call the super class initializer
        self.parent = parent
        # Connect the signal to the slot within the class
        self.showFinalSignal.connect(self.show_final)

    def show_final(self, prj_folder):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Geospatial data processing completed.\nProject file has been created.")
        msgBox.setInformativeText(f"Project data has been extracted and saved to:\n{prj_folder}")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.setWindowTitle("Geospatial Data Extraction Complete.")

        # Get the QGIS main window
        qgis_main_window = self.parent if self.parent else QApplication.activeWindow()

        if qgis_main_window:
            # Determine the screen where the QGIS main window is located
            screen = QApplication.screenAt(qgis_main_window.frameGeometry().center())
        else:
            # If no active QGIS window, use the primary screen
            screen = QApplication.primaryScreen()

        # Calculate the center position relative to the screen
        screen_rect = screen.geometry()
        msg_box_rect = msgBox.rect()
        center_pos = screen_rect.center() - msg_box_rect.center()

        # Move the message box to the center of the screen
        msgBox.move(center_pos.x() - msgBox.width() // 2, center_pos.y() - msgBox.height() // 2)

        msgBox.exec_()
