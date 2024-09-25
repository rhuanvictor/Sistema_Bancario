import sqlite3  # Certifique-se de importar sqlite3

def init_db():
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    # Criação da tabela 'accounts'
    cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cpf TEXT NOT NULL,
                        senha TEXT NOT NULL,
                        nome TEXT NOT NULL,
                        data_nascimento TEXT NOT NULL,
                        endereco TEXT NOT NULL,
                        tipo_conta TEXT NOT NULL,
                        saldo REAL DEFAULT 0.0,
                        saques_diarios INTEGER DEFAULT 0,
                        ultimo_saque TEXT,
                        UNIQUE(cpf, tipo_conta)  -- Garante que não pode haver mais de uma conta do mesmo tipo para o mesmo CPF
                     )''')

    # Criação da tabela 'transactions'
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cpf TEXT,
                        tipo TEXT,
                        valor REAL,
                        data TEXT,
                        tipo_conta TEXT  -- Adiciona o tipo de conta aqui
                     )''')

    # Commit e fechamento da conexão
    conn.commit()
    conn.close()
