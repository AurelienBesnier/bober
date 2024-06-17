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
        self.layoutDetail.addRow("File name: ", self.filename)
        self.setWidget(self.content)

    def updateInfo(self, filename):
        self.filename.setText(filename)
        self.filename.adjustSize()
