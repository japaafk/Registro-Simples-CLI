from conexao import PegarConexao
from validacaoConta import ValidarUsuario

conexao = PegarConexao()
cursor = conexao.cursor()

def RemoverUsuario():
    print('------------------')
    print('REMOÇÃO DE USUÁRIO')
    print('------------------\n')
    

    # LISTAGEM DE USUÁRIO SEM CARREGAMENTO SIMULTÂNEO DE TODOS OS USUÁRIOS NA MEMÓRIA
    cursor.execute('SELECT user_name FROM user ORDER BY user_name;')
    contas = cursor.fetchmany(2) # PERMITE RECUPERAR UMA LISTA LIMITADA DE REGISTROS POR CHAMADA
    while True: 
        print('Lista de usuário(s)')
        print('------------------')
        for conta in contas:
            print(f' - {conta[0]}')
        print('Não encontrou seu nome aqui?!')
        load_users = input('Quer acessar a próxima página de usuários? (s/n)')
        if load_users == 'n':
            break
        elif load_users == 's':
            contas = cursor.fetchmany(2)
        else:
            print('Digite uma resposta válida!')
    print('\n')
    while True:
        escolha = input('Tem certeza que deseja remover um usuário do nosso banco de dados? (s/n) \nResposta: ').strip().lower()
        if escolha != 's':
            print('Resposta inválida. O campo precisa ser preenchido com s(sim) ou n(não)')
            continue      
        elif escolha == 'n':
            print('Remoção cancelada')
            break

        while True:
            id = ValidarUsuario()
            print('ID encontrado, preparando remoção de usuário...')
            cursor.execute('DELETE FROM user WHERE id = ?;', id)
            conexao.commit()
            break
        print('\nRemoção realizada com sucesso.')
        break
    print('\nRetornando para o menu principal...\n')