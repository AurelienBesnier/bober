import sys
import os
import posixpath

from qtpy.QtCore import Qt, QSettings, QUrl, QStandardPaths
from qtpy.QtGui import QKeySequence, QDesktopServices
from qtpy.QtWidgets import QAction, QMenu, QStyle, QTabWidget, QListWidget, \
    QMessageBox, QDialog, QListWidgetItem, QWidget, QVBoxLayout, QLineEdit, \
    QToolBar, QPushButton, QFileDialog, QAbstractItemView, QSystemTrayIcon

import irodsgui.globals as glob
from irodsgui.widgets.detail_dock import DetailDock
from irodsgui.widgets.progress_dock import ProgressDock
from irodsgui.windows.login_window import LoginWindow
from irodsgui.windows.main_window import MainWindow
from irodsgui.windows.settings_window import SettingsWindow
from irodsgui.workers import DownloadThread
from irodsgui.version import __version__

from irods.exception import OVERWRITE_WITHOUT_FORCE_FLAG, \
    CAT_NO_ACCESS_PERMISSION
from irods.models import DataObject


class Window(MainWindow):

    def __init__(self):
        super().__init__()
        self.resize(1280, 720)
        self.center()
        self.setStatusBar(self.statusbar)

        # Main Widgets
        self.content = QWidget(self)
        self.contentLayout = QVBoxLayout(self.content)
        self.toolbar = QToolBar(self)
        self.backButton = QPushButton("Back", self)
        self.backButton.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_ArrowBack))
        self.backButton.clicked.connect(self.back_folder)
        self.searchBar = QLineEdit(self)
        self.searchBar.setPlaceholderText("Filter...")
        self.searchBar.textChanged.connect(lambda:
                                           self.change_filter(self.searchBar.text()))
        self.tabWidget = QTabWidget(self)
        self.toolbar.addWidget(self.backButton)
        self.toolbar.addWidget(self.searchBar)
        self.contentLayout.addWidget(self.toolbar)
        self.contentLayout.addWidget(self.tabWidget)
        self.listWidget = QListWidget(self)
        self.listWidget.currentItemChanged.connect(self.detail_item)
        self.listWidget.itemDoubleClicked.connect(self.on_double_click)
        self.listWidget.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tabWidget.addTab(self.listWidget, "Explorer")
        self.detailDock = DetailDock()
        self.detailDock.hide()
        self.progressDock = ProgressDock()
        self.progressDock.hide()

        # Sub Widgets
        self.settings_window = SettingsWindow(None)
        self.login_window = LoginWindow()
        self.settings = QSettings()
        self.menu = QMenu(self)
        self.trayicon = QSystemTrayIcon()

        # Vars
        self.root = ""
        self.path = ""
        self.details = []
        self.folderIcon = self.style().standardIcon(
            QStyle.StandardPixmap.SP_DirIcon)
        self.fileIcon = self.style().standardIcon(
            QStyle.StandardPixmap.SP_FileLinkIcon)
        self.threads = []

        self.trayicon.setIcon(self.fileIcon)
        self.trayicon.show()
        self.setup_menus()
        self.setCentralWidget(self.content)
        self.addDockWidget(
            Qt.DockWidgetArea.RightDockWidgetArea, self.detailDock)
        self.addDockWidget(
            Qt.DockWidgetArea.RightDockWidgetArea, self.progressDock)
        self.setStatusBarMessage("Application Started", 3000)

    def change_filter(self, pattern):
        for row in range(self.listWidget.count()):
            it = self.listWidget.item(row)
            if pattern:
                it.setHidden(not self.filter(pattern, it.text()))
            else:
                it.setHidden(False)

    @staticmethod
    def filter(text, keywords):
        return text in keywords

    def back_folder(self):
        if self.path:
            self.path = posixpath.dirname(self.path)
            self.change_folder()

    def login(self):
        if self.login_window.exec() == QDialog.Accepted:
            self.setStatusBarMessage("logged in", 5000)
            self.root = self.settings.value('root_path')
            self.path = self.root
            self.change_folder()

    def detail_item(self, item):
        try:
            if item.type() != 0:
                if self.detailDock.isHidden():
                    self.detailDock.show()
                print(posixpath.join(self.path, item.text()))
                meta = glob.irods_session.metadata.get(
                    DataObject, posixpath.join(self.path, item.text()))
                print(meta)
                data = glob.irods_session.data_objects.get(
                    posixpath.join(self.path, item.text()))
                self.detailDock.update_info(
                    item.text(), data.replicas, data.collection)
        except AttributeError as e:
            print(e)

    def on_double_click(self, item):
        if item.type() == 0:  # selected a folder
            self.path = posixpath.join(self.path, item.text())
            self.path = posixpath.normpath(self.path)
            self.change_folder()
        else:  # selected a file
            # open file
            self.open_file(posixpath.join(self.path, item.text()))

    def change_folder(self):
        self.setStatusBarMessage(self.path)
        self.listWidget.clear()
        self.details.clear()

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

    @staticmethod
    def open_file(filepath):
        print(f"opening file {filepath}")
        tmp_folder = os.path.join(
            str(QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.TempLocation)),
            'irodsgui')
        os.makedirs(tmp_folder, exist_ok=True)
        local_path = os.path.join(tmp_folder, os.path.basename(filepath))
        try:
            glob.irods_session.data_objects.get(
                filepath, local_path=local_path)
        except OVERWRITE_WITHOUT_FORCE_FLAG:
            print("file already there")
        except CAT_NO_ACCESS_PERMISSION:
            msgbox = QMessageBox()
            msgbox.setWindowTitle("Open File")
            msgbox.setText(
                "<p>Permission denied.</p>")
            msgbox.setIcon(QMessageBox.Icon.Critical)
            msgbox.exec()
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(local_path))

    def edit_settings(self):
        self.settings_window.show()

    def setup_menus(self):
        quit_icon = self.style().standardIcon(
            QStyle.StandardPixmap.SP_BrowserStop)
        login_icon = self.style().standardIcon(
            QStyle.StandardPixmap.SP_ComputerIcon)
        qt_icon = self.style().standardIcon(
            QStyle.StandardPixmap.SP_TitleBarMenuButton)
        dl_icon = self.style().standardIcon(
            QStyle.StandardPixmap.SP_ToolBarVerticalExtensionButton)
        # File Menu
        file_menu = QMenu("File", self)
        quit_action = QAction(quit_icon, "Quit", self)
        quit_action.triggered.connect(self.close)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)

        login_action = QAction(login_icon, "Login", self)
        login_action.triggered.connect(self.login)
        login_action.setShortcut(QKeySequence.StandardKey.Open)
        file_menu.addAction(login_action)
        file_menu.addSeparator()
        file_menu.addAction(quit_action)

        # Edit Menu
        edit_menu = QMenu("Edit", self)
        settings_action = QAction("Settings...", self)
        settings_action.triggered.connect(self.edit_settings)
        edit_menu.addAction(settings_action)

        # About/Help Menu
        about_menu = QMenu("About", self)
        help_action = QAction("Help", self)
        help_action.triggered.connect(self.help)
        help_action.setShortcut(QKeySequence.StandardKey.HelpContents)
        about_action = QAction("About", self)
        about_action.triggered.connect(self.about)
        about_qt_action = QAction(qt_icon, "About Qt", self)
        about_qt_action.triggered.connect(
            lambda: QMessageBox.aboutQt(self, "About Qt"))
        about_menu.addAction(help_action)
        about_menu.addSeparator()
        about_menu.addAction(about_action)
        about_menu.addAction(about_qt_action)

        # Download menu
        download_action = QAction(dl_icon, "Download", self)
        download_action.triggered.connect(self.download)
        self.menu.addAction(download_action)

        # Add everything
        self.menubar.addAction(file_menu.menuAction())
        self.menubar.addAction(edit_menu.menuAction())
        self.menubar.addAction(about_menu.menuAction())

    @staticmethod
    def help():
        # TODO: implement help message box
        pass

    @staticmethod
    def about():
        msg_box = QMessageBox()
        msg_box.setWindowTitle('PhenXFlow - About')
        msg_box.setText(
            "<div style='text-align: center'>"
            "<h2>IrodsGui:</h2>"
            "<p>A Simple GUI for irods</p><br>"
            f"<p> version: {__version__}</p>"
            f"<p>Python version: {sys.version}</p>"
            "</div>"
        )
        msg_box.exec()

    def download(self):
        doc_folder = str(QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DocumentsLocation))
        folder = QFileDialog.getExistingDirectory(self,
                                                  "Save to folder",
                                                  directory=doc_folder,
                                                  options=QFileDialog.Option.ShowDirsOnly)
        if folder != "":
            download_targets = self.listWidget.selectedIndexes()
            for idx in download_targets:
                target = self.listWidget.itemFromIndex(idx)

                irods_path = posixpath.join(self.path, target.text())
                n = 1
                if glob.irods_session.collections.exists(irods_path):
                    coll = glob.irods_session.collections.get(irods_path)
                    objects = coll.data_objects
                    n = len(objects) - 1
                bar = self.progressDock.add_download(
                    posixpath.basename(irods_path), n)
                t = DownloadThread(self.path, target.text(), folder, bar)
                t.signals.workerMessage.connect(self.download_finished)
                t.signals.delete_bar.connect(self.delete_bar)
                t.start()
                self.threads.append(t)

    def download_finished(self, msg):
        self.trayicon.showMessage(
            "IrodsGui", f'{msg} downloaded',
            QSystemTrayIcon.Information, 2000)

    def delete_bar(self, item):
        print(f"deleting {item}")
        self.progressDock.delete_row(item)

    def contextMenuEvent(self, a0, QContextMenuEvent=None) -> None:
        self.menu.exec(a0.globalPos())
