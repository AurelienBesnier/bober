from qtpy.QtWidgets import QWidget, QDockWidget, QGroupBox, QFormLayout, \
    QLabel, QVBoxLayout
from qtpy.QtCore import Qt


class DetailDock(QDockWidget):
    def __init__(self):
        super().__init__()
        self.setFeatures(QDockWidget.DockWidgetMovable |
                         QDockWidget.DockWidgetFloatable)
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.group_detail = QGroupBox("File Details")
        self.content_layout.addWidget(self.group_detail)
        self.layout_detail = QFormLayout(self.group_detail)
        self.filename = QLabel(self)
        self.filename.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.replicas = QLabel(self)
        self.replicas.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.coll = QLabel(self)
        self.coll.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.layout_detail.addRow("File name: ", self.filename)
        self.layout_detail.addRow("Replicas: ", self.replicas)
        self.layout_detail.addRow("Collection: ", self.coll)
        self.setWidget(self.content)

    def update_info(self, filename, replicas, coll) -> None:
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

        Returns
        -------
        None
        """
        self.filename.setText(filename)
        self.replicas.setText(";".join([str(s.resource_name) for s in replicas]))
        self.coll.setText(coll.name)
