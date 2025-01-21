import datetime
import posixpath

from qtpy.QtCore import QCoreApplication, Qt
from qtpy.QtWidgets import (
    QDockWidget,
    QFormLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

local_tz = datetime.datetime.now().astimezone().tzinfo


def sizeof_fmt(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


class DetailDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFeatures(
            QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable
        )
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.group_detail = QGroupBox(
            QCoreApplication.translate("detail", "File Details")
        )
        self.content_layout.addWidget(self.group_detail)
        self.layout_detail = QFormLayout(self.group_detail)
        self.filename = QLabel(self)
        self.filename.setWordWrap(True)
        self.filename.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.replicas = QLabel(self)
        self.replicas.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.coll = QLabel(self)
        self.coll.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.size = QLabel(self)
        self.size.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.create_time = QLabel(self)
        self.create_time.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.modify_time = QLabel(self)
        self.modify_time.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.download_button = QPushButton(
            QCoreApplication.translate("detail", "Download")
        )
        self.download_button.clicked.connect(parent.download)

        self.open_button = QPushButton(QCoreApplication.translate("detail", "Open"))
        self.open_button.clicked.connect(self.open_file)

        self.layout_detail.addRow(
            QCoreApplication.translate("detail", "File: "), self.filename
        )
        self.layout_detail.addRow(
            QCoreApplication.translate("detail", "Replicas: "), self.replicas
        )
        self.layout_detail.addRow(
            QCoreApplication.translate("detail", "Collection: "), self.coll
        )
        self.layout_detail.addRow(
            QCoreApplication.translate("detail", "Creation time: "), self.create_time
        )
        self.layout_detail.addRow(
            QCoreApplication.translate("detail", "Modified time: "), self.modify_time
        )
        self.layout_detail.addRow(
            QCoreApplication.translate("detail", "Size: "), self.size
        )
        self.layout_detail.addRow(self.open_button)
        self.layout_detail.addRow(self.download_button)
        self.setWidget(self.content)

    def open_file(self):
        self.parent().open_file(
            posixpath.join(self.parent().path, self.filename.text())
        )

    def update_info(self, filename, data) -> None:
        """
        Update the information of the detail dock with the selected file.
        Parameters
        ----------
        filename: str
            The name of the file.
        data: iRODSDataObject
            The irods data object.

        Returns
        -------
        None
        """
        replicas = data.replicas
        coll = data.collection
        size = data.size
        create_time = data.create_time
        modify_time = data.modify_time

        self.filename.setText(filename)
        self.filename.adjustSize()
        self.replicas.setText(";".join([str(s.resource_name) for s in replicas]))
        self.coll.setText(coll.name)
        self.size.setText(sizeof_fmt(size))
        self.create_time.setText(create_time.astimezone(local_tz).strftime("%c %z"))
        self.modify_time.setText(modify_time.astimezone(local_tz).strftime("%c %z"))
