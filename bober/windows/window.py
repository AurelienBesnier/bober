import os
import posixpath
import sys

from irods.exception import CAT_NO_ACCESS_PERMISSION, OVERWRITE_WITHOUT_FORCE_FLAG
from qtpy.QtCore import QSettings, QStandardPaths, Qt, QUrl, QSize, QCoreApplication
from qtpy.QtGui import QDesktopServices, QIcon, QKeySequence, QMovie
from qtpy.QtWidgets import (
    QAbstractItemView,
    QAction,
    QDialog,
    QFileDialog,
    QLineEdit,
    QListWidget,
    QMenu,
    QMessageBox,
    QPushButton,
    QStyle,
    QSystemTrayIcon,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
)

import bober.globals as glob
from bober.utils import assets_folder, bober_path
from bober.version import __version__
from bober.widgets.detail_dock import DetailDock
from bober.widgets.progress_dock import ProgressDock
from bober.windows.login_window import LoginWindow
from bober.windows.main_window import MainWindow
from bober.windows.settings_window import SettingsWindow
from bober.workers import ChangeFolderThread, DownloadThread, UploadThread


class Window(MainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1280, 720)
        self.center()
        self.setStatusBar(self.statusbar)

        # Main Widgets
        self.content = QWidget(self)
        self.content_layout = QVBoxLayout(self.content)
        self.toolbar = QToolBar(self)
        self.back_button = QPushButton(
            QCoreApplication.translate("window", "Back"), self
        )
        self.back_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowBack)
        )
        self.back_button.clicked.connect(self.back_folder)
        self.back_button.setShortcut(QKeySequence.StandardKey.Back)
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText(
            QCoreApplication.translate("window", "Filter...")
        )
        self.search_bar.textChanged.connect(
            lambda: self.change_filter(self.search_bar.text())
        )
        self.tab_widget = QTabWidget(self)
        self.toolbar.addWidget(self.back_button)
        self.toolbar.addWidget(self.search_bar)
        self.change_layout = QHBoxLayout()
        self.change_lbl = QLabel()
        self.change_progress = QMovie(
            str(assets_folder() / "loading-anim.gif"), parent=self.change_lbl
        )
        print(self.change_progress.fileName())
        self.change_lbl.setMovie(self.change_progress)
        self.change_progress.setScaledSize(QSize(32, 32))
        self.change_layout.addWidget(self.change_lbl)

        self.content_layout.addWidget(self.toolbar)
        self.content_layout.addWidget(self.tab_widget)
        self.content_layout.addLayout(self.change_layout)
        self.list_widget = QListWidget(self)
        self.list_widget.currentItemChanged.connect(self.detail_item)
        self.list_widget.itemDoubleClicked.connect(self.on_double_click)
        self.list_widget.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )
        self.tab_widget.addTab(
            self.list_widget, QCoreApplication.translate("window", "Explorer")
        )
        self.detail_dock = DetailDock(self)
        self.detail_dock.hide()
        self.progress_dock = ProgressDock()
        self.progress_dock.hide()

        # Sub Widgets
        self.settings_window = SettingsWindow(None)
        self.login_window = LoginWindow()
        self.settings = QSettings()
        self.menu = QMenu(self)
        self.tray_icon = QSystemTrayIcon()
        # Vars
        self.root = ""
        self.path = ""
        self.details = []
        self.folder_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        self.file_icon = self.style().standardIcon(
            QStyle.StandardPixmap.SP_FileLinkIcon
        )
        self.threads = []

        self.tray_icon.setIcon(QIcon(os.path.join(assets_folder(), "icon.ico")))
        self.tray_icon.show()
        self.setup_menus()
        self.setCentralWidget(self.content)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.detail_dock)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.progress_dock)
        self.set_status_bar_message(
            QCoreApplication.translate("window", "Application Started"), 3000
        )

    def change_filter(self, pattern):
        for row in range(self.list_widget.count()):
            it = self.list_widget.item(row)
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
            self.set_status_bar_message(
                QCoreApplication.translate("window", "logged in"), 5000
            )
            self.root = self.settings.value("root_path")
            self.path = self.root
            self.change_folder()

    def detail_item(self, item):
        try:
            if item.type() != 0:
                if self.detail_dock.isHidden():
                    self.detail_dock.show()
                print(posixpath.join(self.path, item.text()))
                # meta = glob.irods_session.metadata.get(
                #     DataObject, posixpath.join(self.path, item.text())
                # )
                # print(meta)
                data = glob.irods_session.data_objects.get(
                    posixpath.join(self.path, item.text())
                )
                self.detail_dock.update_info(item.text(), data)
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
        self.set_status_bar_message(self.path)
        self.list_widget.clear()
        self.details.clear()
        thread = ChangeFolderThread(
            self.list_widget,
            self.path,
            self.folder_icon,
            self.file_icon,
            self.change_lbl,
        )
        thread.signals.show_change.connect(self.show_change)
        thread.signals.hide_change.connect(self.hide_change)

        thread.start()
        self.threads.append(thread)

    def show_change(self):
        self.change_lbl.show()
        self.change_progress.start()

    def hide_change(self):
        self.change_lbl.hide()
        self.change_progress.stop()

    @staticmethod
    def open_file(filepath):
        print(f"opening file {filepath}")
        tmp_folder = os.path.join(
            str(
                QStandardPaths.writableLocation(
                    QStandardPaths.StandardLocation.TempLocation
                )
            ),
            glob.app_name,
        )
        os.makedirs(tmp_folder, exist_ok=True)
        local_path = os.path.join(tmp_folder, os.path.basename(filepath))
        try:
            glob.irods_session.data_objects.get(filepath, local_path=local_path)
        except OVERWRITE_WITHOUT_FORCE_FLAG:
            print("file already there")
        except CAT_NO_ACCESS_PERMISSION:
            msgbox = QMessageBox()
            msgbox.setWindowTitle(QCoreApplication.translate("window", "Open File"))
            msgbox.setText(
                "<p>"
                + QCoreApplication.translate("window", "Permission denied.")
                + "</p>"
            )
            msgbox.setIcon(QMessageBox.Icon.Critical)
            msgbox.exec()
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(local_path))

    def edit_settings(self):
        self.settings_window.show()

    def setup_menus(self):
        refresh_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload)
        quit_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserStop)
        login_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        qt_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMenuButton)
        dl_icon = self.style().standardIcon(
            QStyle.StandardPixmap.SP_TitleBarUnshadeButton
        )
        ul_icon = self.style().standardIcon(
            QStyle.StandardPixmap.SP_TitleBarShadeButton
        )
        # File Menu
        file_menu = QMenu(QCoreApplication.translate("window", "File"), self)
        login_action = QAction(
            login_icon, QCoreApplication.translate("window", "Login"), self
        )
        login_action.triggered.connect(self.login)
        login_action.setShortcut(QKeySequence.StandardKey.Open)

        refresh_action = QAction(
            refresh_icon, QCoreApplication.translate("window", "Refresh"), self
        )
        refresh_action.triggered.connect(self.change_folder)
        refresh_action.setShortcut(QKeySequence.StandardKey.Refresh)

        quit_action = QAction(
            quit_icon, QCoreApplication.translate("window", "Quit"), self
        )
        quit_action.triggered.connect(self.close)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        file_menu.addAction(login_action)
        file_menu.addAction(refresh_action)
        file_menu.addSeparator()
        file_menu.addAction(quit_action)

        # Edit Menu
        edit_menu = QMenu(QCoreApplication.translate("window", "Edit"), self)
        settings_action = QAction(
            QCoreApplication.translate("window", "Settings"), self
        )
        settings_action.triggered.connect(self.edit_settings)
        edit_menu.addAction(settings_action)

        # About/Help Menu
        about_menu = QMenu(QCoreApplication.translate("window", "About"), self)
        help_action = QAction(QCoreApplication.translate("window", "Help"), self)
        help_action.triggered.connect(self.help)
        help_action.setShortcut(QKeySequence.StandardKey.HelpContents)
        about_action = QAction(QCoreApplication.translate("window", "About"), self)
        about_action.triggered.connect(self.about)
        about_qt_action = QAction(
            qt_icon, QCoreApplication.translate("window", "About Qt"), self
        )
        about_qt_action.triggered.connect(
            lambda: QMessageBox.aboutQt(
                self, QCoreApplication.translate("window", "About Qt")
            )
        )
        about_menu.addAction(help_action)
        about_menu.addSeparator()
        about_menu.addAction(about_action)
        about_menu.addAction(about_qt_action)

        # Download menu
        download_action = QAction(
            dl_icon, QCoreApplication.translate("window", "Download"), self
        )
        download_action.triggered.connect(self.download)
        upload_action = QAction(
            ul_icon, QCoreApplication.translate("window", "Upload file"), self
        )
        upload_action.triggered.connect(self.upload_file)

        self.menu.addAction(upload_action)
        self.menu.addAction(download_action)

        # Add everything
        self.menubar.addAction(file_menu.menuAction())
        self.menubar.addAction(edit_menu.menuAction())
        self.menubar.addAction(about_menu.menuAction())

    def help(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(
            f"{glob.app_name} - " + QCoreApplication.translate("window", "Help")
        )
        msg_box.setText(
            "<div style='text-align: center'>"
            "<h2>"
            + QCoreApplication.translate("window", "Welcome to ")
            + f"{glob.app_name}!</h2>"
            "<p>"
            + QCoreApplication.translate(
                "window",
                "Before doing anything, please be sure to "
                "update the settings of the application. To do this, go to 'Edit'->'Settings'.",
            )
            + "</p>"
            "<p>"
            + QCoreApplication.translate(
                "window",
                "Then, you can login with the login window dialog. Go to 'File'->'Login'.",
            )
            + "</p>"
            + QCoreApplication.translate(
                "window",
                "Once logged in you can enjoy browsing your irods instance like a regular system file explorer. "
                "You can also download those file be right-clicking and hitting the 'Download' button.",
            )
            + "</div>"
        )
        msg_box.setWindowModality(Qt.NonModal)
        msg_box.show()

    @staticmethod
    def about():
        msg_box = QMessageBox()
        msg_box.setWindowTitle(
            f"{glob.app_name} - " + QCoreApplication.translate("window", "About")
        )
        msg_box.setText(
            "<div style='text-align: center'>"
            f"<h2>{glob.app_name}:</h2>"
            "<p>A Simple GUI for irods</p>"
            f"<p><img width='250' height='250' src='{bober_path()}'><p>"
            f"<p> version: {__version__}<br>"
            f"Python version: {sys.version}</p>"
            "<p><a href='https://github.com/AurelienBesnier/irods-gui'>Github</a></p>"
            "</div>"
        )
        msg_box.exec()

    def upload_file(self):
        file = QFileDialog.getOpenFileName(
            self,
            QCoreApplication.translate("window", "Upload file"),
        )[0]

        print(file)
        irods_path = posixpath.join(self.path, os.path.basename(file))
        print(irods_path)

        if file != "":
            t = UploadThread(file, irods_path)
            t.signals.workerMessage.connect(self.upload_finished_notify)
            t.start()
            self.threads.append(t)

    def download(self):
        doc_folder = str(
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.DocumentsLocation
            )
        )
        folder = QFileDialog.getExistingDirectory(
            self,
            QCoreApplication.translate("window", "Save to folder"),
            directory=doc_folder,
            options=QFileDialog.Option.ShowDirsOnly,
        )
        if self.progress_dock.isHidden():
            self.progress_dock.show()
        if folder != "":
            download_targets = self.list_widget.selectedIndexes()
            for idx in download_targets:
                target = self.list_widget.itemFromIndex(idx)

                irods_path = posixpath.join(self.path, target.text())
                n = 1
                if glob.irods_session.collections.exists(irods_path):
                    coll = glob.irods_session.collections.get(irods_path)
                    objects = coll.data_objects
                    n = len(objects) - 1
                progress_bar = self.progress_dock.add_download(
                    posixpath.basename(irods_path), n
                )
                t = DownloadThread(self.path, target.text(), folder, progress_bar)
                t.signals.workerMessage.connect(self.download_finished)
                t.signals.delete_bar.connect(self.delete_bar)
                t.start()
                self.threads.append(t)

    def upload_finished_notify(self, msg):
        if self.settings.value("notifications", defaultValue="true") == "true":
            self.tray_icon.showMessage(
                f"{glob.app_name}",
                f"{msg} " + QCoreApplication.translate("window", "uploaded"),
                QSystemTrayIcon.Information,
                2000,
            )

    def download_finished(self, msg):
        if self.settings.value("notifications", defaultValue="true") == "true":
            self.tray_icon.showMessage(
                f"{glob.app_name}",
                f"{msg} " + QCoreApplication.translate("window", "downloaded"),
                QSystemTrayIcon.Information,
                2000,
            )

    def delete_bar(self, item):
        self.progress_dock.delete_row(item)

    def contextMenuEvent(self, a0, QContextMenuEvent=None) -> None:
        self.menu.exec(a0.globalPos())

    def keyPressEvent(self, event, **kwargs):
        if event.key() == Qt.Key.Key_F5:
            self.change_folder()
