from repositories.cadastrar import CadastroUsuario
from repositories.listagem import ListarUsuarios
from repositories.alterarConta import AlterarUsuario
from repositories.deletarUsuario import RemoverUsuario
from menu.opcaoMenu import opcoesMenu
from database.conexao import InicializarBanco

InicializarBanco()

texto = 'CRUD DE USUÁRIO'
while True:
    print('-'*25)
    print(f'{texto:^25}')
    print('-'*25)
    print('\n')
    print('Bem vindo, qual ação gostaria de executar:')
    escolha = input('''
    1- Cadastrar Usuário
    2- Alterar Usuário
    3- Remover Usuário
    4- Listar Usuários
    0- Sair\n
    Digite sua resposta: ''').lower().strip()

    opcoes = {
        '1': (r'\bcadastrar\s+usu[aá]rio\b', '1'),
        '2': (r'\balterar\s+usu[aá]rio\b', '2'),
        '3': (r'\bremover\s+usu[aá]rio\b', '3'),
        '4': (r'\blistar\s+usu[aá]rios?\b', '4'),
        '0': (r'\bsair\b', '0')
    }

    resposta_menu = opcoesMenu(escolha, opcoes)
    # trabalhar na recepção da funcao menu e quando retornar none

    match resposta_menu:
        case '1':
            CadastroUsuario()
        case '2':
            AlterarUsuario()
        case '3':     
            RemoverUsuario()
        case '4':
            ListarUsuarios()
        case '0':
            print('\nEncerrando programa... \nObrigado por utilizar')
            break
        case _:
            print('Digite uma resposta válida!\n')