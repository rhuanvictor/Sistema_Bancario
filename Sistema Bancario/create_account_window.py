import sqlite3
from PyQt6.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, 
                             QVBoxLayout, QComboBox, QTextEdit, QMessageBox)
from PyQt6.QtCore import Qt

from validators import format_cpf
from styles import STYLE_SHEET
from register_window import RegisterWindow


class CreateAccountWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Criar Conta")
        self.setStyleSheet(STYLE_SHEET)
        self.setFixedSize(400, 300)  # Tamanho fixo padrão
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.account_type_label = QLabel("Tipo de Conta:")
        self.account_type_combo = QComboBox()
        self.account_type_combo.addItems(["Conta Corrente", "Conta Poupança"])
        self.account_type_combo.setFixedSize(200, 30)

        self.cpf_label = QLabel("CPF:")
        self.cpf_input = QLineEdit()
        self.cpf_input.setMaxLength(14)
        self.cpf_input.setFixedSize(200, 30)
        self.cpf_input.textChanged.connect(self.format_cpf_input)

    

        self.next_button = QPushButton("Ir para Cadastro")
        self.next_button.setFixedSize(200, 40)
        self.next_button.clicked.connect(self.verify_cpf)
       # self.next_button.clicked.connect(self.verify_cpfe)

        self.back_button = QPushButton("Voltar")
        self.back_button.setFixedSize(200, 40)
        self.back_button.clicked.connect(self.go_back)

        self.info_display = QTextEdit()
        self.info_display.setReadOnly(True)

        

        layout.addWidget(self.account_type_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.account_type_combo, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.cpf_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.cpf_input, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.next_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_display)

        self.setLayout(layout)
    
    

    def format_cpf_input(self):
        text = self.cpf_input.text().replace('.', '').replace('-', '')
        if text.isdigit():
            formatted_cpf = format_cpf(text)
            self.cpf_input.setText(formatted_cpf)
            self.cpf_input.setCursorPosition(len(formatted_cpf))

    def verify_cpf(self):
        cpf = self.cpf_input.text().replace('.', '').replace('-', '')
        if len(cpf) < 11:
            self.show_info("CPF inválido! O CPF deve ter pelo menos 11 dígitos.")        
            return
        
        account_type = self.account_type_combo.currentText()

        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM accounts WHERE cpf = ? AND tipo_conta = ?", (cpf, account_type))
        account = cursor.fetchone()

        if not account:
            self.hide()
            self.registration_window = RegisterWindow(cpf, account_type)
            self.registration_window.show()
        else:
            self.show_info("Já existe uma conta com esse CPF.")

        conn.close()

    def show_info(self, message):
        self.info_display.setText(message)

    def go_back(self):
        self.hide()
        from main_window import MainWindow
        self.main_window = MainWindow()
        self.main_window.show()