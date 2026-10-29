import sqlite3

conexao = sqlite3.connect('database.db')
cursor = conexao.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS user (
id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
user_name TEXT NOT NULL UNIQUE,
user_password TEXT NOT NULL
);''')

conexao.commit() # SALVANDO ALTERAÇÕES

def PegarConexao():
    return sqlite3.connect('database.db')
