from conexao import PegarConexao

conexao = PegarConexao()
cursor = conexao.cursor()

def CadastroUsuario():
    try:
        print('\nPara o cadastro de um usuário insira as seguintes informações:')
        nome = input('Nome de usuário: ')
        while not nome:
            nome = input('Esse trecho não pode ser vazio.\nInsira um nome válido: ')
        
        senha = input('Senha de usuário: ')
        while len(senha) < 3:
            senha = input('A senha de usuário deve ter ao menos 3 caracteres.\nDigite novamente sua senha: ')

        cursor.execute(''' INSERT INTO user (user_name, user_password) VALUES (?, ?);
        ''', (nome, senha))

        conexao.commit()
    except (KeyboardInterrupt, EOFError):
        print('Cadastro cancelado pelo usuário')