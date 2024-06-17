import irods
from qtpy.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton
from qtpy.QtCore import QSettings

from irods.session import iRODSSession

import irodsgui.globals as glob


class LoginWindow(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("IrodsGui - Login")
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

    def login(self):
        cfg = self.settings.value('config_path')
        host = self.settings.value('host')
        port = self.settings.value('port')
        zone = self.settings.value('zone')
        SSL_options = {
            'irods_client_server_policy': 'CS_NEG_REQUIRE',
            'irods_client_server_negotiation': 'request_server_negotiation',
            'irods_ssl_verify_server': 'cert',
            'irods_encryption_key_size': 32,
            'irods_encryption_salt_size': 8,
            'irods_encryption_num_hash_rounds': 16,
            'irods_encryption_algorithm': 'AES-256-CBC',
        }
        try:
            glob.irods_session = iRODSSession(user=self.usernameEdit.text(),
                                              password=self.passwordEdit.text(),
                                              host=host, port=port, zone=zone,
                                              env_file=cfg, configure=True,
                                              auto_cleanup=True, **SSL_options)
            self.accept()
        except irods.exception.NetworkException as e:
            print(e)

