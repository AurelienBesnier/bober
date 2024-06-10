from qtpy.QtCore import Qt, QSettings
from qtpy.QtWidgets import QWidget, QGridLayout, QLineEdit, QPushButton, \
    QLabel, QFileDialog


class SettingsWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.settings = QSettings()
        self.setWindowTitle("IrodsGui - Settings")
        self.layout = QGridLayout(self)
        self.cfgLabel = QLabel("Config path:")
        self.cfgEdit = QLineEdit()
        self.config_location = self.settings.value('config_path',
                                                   defaultValue='')
        self.cfgEdit.setText(self.config_location)
        self.cfgButton = QPushButton("...")
        self.cfgButton.clicked.connect(self.selectCfg)

        self.saveButton = QPushButton("Save")
        self.saveButton.clicked.connect(self.save)

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.close)

        # Adding Widgets
        self.layout.addWidget(self.cfgLabel, 0, 0)
        self.layout.addWidget(self.cfgEdit, 0, 1)
        self.layout.addWidget(self.cfgButton, 0, 2)
        self.layout.addWidget(self.saveButton, 1, 0)
        self.layout.addWidget(self.cancelButton, 1, 1)

    def selectCfg(self):
        config_location = str(QFileDialog.getOpenFileUrl(self,
                                                         "Select irods "
                                                         "configuration",
                                                         filter="config files (*.json)",
                                                         options=QFileDialog.Option.DontUseNativeDialog)[0])
        print(config_location)
        if config_location == "":
            return
        else:
            self.config_location = self.settings.setValue("config_path",
                                                          config_location)
            self.cfgEdit.setText(self.config_location)

    def save(self):
        self.settings.setValue("config_path", self.config_location)
        self.close()

    def keyPressEvent(self, event, **kwargs):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
