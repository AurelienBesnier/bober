import os
import traceback
import posixpath

from qtpy.QtCore import QObject, Signal, QThread

import irodsgui.globals as glob

from irods.exception import CAT_NO_ROWS_FOUND, CollectionDoesNotExist


class WorkerSignalsMsg(QObject):
    finished = Signal(name="finished")
    error = Signal(str, name="error")
    delete_bar = Signal(str, name="delete_bar")
    workerMessage = Signal(str, name="workerMessage")


class DownloadThread(QThread):
    def __init__(self, path, download_target, folder, bar):
        super(DownloadThread, self).__init__()
        self.path = path
        self.download_target = download_target
        self.folder = folder
        self.bar = bar
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
                        glob.irods_session.data_objects.get(
                            d.path, save_folder)
                        self.bar.setValue(self.bar.value() + 1)
                else:
                    glob.irods_session.data_objects.get(
                        irods_path, self.folder)
                    self.bar.setValue(1)
                self.signals.workerMessage.emit(irods_path)

            except CAT_NO_ROWS_FOUND as e:
                print(e)
            except CollectionDoesNotExist:
                print(f'{irods_path} does not exist')

        except Exception as e:
            print(e, flush=True)
            self.signals.error.emit(traceback.format_exc())
        finally:
            self.sleep(2)
            self.signals.delete_bar.emit(posixpath.basename(irods_path))
            self.signals.finished.emit()

    def quit(self):
        self.running = False
        super().quit()
