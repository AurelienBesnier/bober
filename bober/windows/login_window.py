import irods
from irods.session import iRODSSession
from qtpy.QtCore import QSettings, QCoreApplication
from qtpy.QtWidgets import QDialog, QFormLayout, QLineEdit, QMessageBox, QPushButton

import bober.globals as glob


class LoginWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle(
            f"{glob.app_name} - " + QCoreApplication.translate("login", "Login")
        )
        self.settings = QSettings()

        self.layout = QFormLayout(self)
        self.username_edit = QLineEdit(self)
        self.password_edit = QLineEdit(self)
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_button = QPushButton(
            QCoreApplication.translate("login", "Confirm"), self
        )
        self.confirm_button.clicked.connect(self.login)
        self.layout.addRow(
            QCoreApplication.translate("login", "Username: "), self.username_edit
        )
        self.layout.addRow(
            QCoreApplication.translate("login", "Password: "), self.password_edit
        )
        self.layout.addRow(self.confirm_button)
        self.adjustSize()

    def login(self) -> None:
        """
        Starts the irods session of python-irodsclient with the information previously given.
        Returns
        -------
        None
        """
        cfg = self.settings.value("config_path")
        host = self.settings.value("host")
        port = self.settings.value("port")
        zone = self.settings.value("zone")
        ssl_options = {
            "irods_client_server_policy": "CS_NEG_REQUIRE",
            "irods_client_server_negotiation": "request_server_negotiation",
            "irods_ssl_verify_server": "cert",
            "irods_encryption_key_size": 32,
            "irods_encryption_salt_size": 8,
            "irods_encryption_num_hash_rounds": 16,
            "irods_encryption_algorithm": "AES-256-CBC",
        }
        try:
            glob.irods_session = iRODSSession(
                user=self.username_edit.text(),
                password=self.password_edit.text(),
                host=host,
                port=port,
                zone=zone,
                env_file=cfg,
                configure=True,
                **ssl_options,
            )
        except irods.exception.NetworkException as e:
            print(e)
            msgbox = QMessageBox()
            msgbox.setWindowTitle(QCoreApplication.translate("login", "Login"))
            msgbox.setText(f"<p>Network Error.</p><p>{e}</p>")
            msgbox.setIcon(QMessageBox.Icon.Critical)
            msgbox.exec()
            return
        except irods.exception.CAT_INVALID_USER as e:
            print(e)
            msgbox = QMessageBox()
            msgbox.setWindowTitle(QCoreApplication.translate("login", "Login"))
            msgbox.setText("<p>Invalid user name.</p>")
            msgbox.setIcon(QMessageBox.Icon.Warning)
            msgbox.exec()
            return
        except irods.exception.CAT_INVALID_AUTHENTICATION as e:
            print(e)
            msgbox = QMessageBox()
            msgbox.setWindowTitle(QCoreApplication.translate("login", "Login"))
            msgbox.setText("<p>Invalid authentication.</p>")
            msgbox.setIcon(QMessageBox.Icon.Warning)
            msgbox.exec()
            return
        except TypeError as e:
            print(e)
            msgbox = QMessageBox()
            msgbox.setWindowTitle(QCoreApplication.translate("login", "Login"))
            msgbox.setText("<p>Type Error: Did you set the settings correctly ?</p>")
            msgbox.setIcon(QMessageBox.Icon.Critical)
            msgbox.exec()
            return

        self.accept()
