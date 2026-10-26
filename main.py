from cadastrar import CadastroUsuario
from listagem import ListarUsuarios
from alterarConta import AlterarUsuario

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
    case '4' | 'listar usuarios':
        ListarUsuarios()