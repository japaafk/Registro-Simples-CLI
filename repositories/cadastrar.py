from database.conexao import PegarConexao

conexao = PegarConexao()

def CadastroUsuario():
    cursor = conexao.cursor()
    
    try:
        while True:
            print('\nPara o cadastro de um usuário insira as seguintes informações:')
            nome = input('Nome de usuário: ')
            while not nome:
                nome = input('Esse trecho não pode ser vazio.\nInsira um nome válido: ')
            
            senha = input('Senha de usuário: ')
            while len(senha) < 3:
                senha = input('A senha de usuário deve ter ao menos 3 caracteres.\nDigite novamente sua senha: ')

            cursor.execute('SELECT * from user WHERE user_name = ?', (nome,))
            usuario_repetido = cursor.fetchone()
            if usuario_repetido is not None:
                print('Esse nome ja existe no nosso sistema, por favor escolha outro')
                continue
            break

        cursor.execute(''' INSERT INTO user (user_name, user_password) VALUES (?, ?);
        ''', (nome, senha))
        
        conexao.commit()
    except (KeyboardInterrupt, EOFError):
        print('Cadastro cancelado pelo usuário')
    finally:
        cursor.close()
        print('\n-----------------------------')
        print('Encerrando sessão de cadastro')