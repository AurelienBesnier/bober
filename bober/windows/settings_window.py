import json

from PySide6.QtWidgets import QMessageBox
from qtpy.QtCore import QSettings, QStandardPaths, Qt, QCoreApplication
from qtpy.QtGui import QIntValidator
from qtpy.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
    QCheckBox,
    QComboBox,
)

import bober.globals as glob

locales = ['en_US', 'fr_FR', 'es_ES', 'de_DE', 'uk_UA', 'ru_RU']

class SettingsWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.settings = QSettings()
        self.setWindowTitle(
            f"{glob.app_name} - " + QCoreApplication.translate("settings", "Settings")
        )
        self.layout = QGridLayout(self)

        # Widgets
        self.cfg_label = QLabel(QCoreApplication.translate("settings", "Config path:"))
        self.cfg_edit = QLineEdit()
        self.host_label = QLabel(QCoreApplication.translate("settings", "Host:"))
        self.host_edit = QLineEdit()
        self.port_label = QLabel(QCoreApplication.translate("settings", "Port:"))
        self.port_edit = QLineEdit()
        self.port_edit.setValidator(QIntValidator(0, 9999999))
        self.zone_label = QLabel(QCoreApplication.translate("settings", "Zone:"))
        self.zone_edit = QLineEdit()
        self.root_label = QLabel(QCoreApplication.translate("settings", "Root path:"))
        self.root_edit = QLineEdit()
        self.notification_label = QLabel(
            QCoreApplication.translate("settings", "Download notifications:")
        )
        self.notification_check = QCheckBox()

        self.locale_label = QLabel(QCoreApplication.translate("settings", "Locale:"))
        self.locale_box = QComboBox()
        self.locale_box.addItems(locales)

        # Settings
        self.config_location = self.settings.value("config_path", defaultValue="")
        self.host = self.settings.value("host", defaultValue="")
        self.port = self.settings.value("port", defaultValue="")
        self.zone = self.settings.value("zone", defaultValue="")
        self.root_path = self.settings.value("root_path", defaultValue="/")
        self.notifications = self.settings.value("notifications", defaultValue="true")

        self.cfg_edit.setText(self.config_location.__str__())
        self.cfg_button = QPushButton("...")
        self.cfg_button.clicked.connect(self.select_cfg)

        self.host_edit.setText(self.host.__str__())
        self.port_edit.setText(self.port.__str__())
        self.zone_edit.setText(self.zone.__str__())
        self.root_edit.setText(self.root_path.__str__())
        if self.notifications == "false":
            self.notification_check.setChecked(False)
        elif self.notifications == "true":
            self.notification_check.setChecked(True)

        self.save_button = QPushButton(QCoreApplication.translate("settings", "Save"))
        self.save_button.clicked.connect(self.save)

        self.cancel_button = QPushButton(
            QCoreApplication.translate("settings", "Cancel")
        )
        self.cancel_button.clicked.connect(self.close)

        # Adding Widgets
        self.layout.addWidget(self.cfg_label, 0, 0)
        self.layout.addWidget(self.cfg_edit, 0, 1)
        self.layout.addWidget(self.cfg_button, 0, 2)

        self.layout.addWidget(self.host_label, 1, 0)
        self.layout.addWidget(self.host_edit, 1, 1, 1, 2)

        self.layout.addWidget(self.port_label, 2, 0)
        self.layout.addWidget(self.port_edit, 2, 1, 1, 2)

        self.layout.addWidget(self.zone_label, 3, 0)
        self.layout.addWidget(self.zone_edit, 3, 1, 1, 2)

        self.layout.addWidget(self.root_label, 4, 0)
        self.layout.addWidget(self.root_edit, 4, 1, 1, 2)

        self.layout.addWidget(self.notification_label, 5, 0)
        self.layout.addWidget(self.notification_check, 5, 1, 1, 2)

        self.layout.addWidget(self.locale_label, 6, 0)
        self.layout.addWidget(self.locale_box, 6, 1, 1, 2)

        self.layout.addWidget(self.save_button, 7, 0)
        self.layout.addWidget(self.cancel_button, 7, 1, 1, 2)

    def select_cfg(self) -> None:
        """
        Select the irods configuration file and parse it.
        """
        home_folder = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.HomeLocation
        )
        print(home_folder)
        self.config_location = QFileDialog.getOpenFileUrl(
            self,
            QCoreApplication.translate("settings", "Select irods configuration"),
            dir=home_folder,
            filter="config files (*.json)",
        )[0].toLocalFile()
        print(self.config_location)

        if self.config_location == "":
            return
        self.cfg_edit.setText(self.config_location)
        self.parse_config()

    def parse_config(self) -> None:
        """
        Parse the configuration file and set the line edits with the info in it.
        """
        with open(self.config_location.__str__(), "r", encoding="UTF8") as f:
            data = json.load(f)
            self.port = data["irods_port"]
            self.host = data["irods_host"]
            self.zone = data["irods_zone_name"]
            self.root_path = data["irods_home"]

            self.host_edit.setText(self.host)
            self.port_edit.setText(str(self.port))
            self.zone_edit.setText(self.zone)
            self.root_edit.setText(self.root_path)

    def save(self) -> None:
        """
        Sets the Qt application settings values to the values of the line edits.
        Returns
        -------
        None
        """
        self.settings.setValue("config_path", self.config_location)
        self.settings.setValue("port", self.port_edit.text())
        self.settings.setValue("host", self.host_edit.text())
        self.settings.setValue("zone", self.zone_edit.text())
        self.settings.setValue("root_path", self.root_edit.text())
        self.settings.setValue("notifications", self.notification_check.isChecked())
        if self.settings.value("locale") != self.locale_box.currentText():
            msgbox = QMessageBox()
            msgbox.setWindowTitle(QCoreApplication.translate("settings", "Settings"))
            msgbox.setText(QCoreApplication.translate("settings", "Please restart the application to change the localisation."))
            msgbox.setIcon(QMessageBox.Icon.Information)
            msgbox.exec()
        self.settings.setValue("locale", self.locale_box.currentText())

        self.close()

    def keyPressEvent(self, event, **kwargs):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
