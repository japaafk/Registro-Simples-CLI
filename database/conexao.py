import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "database.db" 
# Dessa maneira, independentemente de onde o programa seja executado, ele encontrará o banco no local correto.
# Path(__file__): identifica o caminho do arquivo Python atual.
# .resolve(): obtém seu caminho absoluto.
# .parent: identifica a pasta onde está o conexao.py.
# / "database.db": define o arquivo do banco dentro dessa pasta.

def PegarConexao():
    return sqlite3.connect(DB_PATH)

def InicializarBanco():
    conexao = PegarConexao()

    try:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL UNIQUE,
                user_password TEXT NOT NULL
            );
        """)

        conexao.commit() # SALVANDO ALTERAÇÕES
    finally:
        conexao.close() # ENCERRANDO CONEXÃO