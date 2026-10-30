from database.conexao import PegarConexao

conexao = PegarConexao()

def ListarUsuarios():
    cursor = conexao.cursor()
    print('\nAqui seguimos com uma lista de usuários cadastrados:\n')
    cursor.execute('SELECT user_name FROM user;')
    contas = cursor.fetchall() # PASSA TODOS OS REGISTROS DA QUERY COMO UM RESULTADO DE UMA VARIÁVEL
    if not contas:
        print('\nNenhum usuário foi cadastrado ainda!')
    else:
        for conta in contas:
            print(f' - {conta[0]}') # PASSANDO POR INDEX E IGNORANDO CARACTERES DESNECESSÁRIOS

    print('\nNota: digite "sair" logo abaixo para deixar de ver esse campo')
    while True:
        tmp = input().strip().lower()
        if tmp == 'sair':
            break
        print('\nSair é a úncia opção valída, digite-a para deixar de ver a lista de usuários')
    print('\n')
    cursor.close()