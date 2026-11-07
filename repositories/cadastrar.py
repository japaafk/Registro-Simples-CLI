import bcrypt
from database.conexao import PegarConexao

conexao = PegarConexao()

def CadastroUsuario():
    cursor = conexao.cursor()
    
    try:
        while True:
            print('\n-------------------')
            print('REGISTRO DE USUÁRIO')
            print('-------------------')

            print('\nPara o cadastro de um usuário insira as seguintes informações:')
            nome = input('Nome de usuário: ').strip()
            while not nome:
                nome = input('Esse trecho não pode ser vazio.\nInsira um nome válido: ').strip()
            
            senha = input('Senha de usuário: ').strip()
            while len(senha) < 3:
                senha = input('A senha de usuário deve ter ao menos 3 caracteres.\nDigite novamente sua senha: ').strip()

            # CRIAÇÃO DE HASH PARA PROTEÇÃO DE SENHA
            senha_criptografada = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            cursor.execute('SELECT * from user WHERE user_name = ?', (nome,))
            usuario_repetido = cursor.fetchone()
            if usuario_repetido is not None:
                print('Esse nome ja existe no nosso sistema, por favor escolha outro')
                continue
            break

        cursor.execute(''' INSERT INTO user (user_name, user_password) VALUES (?, ?);
        ''', (nome, senha_criptografada))
        
        conexao.commit()
    except (KeyboardInterrupt, EOFError):
        print('Cadastro cancelado pelo usuário')
    finally:
        cursor.close()
        print('Encerrando sessão de cadastro...\n')