from abc import abstractmethod

from qtpy.QtCore import QRect, QPoint, Qt
from qtpy.QtGui import QScreen, QCursor, QGuiApplication
from qtpy.QtWidgets import QMainWindow, QStatusBar, QMenuBar


class MainWindow(QMainWindow):
    """
    The abstract class representing the main windows of the application.
    """

    def __init__(self):
        super().__init__(parent=None)
        self.statusbar: QStatusBar = QStatusBar(self)
        self.menubar = QMenuBar(self)
        self.setMenuBar(self.menubar)

    def center(self) -> None:
        """
        Centers the window on the screen.
        Returns
        -------
        None
        """
        # Get the screen where the mouse is
        globalMousePos = QCursor.pos()
        mouseScreen = QGuiApplication.screenAt(globalMousePos)

        sr = QScreen.availableGeometry(mouseScreen)
        frameRect = QRect(QPoint(), self.frameSize().boundedTo(sr.size()))

        self.move(sr.center() - frameRect.center())

    def setStatusBarMessage(self, message: str, msecs=0) -> None:
        self.statusbar.showMessage(message, msecs)

    @staticmethod
    @abstractmethod
    def help():
        pass

    @staticmethod
    @abstractmethod
    def about():
        pass

    def keyPressEvent(self, event, **kwargs):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
