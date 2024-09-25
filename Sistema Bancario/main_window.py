
from PyQt6.QtWidgets import (QWidget, QPushButton, QVBoxLayout)
from PyQt6.QtCore import Qt
from styles import STYLE_SHEET
from create_account_window import CreateAccountWindow
from login_window import LoginWindow

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema Bancário")
        self.setStyleSheet(STYLE_SHEET)
        self.setFixedSize(400, 300)  # Tamanho fixo padrão
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.create_account_button = QPushButton("Criar Conta")
        self.create_account_button.setFixedSize(200, 40)
        self.create_account_button.clicked.connect(self.open_create_account)

        self.login_button = QPushButton("Entrar em Conta")
        self.login_button.setFixedSize(200, 40)
        self.login_button.clicked.connect(self.open_login)

        layout.addWidget(self.create_account_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.login_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def open_create_account(self):
        self.hide()
        self.create_account_window = CreateAccountWindow()
        self.create_account_window.show()

    def open_login(self):
        self.hide()
        self.login_window = LoginWindow()
        self.login_window.show()