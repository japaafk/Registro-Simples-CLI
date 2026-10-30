from database.conexao import PegarConexao

conexao = PegarConexao()

def acharSenha():
    cursor = conexao.cursor()

    print('\nEsqueceu sua senha? Digite seu nome de usuário para encontrá-la')
    nome_usuario = input('Nome: ')

    cursor.execute('SELECT user_password FROM user WHERE user_name = ?', (nome_usuario,))
    senha_encontra = cursor.fetchone()

    if senha_encontra is not None:
        senha = senha_encontra[0]
        cursor.close()
        return senha

    cursor.close()
    print('Seu usuário não foi rastreado no nosso banco, certifique-se de que digitou o nome correto')