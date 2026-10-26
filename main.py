def CadastroUsuario():
    try:
        print('\nParao cadastro de um usuário insira as seguintes informações:')
        nome = input('Nome de usuário: ')
        while not nome:
            nome = input('Esse trecho não pode ser vazio. Insira um nome válido: ')
        
        senha = input('Senha de usuário: ')
        while len(senha) < 3:
            senha = input('A senha de usuário deve ter ao menos 3 caracteres. Digite novamente sua senha: ')
    except (KeyboardInterrupt, EOFError):
        print('Cadastro cancelado pelo usuário')


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
Digite sua resposta: ''').lower

match escolha:
    case '1' | 'cadastrar usuario':
        CadastroUsuario()