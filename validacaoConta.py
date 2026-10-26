from conexao import PegarConexao

conexao = PegarConexao()
cursor = conexao.cursor()

def ValidarUsuario():
    usuario = False
    while not usuario:
            nome = input('\nDigite seu nome de usuário: ')
            cursor.execute('SELECT user_name FROM user WHERE user_name = ?', (nome,))
            usuario = cursor.fetchone() # RETORNA UMA TUPLA DE SOMENTE UM REGISTRO
            if not usuario:
                print('\nSeu usuário não foi encontrado no nosso banco de dados \nPor favor, tente novamente!')
                 
    if usuario:
        print(f'O usuário {usuario[0]} foi encontrado!')
        print('\n')
        print('Agora, digite sua senha para termos certeza de que é você')
        senha = input('Senha: ')
        cursor.execute('SELECT user_password FROM user WHERE user_password = ?', (senha,))
        codigo = cursor.fetchone()
        while not codigo:
            codigo = input('\nSua senha está incorreta, digite-a novamente para que possamos validar seu acesso \nSenha: ')
        print('\nConfirmando acesso...')
        print('\nAcesso confirmado!')