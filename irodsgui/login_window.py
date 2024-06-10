from qtpy.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton
from qtpy.QtCore import QSettings


class LoginWindow(QDialog):

    def __init__(self):
        super().__init__()
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
        pass
