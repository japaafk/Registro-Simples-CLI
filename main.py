from repositories.cadastrar import CadastroUsuario
from repositories.listagem import ListarUsuarios
from repositories.alterarConta import AlterarUsuario
from repositories.deletarUsuario import RemoverUsuario
from database.conexao import InicializarBanco

InicializarBanco()

texto = 'CADASTRO DE USUÁRIO'
print('-'*25)
print(f'{texto:^25}')
print('-'*25)
print('\n')
print('Bem vindo, qual ação gostaria de executar:')
escolha = input('''1- Cadastrar Usuário
2- Alterar Usuário
3- Remover Usuário
4- Listar Usuários\n
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