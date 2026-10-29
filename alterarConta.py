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

    print('\n')

    # VALIDAÇÃO DAS CREDENCIAIS DO USUÁRIO
    id = ValidarUsuario()
    identificador = id[0]

    escolha = None
    while escolha not in ('0', 'sair'):
        print('\nIniciando processo de alteração dos dados de usuário...')
        print('Escoloha o que você gostaria de alterar:')
        print('1- Nome de usuário \n2- Senha \n0- Cancelar alteração')
        escolha = input('\nDigite sua resposta: ').lower()

        match escolha:
            case '1' | 'nome de usuario':
                try:
                    novo_nome = input('Insira seu novo nome: ')
                    while not novo_nome:
                        novo_nome = input('Esse trecho não pode ser vazio.\nInsira um nome válido: ')
                    print('\nConfirme essa alteração digitando sua senha')
                    senha = input('Senha: ')
                    cursor.execute('SELECT user_password FROM user WHERE id = ?', id)
                    senha_tupla = cursor.fetchone()
                    senha_bd = senha_tupla[0]
                    while senha_bd != senha:
                        senha = input('\nSenha incorreta. Digite-a novamente para que possamos confirmar as alterações \nSenha: ')
                    print('Senha confirmada!')
                    print('\nConfirmando alterações...')
                    cursor.execute('UPDATE user SET user_name = ? WHERE id = ?', (novo_nome, identificador))
                    conexao.commit()
                    print('Alterações salvas!')
                except (KeyboardInterrupt, EOFError):
                    print('Alteração interrompida')
                    
            case '2' | 'senha':
                try:
                    senha = input('Insira sua nova senha: ')
                    while len(senha) < 3:
                        senha = input('A senha de usuário deve ter ao menos 3 caracteres.\nDigite corretamente sua nova senha: ')
                    confirmar_alteracao = input('Deseja confirmar essas alterações? (s/n) \nResposta: ')
                    while confirmar_alteracao not in ('s', 'n'):
                        confirmar_alteracao = input('É necessário que seja uma resposta válida. Confirme Digitando s(sim) ou n(não) \nResposta: ')
                    if confirmar_alteracao == 's':
                        print('\nConfirmando alterações...')
                        cursor.execute('UPDATE user SET user_password = ? WHERE id = ?', (senha, identificador))
                        conexao.commit()  
                        print('Alterações salvas!') 
                    elif confirmar_alteracao == 'n':
                        print('Alteração cancelada pelo usuário')
                except (KeyboardInterrupt, EOFError):
                    print('\nAlteração interrompida')
        
            case '0' | 'Cancelar alteração':
                print('Alteração cancelada')
            case _:
                    print('Forneça uma resposta válida!')
    print('\nRetornando para o menu principal...\n')