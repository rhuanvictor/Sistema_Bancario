import sqlite3
from PyQt6.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QTextEdit, QSizePolicy, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtCore import QDate  # Certifique-se de incluir isso
from datetime import datetime

from validators import format_cpf, is_valid_cpf
import bcrypt
from styles import STYLE_SHEET

class RegisterWindow(QWidget):
    def __init__(self, cpf, account_type):
        super().__init__()
        self.setWindowTitle("Cadastro de Conta")
        self.setStyleSheet(STYLE_SHEET)
        self.setFixedSize(500, 400)  # Tamanho fixo padrão
        self.init_ui(cpf, account_type)

    def init_ui(self, cpf, account_type):
        layout = QVBoxLayout()

        # CPF Layout
        cpf_layout = QHBoxLayout()
        self.cpf_label = QLabel("CPF:")
        self.cpf_label.setStyleSheet("font-weight: bold;")
        self.cpf_input = QLineEdit()
        self.cpf_input.setMaxLength(14)
        self.cpf_input.setText(format_cpf(cpf))
        self.cpf_input.setEnabled(False)
        self.cpf_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        cpf_layout.addWidget(self.cpf_label)
        cpf_layout.addWidget(self.cpf_input)

        # Account Type Layout
        account_type_layout = QHBoxLayout()
        account_type_layout.setSpacing(5)
        account_type_layout.setContentsMargins(0, 0, 0, 0)

        self.account_type_label = QLabel("Tipo de Conta:")
        self.account_type_display = QLabel(account_type)

        self.account_type_label.setStyleSheet("font-weight: bold;")
        self.account_type_display.setStyleSheet("font-weight: bold;")

        self.account_type_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.account_type_display.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        account_type_layout.addWidget(self.account_type_label)
        account_type_layout.addWidget(self.account_type_display)
        account_type_layout.addStretch()

        # Name Layout
        name_layout = QHBoxLayout()
        self.name_label = QLabel("Nome:")
        self.name_label.setStyleSheet("font-weight: bold;")
        self.name_input = QLineEdit()
        self.name_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        name_layout.addWidget(self.name_label)
        name_layout.addWidget(self.name_input)

        # Date of Birth Layout
        dob_layout = QHBoxLayout()
        self.dob_label = QLabel("Data de Nascimento:")
        self.dob_label.setStyleSheet("font-weight: bold;")

        self.dob_input = QLineEdit()
        self.dob_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        self.dob_input.textChanged.connect(self.format_dob)

        dob_layout.addWidget(self.dob_label)
        dob_layout.addWidget(self.dob_input)

        # Address Layout
        address_layout = QHBoxLayout()
        self.address_label = QLabel("Endereço:")
        self.address_label.setStyleSheet("font-weight: bold;")
        self.address_input = QLineEdit()
        self.address_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        address_layout.addWidget(self.address_label)
        address_layout.addWidget(self.address_input)

        # Password Layout
        password_layout = QHBoxLayout()
        self.password_label = QLabel("Senha:")
        self.password_label.setStyleSheet("font-weight: bold;")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        password_layout.addWidget(self.password_label)
        password_layout.addWidget(self.password_input)

        # Buttons
        self.register_button = QPushButton("Cadastrar")
        self.register_button.setFixedSize(200, 40)
        self.register_button.clicked.connect(self.register_account)

        self.back_button = QPushButton("Voltar")
        self.back_button.setFixedSize(200, 40)
        self.back_button.clicked.connect(self.go_back)

        self.info_display = QTextEdit()
        self.info_display.setReadOnly(True)

        # Add layouts to main layout
        layout.addLayout(cpf_layout)
        layout.addLayout(account_type_layout)
        layout.addLayout(name_layout)
        layout.addLayout(dob_layout)
        layout.addLayout(address_layout)
        layout.addLayout(password_layout)
        layout.addWidget(self.info_display)

        # Add buttons
        layout.addWidget(self.register_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def format_dob(self):
        text = self.dob_input.text()
        text = ''.join(filter(str.isdigit, text))
        if len(text) > 2:
            text = text[:2] + '/' + text[2:]
        if len(text) > 5:
            text = text[:5] + '/' + text[5:]
        
        self.dob_input.blockSignals(True)
        self.dob_input.setText(text)
        self.dob_input.blockSignals(False)

        if len(text) == 10:
            self.validate_age(text)

    def validate_age(self, dob):
        day, month, year = map(int, dob.split('/'))
        birth_date = QDate(year, month, day)
        age = birth_date.daysTo(QDate.currentDate()) // 365

        if age < 18:
            QMessageBox.warning(self, "Atenção", "Usuário precisa ser maior de idade.")
            self.dob_input.clear()

    def register_account(self):
        cpf = self.cpf_input.text().replace('.', '').replace('-', '')
        senha = self.password_input.text()
        tipo_conta = self.account_type_display.text()
        nome = self.name_input.text()
        data_nascimento = self.dob_input.text()
        endereco = self.address_input.text()

        # Verifique se todos os campos estão preenchidos
        if not all([cpf, senha, tipo_conta, nome, data_nascimento, endereco]):
            self.show_info("Por favor, preencha todos os campos.")
            return

        if not is_valid_cpf(cpf):
            self.show_info("CPF inválido!")
            return

        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()

        # Verificar se já existe uma conta do mesmo tipo para o CPF
        cursor.execute("SELECT * FROM accounts WHERE cpf = ? AND tipo_conta = ?", (cpf, tipo_conta))
        existing_account = cursor.fetchone()

        if existing_account:
            self.show_info(f"Já existe uma conta do tipo '{tipo_conta}' cadastrada para o CPF informado.")
            conn.close()
            return

        try:
            # Hash da senha
            hashed_password = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

            cursor.execute("INSERT INTO accounts (cpf, senha, nome, data_nascimento, endereco, tipo_conta) VALUES (?, ?, ?, ?, ?, ?)",
                        (cpf, hashed_password, nome, data_nascimento, endereco, tipo_conta))
            conn.commit()
            self.show_info("Conta cadastrada com sucesso! Redirecionando para tela de login")
            
            # Adiciona um QTimer para esperar 5 segundos
            self.timer = QTimer(self)
            self.timer.setSingleShot(True)
            self.timer.timeout.connect(self.go_to_login)
            self.timer.start(5000)  # 5000 milissegundos = 5 segundos
            
        except sqlite3.IntegrityError:
            self.show_info("CPF já cadastrado!")

        conn.close()

    def go_to_login(self):
        self.hide()
        from login_window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()


    def show_info(self, message):
        self.info_display.setText(message)

    def go_back(self):
        self.hide()
        from main_window import CreateAccountWindow
        self.main_window = CreateAccountWindow()
        self.main_window.show()

         