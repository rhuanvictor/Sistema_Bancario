from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit
from styles import STYLE_SHEET
from validators import format_cpf
from bank_window import BankWindow
import sqlite3
import bcrypt


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema Bancário - Login")
        self.setStyleSheet(STYLE_SHEET)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.cpf_label = QLabel("CPF:")
        self.cpf_input = QLineEdit()
        self.cpf_input.setMaxLength(14)
        self.cpf_input.textChanged.connect(self.format_cpf_input)

        self.senha_label = QLabel("Senha:")
        self.senha_input = QLineEdit()
        self.senha_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.tipo_conta_label = QLabel("Tipo de Conta:")
        self.tipo_conta_combo = QComboBox()
        self.tipo_conta_combo.addItems(["Conta Corrente", "Conta Poupança"])

        self.login_button = QPushButton("Entrar")
        self.login_button.clicked.connect(self.login)

        self.register_button = QPushButton("Cadastrar")
        self.register_button.clicked.connect(self.register)

        self.back_button = QPushButton("Voltar")
        self.back_button.clicked.connect(self.go_back)

        self.info_display = QTextEdit()
        self.info_display.setReadOnly(True)

        layout.addWidget(self.cpf_label)
        layout.addWidget(self.cpf_input)
        layout.addWidget(self.senha_label)
        layout.addWidget(self.senha_input)
        layout.addWidget(self.tipo_conta_label)
        layout.addWidget(self.tipo_conta_combo)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)
        layout.addWidget(self.back_button)
        layout.addWidget(self.info_display)

        self.setLayout(layout)

    def format_cpf_input(self):
        text = self.cpf_input.text().replace('.', '').replace('-', '')
        if text.isdigit():
            formatted_cpf = format_cpf(text)
            self.cpf_input.setText(formatted_cpf)
            self.cpf_input.setCursorPosition(len(formatted_cpf))

    def login(self):
        cpf = self.cpf_input.text().replace('.', '').replace('-', '')
        senha = self.senha_input.text().strip()  # Adicionando strip para remover espaços extras
        tipo_conta = self.tipo_conta_combo.currentText().strip()

        # Debug - Imprimindo valores antes da consulta
        print(f"CPF: {cpf}, Senha: {senha}, Tipo de Conta: {tipo_conta}")

        # Conectando ao banco de dados
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()

        # Consulta de debug para verificar as contas no banco
        cursor.execute("SELECT * FROM accounts WHERE cpf = ?", (cpf,))
        accounts = cursor.fetchall()
        print("Contas encontradas para o CPF no banco:")
        for acc in accounts:
            print(acc)  # Verifica todas as contas associadas a esse CPF

        # Executar consulta SQL para obter a senha armazenada
        print(f"Executando consulta para CPF: {cpf} e Tipo de Conta: {tipo_conta}")
        cursor.execute("SELECT senha FROM accounts WHERE cpf = ? AND tipo_conta = ?", (cpf, tipo_conta))
        result = cursor.fetchone()

        if result:
            stored_password = result[0]  # O hash da senha armazenado
            # Verifica se a senha informada corresponde ao hash armazenado
            if bcrypt.checkpw(senha.encode('utf-8'), stored_password):
                print("Senha correta.")
                # Se a senha estiver correta, busque a conta completa
                cursor.execute("SELECT * FROM accounts WHERE cpf = ? AND tipo_conta = ?", (cpf, tipo_conta))
                account = cursor.fetchone()

                if account:
                    print(f"Conta encontrada: {account}")
                    self.hide()
                    self.bank_window = BankWindow(cpf, tipo_conta)
                    self.bank_window.show()
                else:
                    self.show_info("Conta não encontrada para este CPF e tipo de conta!")
            else:
                self.show_info("Senha incorreta.")
        else:
            self.show_info("Conta não encontrada para este CPF e tipo de conta!")

        conn.close()


    def register(self):
        self.hide()
        from create_account_window import CreateAccountWindow
        self.create_account_window = CreateAccountWindow()

        self.create_account_window.show()

    def show_info(self, message):
        self.info_display.setText(message)

    def go_back(self):
        self.hide()
        from main_window import MainWindow
        self.main_window = MainWindow()
        self.main_window.show()

    
