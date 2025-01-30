from qtpy.QtCore import QCoreApplication, QSettings
from qtpy.QtWidgets import QDialog, QFormLayout, QComboBox, QLabel, QPushButton


class UploadDialog(QDialog):
    def __init__(self, parent=None, list_replica=None):
        super().__init__(parent=parent)
        if list_replica is None:
            list_replica = list()

        self.settings = QSettings()
        default = str(self.settings.value("default_resc", defaultValue=""))

        self.upload_layout = QFormLayout(self)
        self.replica_upload_box = QComboBox(self)
        self.replica_upload_box.addItems(list_replica)
        if default != "":
            idx = self.replica_upload_box.findText(default)
            self.replica_upload_box.setCurrentIndex(idx)

        self.confirm_button = QPushButton(
            QCoreApplication.translate("widget", "Confirm")
        )
        self.confirm_button.clicked.connect(self.confirm)
        self.upload_layout.addRow(
            QLabel(QCoreApplication.translate("widget", "Replica") + ": "),
            self.replica_upload_box,
        )
        self.upload_layout.addRow(self.confirm_button)

    def confirm(self):
        self.settings.setValue("default_resc", self.replica_upload_box.currentText())
        self.accept()
