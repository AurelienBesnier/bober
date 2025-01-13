from qtpy.QtWidgets import (
    QDockWidget,
    QFormLayout,
    QLabel,
    QProgressBar,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from qtpy.QtCore import QCoreApplication


class ProgressDock(QDockWidget):
    def __init__(self):
        super().__init__()
        self.setFeatures(
            QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable
        )
        self.content = QWidget()
        self.scroll_area = QScrollArea()
        self.content_layout = QVBoxLayout(self.content)

        self.group_wdg = QWidget()
        self.layout_progress = QFormLayout(self.group_wdg)
        self.scroll_area.setWidget(self.group_wdg)
        self.scroll_area.setWidgetResizable(True)
        # self.groupWdg.resize(500, 100)

        self.content_layout.addWidget(QLabel(QCoreApplication.translate("progress", "Download progress")))
        self.content_layout.addWidget(self.scroll_area)

        self.setWidget(self.content)
        self.content.show()

    def add_download(self, target, size) -> QProgressBar:
        """
        Add a download progression progress_bar for the given target.
        Parameters
        ----------
        target: str
            The name of the target.
        size: int
            The size of the download target in number of files in it.

        Returns
        -------
        None
        """
        progress_bar = QProgressBar()
        progress_bar.setMaximum(size)
        self.layout_progress.addRow(target, progress_bar)
        return progress_bar

    def delete_row(self, item) -> None:
        """
        Remove an item from the list.
        Parameters
        ----------
        item: str
            The item's name.

        Returns
        -------
        None
        """
        for i in range(self.layout_progress.rowCount()):
            try:
                if (
                    self.layout_progress.itemAt(i, QFormLayout.ItemRole.LabelRole)
                    .widget()
                    .text()
                    == item
                ):
                    self.layout_progress.removeRow(i)
                if self.layout_progress.rowCount() == 0:
                    self.hide()
            except AttributeError:
                pass
