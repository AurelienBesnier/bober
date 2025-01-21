import os
import sys

from qtpy.QtCore import QCoreApplication, QLocale, QSettings, QTranslator
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QApplication

import bober.globals as glob
from bober.utils import assets_folder
from bober.version import __version__
from bober.windows.window import Window


def quit_application():
    print(QCoreApplication.translate("main", "Quitting application"))
    sys.exit(app.exit())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.join(assets_folder(), "icon.ico")))
    app.setOrganizationName(glob.app_name)
    app.setApplicationName(glob.app_name)
    app.setApplicationVersion(__version__)
    settings = QSettings()
    user_locale = str(settings.value("locale", defaultValue=""))
    translator = QTranslator()
    locale = QLocale(user_locale) if user_locale != "" else QLocale()
    if translator.load(locale, "", "", str(assets_folder() / "i18n")):
        QCoreApplication.installTranslator(translator)
    win = Window()
    win.show()

    app.setQuitOnLastWindowClosed(True)
    app.lastWindowClosed.connect(quit_application)
    app.exec()
