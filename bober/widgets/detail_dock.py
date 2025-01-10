from qtpy.QtCore import Qt
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
        self.group_detail = QGroupBox("File Details")
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
        self.create_time.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self.layout_detail.addRow("File name: ", self.filename)
        self.layout_detail.addRow("Replicas: ", self.replicas)
        self.layout_detail.addRow("Collection: ", self.coll)
        self.layout_detail.addRow("Creation time: ", self.create_time)
        self.layout_detail.addRow("Size: ", self.size)
        self.setWidget(self.content)

    def update_info(self, filename, replicas, coll, size, create_time) -> None:
        """
        Update the information of the detail dock with the selected file.
        Parameters
        ----------
        filename: str
            The name of the file.
        replicas: list
            The replicas where the file can be found.
        coll: iRODSCollection
            The collection where the file is.
        size: int
            The size of the file in bits.
        create_time: date
            The date of the creation of the file.

        Returns
        -------
        None
        """
        self.filename.setText(filename)
        self.replicas.setText(";".join([str(s.resource_name) for s in replicas]))
        self.coll.setText(coll.name)
        self.size.setText(sizeof_fmt(size))
        self.create_time.setText(create_time.astimezone(local_tz).strftime("%c %z"))
