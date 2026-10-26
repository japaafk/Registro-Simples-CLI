from conexao import PegarConexao
from validacaoConta import ValidarUsuario

conexao = PegarConexao()
cursor = conexao.cursor()

def AlterarUsuario():

    print('\nTABELA DE USUÁRIOS')
    print('------------------')
    cursor.execute('SELECT user_name FROM user;')
    contas = cursor.fetchall()
    for conta in contas:
        print(f' - {conta[0]}')

    # VALIDAÇÃO DAS CREDENCIAIS DO USUÁRIO
    ValidarUsuario()

    print('Iniciando processo de alteração dos dados de usuário')