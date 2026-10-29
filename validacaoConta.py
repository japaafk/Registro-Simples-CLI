from conexao import PegarConexao

conexao = PegarConexao()
cursor = conexao.cursor()

def ValidarUsuario():
    id_usuario = False
    while not id_usuario:
            nome = input('\nDigite seu nome de usuário: ')
            cursor.execute('SELECT id FROM user WHERE user_name = ?', (nome,))
            id_usuario = cursor.fetchone() # RETORNA UMA TUPLA DE SOMENTE UM REGISTRO
            if not id_usuario:
                print('\nSeu usuário não foi encontrado no nosso banco de dados \nPor favor, tente novamente!')
                 
    if id_usuario:
        cursor.execute('SELECT user_password FROM user WHERE id = ?', id_usuario)
        senha_bd = cursor.fetchone()
        print(f'O usuário {nome} foi encontrado!')
        print('\n')
        print('Agora, digite sua senha para termos certeza de que é você')
        senha = input('Senha: ')
        while senha_bd[0] != senha:
            if senha_bd != senha:
                senha = input('\nSua senha está incorreta, digite-a novamente para que possamos validar seu acesso. \nSenha: ')

    print('\nConfirmando acesso...')
    print('\nAcesso confirmado!')
    return id_usuario