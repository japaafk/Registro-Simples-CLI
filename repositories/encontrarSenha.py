import bcrypt
from database.conexao import PegarConexao

conexao = PegarConexao()
cursor = conexao.cursor()

try:
    cursor.execute("SELECT id, user_password FROM user")
    usuarios = cursor.fetchall()

    for id_usuario, senha in usuarios:

        # Ignora senhas que já são hashes bcrypt
        if senha.startswith(("$2a$", "$2b$", "$2y$")):
            continue

        # Gera um hash para a senha antiga
        senha_hash = bcrypt.hashpw(
            senha.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        # Atualiza a senha no banco de dados
        cursor.execute("""
            UPDATE user
            SET user_password = ?
            WHERE id = ?
        """, (senha_hash, id_usuario))

    conexao.commit()
    print("Migração de senhas concluída!")

except Exception:
    conexao.rollback()
    raise

finally:
    cursor.close()
    conexao.close()