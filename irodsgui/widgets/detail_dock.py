from qtpy.QtWidgets import QWidget, QDockWidget, QGroupBox, QFormLayout, \
    QLabel, QVBoxLayout
from qtpy.QtCore import Qt


class DetailDock(QDockWidget):
    def __init__(self):
        super().__init__()
        self.setFeatures(QDockWidget.DockWidgetMovable |
                         QDockWidget.DockWidgetFloatable)
        self.content = QWidget()
        self.contentLayout = QVBoxLayout(self.content)
        self.groupDetail = QGroupBox("File Details")
        self.contentLayout.addWidget(self.groupDetail)
        self.layoutDetail = QFormLayout(self.groupDetail)
        self.filename = QLabel(self)
        self.filename.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.replicas = QLabel(self)
        self.replicas.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.coll = QLabel(self)
        self.coll.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.layoutDetail.addRow("File name: ", self.filename)
        self.layoutDetail.addRow("Replicas: ", self.replicas)
        self.layoutDetail.addRow("Collection: ", self.coll)
        self.setWidget(self.content)

    def update_info(self, filename, replicas, coll):
        self.filename.setText(filename)
        self.replicas.setText(";".join([str(s.resource_name) for s in replicas]))
        self.coll.setText(coll.name)
