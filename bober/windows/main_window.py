from abc import abstractmethod

from qtpy.QtCore import QPoint, QRect, Qt
from qtpy.QtGui import QCursor, QGuiApplication, QScreen
from qtpy.QtWidgets import QMainWindow, QMenuBar, QStatusBar


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
        global_mouse_pos = QCursor.pos()
        mouse_screen = QGuiApplication.screenAt(global_mouse_pos)

        sr = QScreen.availableGeometry(mouse_screen)
        frame_rect = QRect(QPoint(), self.frameSize().boundedTo(sr.size()))

        self.move(sr.center() - frame_rect.center())

    def set_status_bar_message(self, message: str, msecs=0) -> None:
        """
        Sets a message in the Status bar for the designated amount of time.
        Returns
        -------
        None
        """
        self.statusbar.showMessage(message, msecs)

    @abstractmethod
    def help(self):
        pass

    @staticmethod
    @abstractmethod
    def about():
        pass

    def keyPressEvent(self, event, **kwargs):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
