import bcrypt
from database.conexao import PegarConexao
from auth.validacaoConta import ValidarUsuario
from menu.opcaoMenu import opcoesMenu

conexao = PegarConexao()

def AlterarUsuario():
    cursor = conexao.cursor()

    print('\n--------------------')
    print('ALTERAÇÃO DE USUÁRIO')
    print('--------------------')

    print('\nTABELA DE USUÁRIOS')
    print('------------------')
    cursor.execute('SELECT user_name FROM user;')
    contas = cursor.fetchall()
    for conta in contas:
        print(f' - {conta[0]}')

    print('\nValide suas credencias antes de fazer qualquer alteração')

    # VALIDAÇÃO DAS CREDENCIAIS DO USUÁRIO
    identificador = ValidarUsuario()

    resposta_menu = None
    while resposta_menu not in ('0', 'sair'):
        print('\nIniciando processo de alteração dos dados de usuário...')
        print('Escoloha o que você gostaria de alterar:')
        print('1- Nome de usuário \n2- Senha \n0- Cancelar alteração')
        escolha = input('\nDigite sua resposta: ').lower().strip()

        opcoes = {
            '1': (r'\bnome\s+de\s+usu[aá]rio\b', '1'),
            '2': (r'\bsenha\b', '2'),
            '0': (r'\bcancelar\s+altera[cç][aã]o\b', '0')
        }

        resposta_menu = opcoesMenu(escolha, opcoes)

        match resposta_menu:
            case '1':
                try:
                    while True:
                        novo_nome = input('Insira seu novo nome: ').strip()
                        while not novo_nome:
                            novo_nome = input('Esse trecho não pode ser vazio.\nInsira um nome válido: ').strip()

                        print('\nConfirme essa alteração digitando sua senha')
                        senha = input('Senha: ')
                        cursor.execute('SELECT user_password FROM user WHERE id = ?', (identificador,))
                        senha_bd = cursor.fetchone()[0]
                        
                        while not bcrypt.checkpw(senha.encode('utf-8'), senha_bd.encode('utf-8')):
                            senha = input('\nSenha incorreta. Digite-a novamente para que possamos confirmar as alterações \nSenha: ')
                            
                        print('Senha confirmada!')
                        print('\nConfirmando alterações...')

                        # VERIFICAÇÃO DO NOME NO BANCO DE DADOS
                        cursor.execute('SELECT * FROM user WHERE user_name = ?', (novo_nome,))
                        usuario_existente = cursor.fetchone()
                        if usuario_existente is not None:
                            print('Esse nome ja existe no nosso sistema, por favor escolha outro')
                            continue

                        break
                    cursor.execute('UPDATE user SET user_name = ? WHERE id = ?', (novo_nome, identificador))
                    conexao.commit()
                    print('Alterações salvas!')
                except (KeyboardInterrupt, EOFError):
                    print('Alteração interrompida')
                    
            case '2':
                try:
                    senha = input('Insira sua nova senha: ').strip()
                    while len(senha) < 3:
                        senha = input('A senha de usuário deve ter ao menos 3 caracteres.\nDigite corretamente sua nova senha: ').strip()
                    confirmar_alteracao = input('Deseja confirmar essas alterações? (s/n) \nResposta: ')

                    while confirmar_alteracao not in ('s', 'n'):
                        confirmar_alteracao = input('É necessário que seja uma resposta válida. Confirme Digitando s(sim) ou n(não) \nResposta: ')

                    if confirmar_alteracao == 's':
                        print('\nConfirmando alterações...')

                        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                        cursor.execute('UPDATE user SET user_password = ? WHERE id = ?', (senha_hash, identificador))
                        conexao.commit()  
                        print('Alterações salvas!') 
                    elif confirmar_alteracao == 'n':
                        print('Alteração cancelada pelo usuário')
                except (KeyboardInterrupt, EOFError):
                    print('\nAlteração interrompida')
        
            case '0':
                print('Alteração cancelada')
            case _:
                    print('Forneça uma resposta válida!')
    cursor.close()
    print('\nRetornando para o menu principal...\n')