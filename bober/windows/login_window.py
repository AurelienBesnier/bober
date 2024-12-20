from qtpy.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton, QMessageBox
from qtpy.QtCore import QSettings

import irods
from irods.session import iRODSSession

import bober.globals as glob


class LoginWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle(f"{glob.app_name} - Login")
        self.settings = QSettings()

        self.layout = QFormLayout(self)
        self.usernameEdit = QLineEdit(self)
        self.passwordEdit = QLineEdit(self)
        self.passwordEdit.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirmButton = QPushButton("Confirm", self)
        self.confirmButton.clicked.connect(self.login)
        self.layout.addRow("Username: ", self.usernameEdit)
        self.layout.addRow("Password: ", self.passwordEdit)
        self.layout.addRow(self.confirmButton)
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
                user=self.usernameEdit.text(),
                password=self.passwordEdit.text(),
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
            msgbox.setWindowTitle("Login")
            msgbox.setText("<p>Network Error.</p>" f"<p>{e}</p>")
            msgbox.setIcon(QMessageBox.Icon.Critical)
            msgbox.exec()
            return
        except irods.exception.CAT_INVALID_USER as e:
            print(e)
            msgbox = QMessageBox()
            msgbox.setWindowTitle("Login")
            msgbox.setText("<p>Invalid user name.</p>")
            msgbox.setIcon(QMessageBox.Icon.Warning)
            msgbox.exec()
            return
        except irods.exception.CAT_INVALID_AUTHENTICATION as e:
            print(e)
            msgbox = QMessageBox()
            msgbox.setWindowTitle("Login")
            msgbox.setText("<p>Invalid authentication.</p>")
            msgbox.setIcon(QMessageBox.Icon.Warning)
            msgbox.exec()
            return
        except TypeError as e:
            print(e)
            msgbox = QMessageBox()
            msgbox.setWindowTitle("Login")
            msgbox.setText("<p>Type Error: Did you set the settings correctly ?</p>")
            msgbox.setIcon(QMessageBox.Icon.Critical)
            msgbox.exec()
            return

        self.accept()
