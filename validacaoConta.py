from conexao import PegarConexao

conexao = PegarConexao()
cursor = conexao.cursor()

def ValidarUsuario():
    while True:
        nome = input('Nome: ')
        senha = input('Senha: ')

        print('\nConfimando usuário...')
        cursor.execute('SELECT id FROM user WHERE user_name = ? AND user_password = ?;', (nome, senha))
        id_usuario = cursor.fetchone()

        if id_usuario is not None:
            break

        print('\nNome de usuário ou senha inválidos. Por favor digite-os novamente!\n')

    print('\nValidação concluída com sucesso!\n')
    return id_usuario