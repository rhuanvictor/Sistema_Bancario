from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
from datetime import datetime
import sqlite3
from styles import STYLE_SHEET

class BankWindow(QWidget):
    def __init__(self, cpf,tipo_conta):
        super().__init__()
        self.cpf = cpf
        self.tipo_conta = tipo_conta  # Armazena o tipo de conta como atributo
        self.setWindowTitle("Banco")
        self.setStyleSheet(STYLE_SHEET)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.info_display = QTextEdit()
        self.info_display.setReadOnly(True)

        self.saldo_button = QPushButton("Consultar Saldo")
        self.saldo_button.clicked.connect(self.consultar_saldo)

        self.saque_label = QLabel("Valor do Saque:")
        self.saque_input = QLineEdit()
        self.saque_input.setPlaceholderText("0.00")
        self.saque_input.textChanged.connect(self.format_currency_input)

        self.saque_button = QPushButton("Sacar Dinheiro")
        self.saque_button.clicked.connect(self.sacar_dinheiro)

        self.deposito_label = QLabel("Valor do Depósito:")
        self.deposito_input = QLineEdit()
        self.deposito_input.setPlaceholderText("0.00")
        self.deposito_input.textChanged.connect(self.format_currency_input)

        self.deposito_button = QPushButton("Depositar Dinheiro")
        self.deposito_button.clicked.connect(self.depositar_dinheiro)

        self.extrato_button = QPushButton("Consultar Extrato")
        self.extrato_button.clicked.connect(self.consultar_extrato)

        self.cadastro_button = QPushButton("Consultar Cadastro")
        self.cadastro_button.clicked.connect(self.consultar_cadastro)

        self.sair_button = QPushButton("Sair")
        self.sair_button.clicked.connect(self.close_app)

        layout.addWidget(self.info_display)
        layout.addWidget(self.saldo_button)
        layout.addWidget(self.saque_label)
        layout.addWidget(self.saque_input)
        layout.addWidget(self.saque_button)
        layout.addWidget(self.deposito_label)
        layout.addWidget(self.deposito_input)
        layout.addWidget(self.deposito_button)
        layout.addWidget(self.extrato_button)
        layout.addWidget(self.cadastro_button)  # Adicionando o botão de consulta
        layout.addWidget(self.sair_button)

        self.setLayout(layout)

    def format_currency_input(self):
        sender = self.sender()
        text = sender.text().replace('.', '').replace(',', '')
        if text.isdigit():
            try:
                # Converte o texto para float e divide por 100 para obter o valor em reais
                value = float(text) / 100
                # Formata o valor com 2 casas decimais, separador de milhares e ponto como separador decimal
                formatted_text = f"{value:,.2f}"
                sender.setText(formatted_text)
                sender.setCursorPosition(len(formatted_text))
               # print(f"Texto formatado: {formatted_text}")  # Exibe o valor formatado
            except ValueError:
                pass

    def consultar_saldo(self):
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT saldo FROM accounts WHERE cpf = ?  AND tipo_conta = ?", (self.cpf,self.tipo_conta))
        saldo = cursor.fetchone()[0]

        print(f"Saldo armazenado no banco: {saldo:.2f}")  # Exibe o saldo armazenado

        self.show_info(f"Saldo atual: R${saldo:,.2f}")

        conn.close()

    def sacar_dinheiro(self):
        text = self.saque_input.text().replace('.', '').replace(',', '')
        valor = float(text) / 100 if text else 0
       # print(f"Valor digitado para saque: {valor:,.2f}")  # Exibe o valor digitado
        self.realizar_saque(valor)

    def realizar_saque(self, valor):
        if valor <= 0:
            self.show_info("O valor do saque deve ser maior que zero.")
            return

        if valor > 500:
            self.show_info("O valor do saque não pode ultrapassar R$500,00.")
            return

        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()

        # Consultando saldo, saques diários e último saque
        cursor.execute("SELECT saldo, saques_diarios, ultimo_saque FROM accounts WHERE cpf = ? AND tipo_conta = ?", 
                    (self.cpf, self.tipo_conta))
        resultado = cursor.fetchone()
        saldo = resultado[0]
        saques_diarios = resultado[1]
        ultimo_saque = resultado[2]

        # Pegando a data de hoje (somente a data, sem a hora)
        hoje = datetime.now().strftime('%d-%m-%Y')
        
        # Comparando apenas a data do último saque (sem a hora)
        if ultimo_saque and ultimo_saque.startswith(hoje):
            if saques_diarios >= 3:
                self.show_info("Você já realizou 3 saques hoje. Tente novamente amanhã.")
                conn.close()
                return
        else:
            # Resetar saques diários se a data for diferente
            saques_diarios = 0

        if valor > saldo:
            self.show_info("Saldo insuficiente para o saque.")
            conn.close()
            return

        # Atualizando saldo, número de saques e a data do último saque
        novo_saldo = saldo - valor
        cursor.execute("UPDATE accounts SET saldo = ?, saques_diarios = ?, ultimo_saque = ? WHERE cpf = ?", 
                    (novo_saldo, saques_diarios + 1, hoje, self.cpf))

        # Gravando a transação com a data e hora atuais
        agora = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        cursor.execute("INSERT INTO transactions (cpf, tipo, valor, data, tipo_conta) VALUES (?, 'Saque', ?, ?, ?)", 
                    (self.cpf, valor, agora, self.tipo_conta))

        conn.commit()
        self.show_info("Saque realizado com sucesso!")
        conn.close()

    def depositar_dinheiro(self):
        text = self.deposito_input.text().replace('.', '').replace(',', '')
        valor = float(text) / 100 if text else 0
        #print(f"Valor digitado para depósito: {valor:,.2f}")  # Exibe o valor digitado
        self.depositar(valor)

    def depositar(self, valor):
        if valor <= 0:
            self.show_info("O valor do depósito deve ser maior que zero.")
            return

        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()

        cursor.execute("SELECT saldo FROM accounts WHERE cpf = ? AND tipo_conta = ?", (self.cpf, self.tipo_conta))
        saldo = cursor.fetchone()

        if saldo is None:
            self.show_info("Conta não encontrada.")
            conn.close()
            return

        saldo = saldo[0]
        novo_saldo = saldo + valor
        cursor.execute("UPDATE accounts SET saldo = ? WHERE cpf = ? AND tipo_conta = ?", (novo_saldo, self.cpf, self.tipo_conta))
        
        # Inclui o tipo de conta na transação
        cursor.execute("INSERT INTO transactions (cpf, tipo, valor, data, tipo_conta) VALUES (?, 'Depósito', ?, ?, ?)",
                (self.cpf, valor, datetime.now().strftime('%d-%m-%Y %H:%M:%S'), self.tipo_conta))

        conn.commit()
        self.show_info("Depósito realizado com sucesso!")
        conn.close()


    def consultar_extrato(self):
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()

        # Consultar o saldo
        cursor.execute("SELECT saldo FROM accounts WHERE cpf = ? AND tipo_conta = ?", (self.cpf, self.tipo_conta))
        saldo = cursor.fetchone()[0]

        # Consultar as transações
        cursor.execute("SELECT tipo, valor, data FROM transactions WHERE cpf = ? AND tipo_conta = ?", 
                    (self.cpf, self.tipo_conta))
        transacoes = cursor.fetchall()

        if transacoes:
            extrato = "Extrato de Transações:\n"
            for transacao in transacoes:
                # Exibe a data e a hora da transação corretamente
                data_formatada = datetime.strptime(transacao[2], '%d-%m-%Y %H:%M:%S').strftime('%d/%m/%Y %H:%M:%S')
                extrato += f"{transacao[0]}: R${transacao[1]:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') + f" em {data_formatada}\n"
            
            extrato += f"\nSaldo atual: R${saldo:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            self.show_info(extrato)
        else:
            self.show_info(f"Nenhuma transação encontrada.\n\nSaldo atual: R${saldo:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))


        conn.close()



    def show_info(self, text):
        self.info_display.setText(text)

    def close_app(self):
        self.close()

    def consultar_cadastro(self):
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()

        # Atualizando a consulta para considerar o tipo de conta
        cursor.execute("SELECT nome, tipo_conta, data_nascimento, endereco FROM accounts WHERE cpf = ? AND tipo_conta = ?", (self.cpf, self.tipo_conta))
        cadastro = cursor.fetchone()

        if cadastro:
            nome, tipo_conta, data_nascimento, endereco = cadastro
            info = f"Nome: {nome}\nTipo de Conta: {tipo_conta}\nData de Nascimento: {data_nascimento}\nEndereço: {endereco}"
            self.show_info(info)
        else:
            self.show_info("Cadastro não encontrado.")

        conn.close() 
