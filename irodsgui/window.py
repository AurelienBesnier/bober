from qtpy.QtGui import QKeySequence
from qtpy.QtWidgets import QAction, QMenu, QStyle, QTabWidget, QListWidget, \
    QMessageBox

from irodsgui.main_window import MainWindow
from irodsgui.settings_window import SettingsWindow


class Window(MainWindow):

    def __init__(self):
        super().__init__()
        self.center()
        self.resize(1280, 720)
        self.setStatusBar(self.statusbar)
        # Widgets
        self.tabWidget = QTabWidget(self)
        self.listWidget = QListWidget(self)
        self.tabWidget.addTab(self.listWidget, "Explorer")
        self.settings_window = SettingsWindow(None)

        self.setupMenus()
        self.setCentralWidget(self.tabWidget)
        self.setStatusBarMessage("Application Started", 5000)

    def login(self):
        pass

    def setupList(self):
        pass

    def editSettings(self):
        self.settings_window.show()

    def setupMenus(self):
        quitIcon = self.style().standardIcon(
            QStyle.StandardPixmap.SP_BrowserStop)
        loginIcon = self.style().standardIcon(
            QStyle.StandardPixmap.SP_ComputerIcon)
        qtIcon = self.style().standardIcon(
            QStyle.StandardPixmap.SP_TitleBarMenuButton)
        # File Menu
        fileMenu = QMenu("File", self)
        quitAction = QAction(quitIcon, "Quit", self)
        quitAction.triggered.connect(self.close)
        quitAction.setShortcut(QKeySequence.StandardKey.Quit)

        loginAction = QAction(loginIcon, "Login", self)
        loginAction.triggered.connect(self.login)
        fileMenu.addAction(loginAction)
        fileMenu.addSeparator()
        fileMenu.addAction(quitAction)

        # Edit Menu
        editMenu = QMenu("Edit", self)
        settingsAction = QAction("Settings...", self)
        settingsAction.triggered.connect(self.editSettings)
        editMenu.addAction(settingsAction)


        # About/Help Menu
        aboutMenu = QMenu("About", self)
        aboutAction = QAction("About", self)
        aboutAction.triggered.connect(self.about)
        aboutQtAction = QAction(qtIcon, "About Qt", self)
        aboutQtAction.triggered.connect(
            lambda: QMessageBox.aboutQt(self, "About Qt"))
        aboutMenu.addAction(aboutAction)
        aboutMenu.addAction(aboutQtAction)

        # Add everything
        self.menubar.addAction(fileMenu.menuAction())
        self.menubar.addAction(editMenu.menuAction())
        self.menubar.addAction(aboutMenu.menuAction())

    @staticmethod
    def help():
        pass

    @staticmethod
    def about():
        pass
