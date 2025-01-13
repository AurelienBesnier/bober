from qtpy.QtCore import Qt, QCoreApplication
from qtpy.QtWidgets import (
    QDockWidget,
    QFormLayout,
    QGroupBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)


import datetime

local_tz = datetime.datetime.now().astimezone().tzinfo


def sizeof_fmt(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


class DetailDock(QDockWidget):
    def __init__(self):
        super().__init__()
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
        self.setWidget(self.content)

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
        self.replicas.setText(";".join([str(s.resource_name) for s in replicas]))
        self.coll.setText(coll.name)
        self.size.setText(sizeof_fmt(size))
        self.create_time.setText(create_time.astimezone(local_tz).strftime("%c %z"))
        self.modify_time.setText(modify_time.astimezone(local_tz).strftime("%c %z"))
