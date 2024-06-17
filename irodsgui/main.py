import sys

from qtpy.QtCore import QSettings
from qtpy.QtWidgets import QApplication

from irodsgui.window import Window
from irodsgui.version import __version__


def quit_application():
    print("Quitting application")
    sys.exit(app.exit())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setOrganizationName("IrodsGui")
    app.setApplicationName("IrodsGui")
    app.setApplicationVersion(__version__)
    settings = QSettings()
    win = Window()
    win.show()

    app.setQuitOnLastWindowClosed(True)
    app.lastWindowClosed.connect(quit_application)
    app.exec()
