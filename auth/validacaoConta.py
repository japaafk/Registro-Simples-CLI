import bcrypt
from database.conexao import PegarConexao

conexao = PegarConexao()
cursor = conexao.cursor()

def ValidarUsuario():
    while True:
        nome = input('Nome: ')
        senha = input('Senha: ')

        print('\nConfimando usuário...')
        cursor.execute('SELECT id, user_password FROM user WHERE user_name = ?;', (nome,))
        registro_usuario = cursor.fetchone()

        if registro_usuario is not None:
            id_usuario = registro_usuario[0]
            senha_armazenada = registro_usuario[1]

            if bcrypt.checkpw(senha.encode('utf-8'), senha_armazenada.encode('utf-8')):
                break

        print('\nNome de usuário ou senha inválidos. Por favor digite-os novamente!\n')

    print('\nValidação concluída com sucesso!\n')
    cursor.close()
    return id_usuario