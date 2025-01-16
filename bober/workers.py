import os
import posixpath
import traceback

from irods.exception import CAT_NO_ROWS_FOUND, CollectionDoesNotExist
from qtpy.QtCore import QObject, QThread, Signal, QCoreApplication
from qtpy.QtWidgets import QListWidgetItem

import bober.globals as glob


class WorkerSignalsMsg(QObject):
    finished = Signal(name="finished")
    error = Signal(str, name="error")
    delete_bar = Signal(str, name="delete_bar")
    workerMessage = Signal(str, name="workerMessage")


class ChangeSignals(QObject):
    hide_change = Signal(name="hide_change")
    show_change = Signal(name="show_change")


class ChangeFolderThread(QThread):
    def __init__(self, list_widget, path, folder_icon, file_icon, change_progress):
        super().__init__()
        self.list_widget = list_widget
        self.path = path
        self.folder_icon = folder_icon
        self.file_icon = file_icon
        self.change_progress = change_progress
        self.signals = ChangeSignals()

    def run(self):
        self.signals.show_change.emit()
        dirs = [QListWidgetItem(self.folder_icon, "..")]
        files = []
        coll = glob.irods_session.collections.get(self.path)
        dirs.extend(
            [QListWidgetItem(self.folder_icon, d.name) for d in coll.subcollections]
        )
        files.extend(
            [
                QListWidgetItem(self.file_icon, f.name, None, 1000)
                for f in coll.data_objects
            ]
        )

        for directory in dirs:
            self.list_widget.addItem(directory)
        for file in files:
            self.list_widget.addItem(file)

        self.list_widget.sortItems()
        self.signals.hide_change.emit()


class UploadThread(QThread):
    def __init__(self, path, upload_targe):
        super().__init__()
        self.path = path
        self.upload_target = upload_targe
        self.signals = WorkerSignalsMsg()

    def run(self) -> None:
        try:
            try:
                # If collection
                if glob.irods_session.collections.exists(self.upload_target):
                    self.signals.error.emit(
                        QCoreApplication.translate("worker", "File already exists")
                    )
                else:
                    glob.irods_session.data_objects.put(self.path, self.upload_target)
                self.signals.workerMessage.emit(self.path)
            except CAT_NO_ROWS_FOUND as e:
                print(e)
        except Exception as e:
            print(e, flush=True)
            self.signals.error.emit(traceback.format_exc())
        finally:
            self.sleep(2)
            self.signals.finished.emit()


class DownloadThread(QThread):
    def __init__(self, path, download_target, folder, progress_bar):
        super().__init__()
        self.path = path
        self.download_target = download_target
        self.folder = folder
        self.progress_bar = progress_bar
        self.signals = WorkerSignalsMsg()

    def run(self) -> None:
        irods_path = posixpath.join(self.path, self.download_target)
        try:
            try:
                # If collection
                if glob.irods_session.collections.exists(irods_path):
                    coll = glob.irods_session.collections.get(irods_path)
                    for d in coll.data_objects:
                        save_folder = os.path.join(self.folder, coll.name)
                        os.makedirs(save_folder, exist_ok=True)
                        glob.irods_session.data_objects.get(d.path, save_folder)
                        self.progress_bar.setValue(self.progress_bar.value() + 1)
                else:
                    glob.irods_session.data_objects.get(irods_path, self.folder)
                    self.progress_bar.setValue(1)
                self.signals.workerMessage.emit(irods_path)

            except CAT_NO_ROWS_FOUND as e:
                print(e)
            except CollectionDoesNotExist:
                print(
                    f"{irods_path} "
                    + QCoreApplication.translate("worker", "does not exist")
                )

        except Exception as e:
            print(e, flush=True)
            self.signals.error.emit(traceback.format_exc())
        finally:
            self.sleep(2)
            self.signals.delete_bar.emit(posixpath.basename(irods_path))
            self.signals.finished.emit()
