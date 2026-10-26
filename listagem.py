from conexao import PegarConexao

conexao = PegarConexao()
cursor = conexao.cursor()

def ListarUsuarios():
    print('Aqui seguimos com uma lista de usuários cadastrados:')
    cursor.execute('SELECT user_name FROM user;')
    contas = cursor.fetchall() # PASSA A QUERY COMO UM RESULTADO DE UMA VARIÁVEL
    for conta in contas:
        print(f' - {conta[0]}') # PASSANDO POR INDEX E IGNORANDO CARACTERES DESNECESSÁRIOS