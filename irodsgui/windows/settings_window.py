import json
import irodsgui.globals as glob
from qtpy.QtGui import QIntValidator
from qtpy.QtCore import Qt, QSettings, QStandardPaths
from qtpy.QtWidgets import QWidget, QGridLayout, QLineEdit, QPushButton, \
    QLabel, QFileDialog


class SettingsWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.settings = QSettings()
        self.setWindowTitle(f"{glob.app_name} - Settings")
        self.layout = QGridLayout(self)
        self.cfgLabel = QLabel("Config path:")
        self.cfgEdit = QLineEdit()
        self.hostLabel = QLabel("Host:")
        self.hostEdit = QLineEdit()
        self.portLabel = QLabel("Port:")
        self.portEdit = QLineEdit()
        self.portEdit.setValidator(QIntValidator(0, 9999999))

        self.zoneLabel = QLabel("Zone:")
        self.zoneEdit = QLineEdit()
        self.rootLabel = QLabel("Root path:")
        self.rootEdit = QLineEdit()
        self.config_location = self.settings.value('config_path',
                                                   defaultValue='')
        self.host = self.settings.value('host', defaultValue='')
        self.port = self.settings.value('port', defaultValue='')
        self.zone = self.settings.value('zone', defaultValue='')
        self.rootPath = self.settings.value('root_path', defaultValue='/')

        self.cfgEdit.setText(self.config_location)
        self.cfgButton = QPushButton("...")
        self.cfgButton.clicked.connect(self.select_cfg)

        self.hostEdit.setText(self.host)
        self.portEdit.setText(self.port)
        self.zoneEdit.setText(self.zone)
        self.rootEdit.setText(self.rootPath)

        self.saveButton = QPushButton("Save")
        self.saveButton.clicked.connect(self.save)

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.close)

        # Adding Widgets
        self.layout.addWidget(self.cfgLabel, 0, 0)
        self.layout.addWidget(self.cfgEdit, 0, 1)
        self.layout.addWidget(self.cfgButton, 0, 2)

        self.layout.addWidget(self.hostLabel, 1, 0)
        self.layout.addWidget(self.hostEdit, 1, 1, 1, 2)

        self.layout.addWidget(self.portLabel, 2, 0)
        self.layout.addWidget(self.portEdit, 2, 1, 1, 2)

        self.layout.addWidget(self.zoneLabel, 3, 0)
        self.layout.addWidget(self.zoneEdit, 3, 1, 1, 2)

        self.layout.addWidget(self.rootLabel, 4, 0)
        self.layout.addWidget(self.rootEdit, 4, 1, 1, 2)

        self.layout.addWidget(self.saveButton, 5, 0)
        self.layout.addWidget(self.cancelButton, 5, 1, 1, 2)

    def select_cfg(self) -> None:
        """
        Select the irods configuration file and parse it.
        """
        home_folder = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.HomeLocation)
        print(home_folder)
        self.config_location = QFileDialog.getOpenFileUrl(self,
                                                          "Select irods "
                                                          "configuration",
                                                          dir=home_folder,
                                                          filter="config files (*.json)")[
            0].toLocalFile()
        print(self.config_location)

        if self.config_location == "":
            return
        self.cfgEdit.setText(self.config_location)
        self.parse_config()

    def parse_config(self) -> None:
        """
        Parse the configuration file and set the line edits with the info in it.
        """
        with open(self.config_location, 'r') as f:
            data = json.load(f)
            self.port = data['irods_port']
            self.host = data['irods_host']
            self.zone = data['irods_zone_name']
            self.rootPath = data['irods_home']

            self.hostEdit.setText(self.host)
            self.portEdit.setText(str(self.port))
            self.zoneEdit.setText(self.zone)
            self.rootEdit.setText(self.rootPath)

    def save(self) -> None:
        """
        Sets the Qt application settings values to the values of the line edits.
        Returns
        -------
        None
        """
        self.settings.setValue("config_path", self.config_location)
        self.settings.setValue("port", self.portEdit.text())
        self.settings.setValue("host", self.hostEdit.text())
        self.settings.setValue("zone", self.zoneEdit.text())
        self.settings.setValue("root_path", self.rootEdit.text())
        self.close()

    def keyPressEvent(self, event, **kwargs):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
