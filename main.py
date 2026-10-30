from repositories.cadastrar import CadastroUsuario
from repositories.listagem import ListarUsuarios
from repositories.alterarConta import AlterarUsuario
from repositories.deletarUsuario import RemoverUsuario
from database.conexao import InicializarBanco

InicializarBanco()

texto = 'CRUD DE USUÁRIO'
while True:
    print('-'*25)
    print(f'{texto:^25}')
    print('-'*25)
    print('\n')
    print('Bem vindo, qual ação gostaria de executar:')
    escolha = input('''1- Cadastrar Usuário
    2- Alterar Usuário
    3- Remover Usuário
    4- Listar Usuários
    0- Sair\n
    Digite sua resposta: ''').lower()

    match escolha:
        case '1' | 'cadastrar usuario':
            CadastroUsuario()
        case '2' | 'alterar usuario':
            AlterarUsuario()
        case '3' | 'remover usuario':
            RemoverUsuario()
        case '4' | 'listar usuarios':
            ListarUsuarios()
        case '0' | 'sair':
            print('Encerrando programa...')
            break
        case _:
            print('Digite uma resposta válida!\n')
    print('Obrigado por utilizar')