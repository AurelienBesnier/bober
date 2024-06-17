import sys
import os

from qtpy.QtCore import Qt, QSettings, QUrl, QStandardPaths
from qtpy.QtGui import QKeySequence, QDesktopServices
from qtpy.QtWidgets import QAction, QMenu, QStyle, QTabWidget, QListWidget, \
    QMessageBox, QDialog, QListWidgetItem

from irodsgui.detail_dock import DetailDock
from irodsgui.login_window import LoginWindow
from irodsgui.main_window import MainWindow
from irodsgui.settings_window import SettingsWindow
from irodsgui.version import __version__
from irods.exception import OVERWRITE_WITHOUT_FORCE_FLAG
import irodsgui.globals as glob


class Window(MainWindow):

    def __init__(self):
        super().__init__()
        self.resize(1280, 720)
        self.center()
        self.setStatusBar(self.statusbar)

        # Main Widgets
        self.tabWidget = QTabWidget(self)
        self.listWidget = QListWidget(self)
        self.listWidget.itemClicked.connect(self.detailItem)
        self.listWidget.itemDoubleClicked.connect(self.onDoubleClick)
        self.tabWidget.addTab(self.listWidget, "Explorer")
        self.detailDock = DetailDock()

        # Sub Widgets
        self.settings_window = SettingsWindow(None)
        self.login_window = LoginWindow()
        self.settings = QSettings()

        # Vars
        self.root = ""
        self.path = ""
        self.folderIcon = self.style().standardIcon(
            QStyle.StandardPixmap.SP_DirIcon)
        self.fileIcon = self.style().standardIcon(
            QStyle.StandardPixmap.SP_FileLinkIcon)

        self.setupMenus()
        self.setCentralWidget(self.tabWidget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.detailDock)
        self.setStatusBarMessage("Application Started", 5000)

    def login(self):
        if self.login_window.exec() == QDialog.Accepted:
            self.setStatusBarMessage("logged in", 5000)
            self.root = self.settings.value('root_path')
            self.path = self.root

            dirs = [QListWidgetItem(self.folderIcon, '..')]
            files = []
            coll = glob.irods_session.collections.get(self.root)
            dirs.extend([QListWidgetItem(self.folderIcon, d.name)
                        for d in coll.subcollections])
            files.extend([QListWidgetItem(self.fileIcon, f.name, None, 1000)
                         for f in coll.data_objects])
            for directory in dirs:
                self.listWidget.addItem(directory)
            for file in files:
                self.listWidget.addItem(file)

            self.listWidget.sortItems()

    def detailItem(self, item):
        if item.type() != 0:
            self.detailDock.updateInfo(item.text())

    def onDoubleClick(self, item):
        if item.type() == 0:  # selected a folder
            self.path += '/' + item.text()
            self.path = os.path.normpath(self.path)
            self.changeFolder()
        else:  # selected a file
            # open file
            self.openFile(self.path+'/'+item.text())

    def changeFolder(self):
        self.setStatusBarMessage(self.path)
        self.listWidget.clear()

        dirs = [QListWidgetItem(self.folderIcon, '..')]
        files = []
        coll = glob.irods_session.collections.get(self.path)
        dirs.extend([QListWidgetItem(self.folderIcon, d.name)
                    for d in coll.subcollections])
        files.extend([QListWidgetItem(self.fileIcon, f.name, None, 1000)
                     for f in coll.data_objects])
        for directory in dirs:
            self.listWidget.addItem(directory)
        for file in files:
            self.listWidget.addItem(file)

        self.listWidget.sortItems()

    def openFile(self, filepath):
        print(f"opening file {filepath}")
        tmp_folder = os.path.join(str(QStandardPaths.writableLocation(QStandardPaths.TempLocation)),
                                  'irodsgui')
        os.makedirs(tmp_folder, exist_ok=True)
        local_path = os.path.join(tmp_folder, os.path.basename(filepath))
        try:
            glob.irods_session.data_objects.get(filepath, local_path=local_path)
            print(local_path)
        except OVERWRITE_WITHOUT_FORCE_FLAG:
            print("file already there")
        QDesktopServices.openUrl(QUrl('file://'+local_path))

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
        helpAction = QAction("Help", self)
        helpAction.triggered.connect(self.help)
        helpAction.setShortcut(QKeySequence.StandardKey.HelpContents)
        aboutAction = QAction("About", self)
        aboutAction.triggered.connect(self.about)
        aboutQtAction = QAction(qtIcon, "About Qt", self)
        aboutQtAction.triggered.connect(
            lambda: QMessageBox.aboutQt(self, "About Qt"))
        aboutMenu.addAction(helpAction)
        aboutMenu.addSeparator()
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
        msgBox = QMessageBox()
        msgBox.setWindowTitle('PhenXFlow - About')
        msgBox.setText(
            "<div style='text-align: center'>"
            "<h2>IrodsGui:</h2>"
            "<p>A Simple GUI to irods</p><br>"
            f"<p> version: {__version__}</p>"
            f"<p>Python version: {sys.version}</p>"
            "</div>"
        )
        msgBox.exec()
