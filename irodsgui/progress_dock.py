from qtpy.QtWidgets import QWidget, QDockWidget, QFormLayout, \
    QVBoxLayout, QProgressBar, QScrollArea, QLabel


class ProgressDock(QDockWidget):
    def __init__(self):
        super().__init__()
        self.setFeatures(QDockWidget.DockWidgetMovable |
                         QDockWidget.DockWidgetFloatable)
        self.content = QWidget()
        self.scrollArea = QScrollArea()
        self.contentLayout = QVBoxLayout(self.content)

        self.groupWdg = QWidget()
        self.layoutProgress = QFormLayout(self.groupWdg)
        self.scrollArea.setWidget(self.groupWdg)
        self.scrollArea.setWidgetResizable(True)
        # self.groupWdg.resize(500, 100)

        self.contentLayout.addWidget(QLabel("Download progress"))
        self.contentLayout.addWidget(self.scrollArea)

        self.setWidget(self.content)
        self.content.show()

    def addDownload(self, target, size):
        bar = QProgressBar()
        bar.setMaximum(size)
        self.layoutProgress.addRow(target, bar)
        return bar

    def deleteRow(self, item):
        for i in range(self.layoutProgress.rowCount()):
            try:
                if self.layoutProgress.itemAt(i, QFormLayout.ItemRole.LabelRole).widget().text() == item:
                    self.layoutProgress.removeRow(i)
            except AttributeError:
                pass
