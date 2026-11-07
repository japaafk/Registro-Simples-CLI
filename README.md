# Registro Simples CLI

Sistema de cadastro e gerenciamento de usuários desenvolvido em **Python**, com interface pelo **terminal**, persistência em **SQLite** e proteção de senhas com **bcrypt**.

O projeto implementa um **CRUD** completo: cadastrar, consultar, alterar e remover usuários. Foi construído de forma incremental como exercício prático de programação, banco de dados, validação de entradas, testes automatizados e versionamento com Git e GitHub.

## Índice

- [Sobre o projeto](#sobre-o-projeto)
- [Tecnologias utilizadas](#tecnologias-utilizadas)
- [Funcionamento do CRUD](#funcionamento-do-crud)
- [Leitura de entradas com regex](#leitura-de-entradas-com-regex)
- [Organização do código](#organização-do-código)
- [Banco de dados](#banco-de-dados)
- [Proteção de senhas com bcrypt](#proteção-de-senhas-com-bcrypt)
- [Como executar](#como-executar)
- [Testes automatizados](#testes-automatizados)
- [Integração contínua](#integração-contínua)
- [Desenvolvimento e versionamento](#desenvolvimento-e-versionamento)
- [Limitações atuais](#limitações-atuais)
- [Licença](#licença)

## Sobre o projeto

O Registro Simples CLI permite administrar contas localmente, sem precisar de um servidor de banco de dados ou de uma interface gráfica. As interações acontecem por perguntas e respostas no terminal, e os registros permanecem salvos entre as execuções.

A autenticação é utilizada para autorizar alterações e exclusões da própria conta. Cadastro e listagem ficam disponíveis no menu principal, sem login prévio. O sistema não possui interface web, API HTTP, sessões de login ou níveis de permissão.

O desenvolvimento reúne práticas trabalhadas ao longo do projeto:

- Funções, módulos, laços de repetição e seleção de opções com `match/case`.
- Consultas SQL parametrizadas e persistência de alterações com `commit()`.
- Tratamento de nomes duplicados, entradas vazias e credenciais incorretas.
- Separação entre menu, autenticação, acesso ao banco e operações de usuários.
- Testes de fluxos interativos com entradas simuladas e banco isolado.
- Uso de branches, commits, pull requests e integração de alterações à `main`.
- Substituição do armazenamento de senhas em texto puro por hashes bcrypt.

## Tecnologias utilizadas

| Tecnologia | Papel no projeto |
| --- | --- |
| **Python** | Linguagem da aplicação e dos testes; Python 3.13 é a versão configurada na integração contínua. |
| **SQLite / `sqlite3`** | Banco relacional local e acesso a consultas SQL pela biblioteca padrão do Python. |
| **`pathlib`** | Localização do arquivo do banco a partir do caminho do módulo de conexão. |
| **Regex / `re`** | Reconhecimento de comandos textuais e opções numéricas nos menus, com padrões para variações de acentuação e espaçamento e comparação sem diferenciar maiúsculas de minúsculas. |
| **bcrypt 5.0.0** | Geração de hashes de senha, criação de salt e verificação de credenciais. |
| **pytest 9.2.0** | Execução dos testes, fixtures, parametrização e simulação de entradas com `monkeypatch`. |
| **Git** | Histórico de alterações, branches e merges. |
| **GitHub** | Hospedagem do repositório e integração por pull requests. |
| **GitHub Actions** | Execução automatizada da suíte em pull requests destinados à `main`. |

As dependências externas estão fixadas em [`requirements.txt`](requirements.txt). `sqlite3`, `pathlib` e `re` fazem parte da biblioteca padrão e não exigem instalação adicional. A aplicação utiliza funções e SQL diretamente, sem framework web ou ORM.

## Funcionamento do CRUD

CRUD é a sigla para **Create, Read, Update e Delete**, as quatro operações básicas de gerenciamento de dados.

| Operação | Opção no menu | Comportamento |
| --- | --- | --- |
| **Create — Criar** | `1` — Cadastrar Usuário | Recebe nome e senha, valida os dados, gera o hash e insere a conta. |
| **Read — Consultar** | `4` — Listar Usuários | Exibe os nomes cadastrados ou informa que não há registros. |
| **Update — Atualizar** | `2` — Alterar Usuário | Valida as credenciais e permite modificar o nome ou a senha. |
| **Delete — Excluir** | `3` — Remover Usuário | Solicita confirmação, valida as credenciais e exclui a conta autenticada. |

Ao iniciar, `main.py` chama `InicializarBanco()` e apresenta o menu em um laço. Depois de cada operação, o usuário pode escolher outra ação. A opção `0` ou `sair` encerra o programa.

### Cadastro

O nome não pode ficar vazio e a senha deve ter pelo menos três caracteres. Espaços no início e no fim desses campos são removidos. Se o nome já existir, o sistema solicita um novo cadastro. Antes de salvar, a senha é transformada em um hash bcrypt.

### Listagem

A consulta exibe somente os nomes dos usuários, sem senhas ou hashes. Digite `sair` para retornar ao menu. Nessa tela, o comando aceita letras maiúsculas e espaços nas extremidades.

### Alteração

Após informar nome e senha válidos, é possível escolher:

- `1`: alterar o nome, confirmando novamente a senha e verificando se o novo nome já existe.
- `2`: alterar a senha, respeitando o mínimo de três caracteres e confirmando com `s` ou cancelando com `n`.
- `0`: sair do submenu de alteração e retornar ao menu principal.

A nova senha também é salva como hash. A validação retorna o **ID inteiro** da conta, usado para identificar o registro nas consultas de atualização.

### Remoção

O sistema apresenta os nomes em ordem alfabética, em grupos de dois registros por meio de `fetchmany(2)`. Responder `s` solicita a próxima página; `n` encerra a navegação pela lista.

Em seguida, outra pergunta solicita a confirmação da exclusão. Responder `n` cancela a operação. Ao responder `s`, o usuário deve informar credenciais válidas, e somente a conta autenticada é removida pelo seu ID.

## Leitura de entradas com regex

**Regex (expressões regulares)** são padrões usados para reconhecer trechos de texto. No projeto, a função `opcoesMenu()`, em [`menu/opcaoMenu.py`](menu/opcaoMenu.py), usa o módulo `re` da biblioteca padrão do Python para interpretar as respostas do menu principal e do submenu de alteração, retornando a chave da opção correspondente ou `None` quando nenhum padrão é reconhecido.

Além dos números, é possível digitar comandos como `cadastrar usuário`, `alterar usuario`, `listar usuários` e `sair`; no submenu, são reconhecidos `nome de usuário`, `senha` e `cancelar alteração`. O uso de `re.IGNORECASE` ignora diferenças entre maiúsculas e minúsculas, enquanto os padrões aceitam variações específicas de acentuação, múltiplos espaços entre palavras e, na listagem, singular ou plural.

O `re.search()` encontra comandos textuais mesmo dentro de uma frase, com limites de palavra (`\b`) que impedem, por exemplo, que `sairmos` seja interpretado como `sair`. Já o `re.fullmatch()` exige que a entrada numérica inteira corresponda à opção, evitando aceitar `10` ou `abc3` como escolhas válidas. Isso torna a leitura das entradas mais flexível e consistente e centraliza a lógica de reconhecimento em uma função reutilizável. Esse recurso interpreta comandos dos menus; as regras de nome e senha continuam nos respectivos fluxos.

## Organização do código

```text
Registro-Simples-CLI/
├── .github/
│   └── workflows/
│       └── test.yml          # Testes automatizados em pull requests
├── auth/
│   └── validacaoConta.py     # Validação de credenciais com bcrypt
├── database/
│   ├── conexao.py            # Caminho do banco, conexões e criação da tabela
│   └── database.db           # Arquivo SQLite persistente
├── menu/
│   └── opcaoMenu.py          # Reconhecimento das opções dos menus com regex
├── repositories/
│   ├── cadastrar.py          # Cadastro de usuários
│   ├── listagem.py           # Consulta e exibição dos nomes
│   ├── alterarConta.py       # Alteração de nome e senha
│   └── deletarUsuario.py     # Exclusão de contas
├── tests/
│   └── test_crud.py          # Suíte de testes com pytest
├── .gitignore
├── LICENSE
├── main.py                  # Ponto de entrada e menu principal
├── README.md
└── requirements.txt
```

A organização é modular e procedural. `main.py` encaminha as escolhas às funções de `repositories/`, que concentram a interação de cada operação e suas consultas SQL. `menu/` centraliza o reconhecimento das opções por regex, reutilizado no menu principal e no submenu de alteração. `auth/` centraliza a validação de credenciais, enquanto `database/` define o acesso ao SQLite.

## Banco de dados

O arquivo utilizado é `database/database.db`. Seu caminho é calculado com `Path(__file__).resolve().parent`, evitando depender da pasta de onde o programa foi chamado.

A inicialização cria a tabela `user` caso ela ainda não exista:

```sql
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT NOT NULL UNIQUE,
    user_password TEXT NOT NULL
);
```

| Campo | Finalidade |
| --- | --- |
| `id` | Identificador inteiro gerado automaticamente para cada conta. |
| `user_name` | Nome obrigatório e único. |
| `user_password` | Hash bcrypt armazenado como texto nas contas criadas ou atualizadas pela versão atual. |

As consultas recebem valores separadamente por marcadores `?`, em vez de concatenar entradas do usuário ao SQL. As operações de cadastro, alteração e exclusão usam `commit()` para persistir os dados.

O arquivo `database.db` está versionado no repositório, portanto uma cópia clonada pode conter registros anteriores. A inicialização preserva os dados existentes e não migra automaticamente as senhas de versões antigas.

## Proteção de senhas com bcrypt

Inicialmente, as senhas eram armazenadas em texto puro. A evolução incorporada pela branch `feature/encrypt` passou a proteger o cadastro, a troca de senha e a autenticação com bcrypt.

Apesar do nome da branch, o mecanismo utilizado é **hash de senha**, sem uma operação de descriptografia para recuperar a senha original.

### Geração e armazenamento

No cadastro e na troca de senha, a aplicação converte a entrada para bytes UTF-8, gera um salt com `bcrypt.gensalt()` e calcula o hash:

```python
senha_hash = bcrypt.hashpw(
    senha.encode('utf-8'),
    bcrypt.gensalt()
).decode('utf-8')
```

O salt é gerado a cada chamada e faz parte do resultado armazenado. Assim, duas contas que utilizem a mesma senha podem ter hashes diferentes. O banco recebe o hash, e não a senha digitada.

### Verificação de credenciais

A autenticação busca o ID e o hash pelo nome de usuário. Depois, verifica a senha informada com:

```python
bcrypt.checkpw(
    senha.encode('utf-8'),
    senha_armazenada.encode('utf-8')
)
```

Se a verificação for bem-sucedida, `ValidarUsuario()` retorna o ID da conta. Caso contrário, solicita novamente as credenciais. Esse mesmo mecanismo confirma a senha antes de alterar o nome.

## Como executar

Utilize **Python 3.13**, versão adotada pelo workflow do projeto, e Git para clonar o repositório. Não é necessário instalar um servidor SQLite.

### 1. Clonar o repositório

```bash
git clone https://github.com/japaafk/Registro-Simples-CLI.git
cd Registro-Simples-CLI
```

### 2. Criar um ambiente virtual

```bash
python -m venv .venv
```

Ative no **Windows PowerShell**:

```powershell
.\.venv\Scripts\Activate.ps1
```

Ou no **Linux/macOS**:

```bash
source .venv/bin/activate
```

### 3. Instalar as dependências

```bash
python -m pip install -r requirements.txt
```

### 4. Iniciar a aplicação

```bash
python main.py
```

O menu oferece as opções `1` para cadastro, `2` para alteração, `3` para remoção, `4` para listagem e `0` para saída. Para experimentar o fluxo completo, cadastre uma conta, consulte a lista, altere seus dados e depois remova a conta usando as credenciais atualizadas.

No Windows, se preferir não ativar o ambiente virtual, utilize diretamente `.\.venv\Scripts\python.exe` no lugar de `python` nos comandos de instalação, execução e testes.

## Testes automatizados

A suíte está em [`tests/test_crud.py`](tests/test_crud.py) e utiliza **pytest**, conforme a evolução do projeto. Cada teste recebe um banco SQLite isolado em memória, com entradas de terminal simuladas e captura da saída. As conexões são fechadas e os módulos restaurados ao final de cada teste, sem utilizar o banco persistente da aplicação.

Os cenários cobrem cadastro, rejeição de nome vazio e senha curta, nomes duplicados, listagem, autenticação, alteração de dados, cancelamentos, exclusão e repetição de operações. Também verificam a rejeição da senha anterior após uma troca e que a senha cadastrada não seja armazenada em texto puro.

Execute a suíte completa na raiz do projeto:

```bash
python -m pytest tests -v
```

Também é possível executar o próprio arquivo:

```bash
python tests/test_crud.py
```

Para selecionar um teste específico:

```bash
python -m pytest tests/test_crud.py::test_cadastrar_usuario -v
```

Na validação local realizada em **6 de novembro de 2026**, com Python 3.13, pytest 9.2.0 e bcrypt 5.0.0, os **28 casos passaram**. Esse resultado representa os cenários existentes, não uma cobertura completa de todos os comportamentos possíveis.

O comentário no início do arquivo de testes ainda menciona a antiga falha de armazenamento em texto puro; essa observação é histórica e não corresponde ao resultado atual. O teste específico de armazenamento verifica que o valor difere da senha original, mas não valida sozinho todo o formato do hash bcrypt.

## Integração contínua

O workflow [`test.yml`](.github/workflows/test.yml), chamado **Testes Python**, executa a suíte em pull requests com destino à `main` nos eventos:

- Abertura (`opened`).
- Atualização dos commits do PR (`synchronize`).
- Reabertura (`reopened`).
- Mudança para pronto para revisão (`ready_for_review`).

A execução usa `ubuntu-latest`, Python 3.13, instalação pelo `requirements.txt` e o comando `python -m pytest tests -v`. O job possui limite de cinco minutos e permissão `contents: read`.

Os testes locais podem ser executados antes de qualquer commit. O workflow atual depende dos eventos de pull request: salvar arquivos ou enviar um push sem PR correspondente não dispara essa configuração. A execução no GitHub e suas regras de bloqueio de merge dependem das configurações do repositório.

## Desenvolvimento e versionamento

O projeto foi construído por etapas, combinando implementação, revisão e ajustes conforme novos comportamentos eram adicionados. O histórico registra a seguinte evolução:

1. Criação do ponto de entrada, listagem e conexão com SQLite.
2. Implementação do cadastro, validações e restrição a nomes duplicados.
3. Inclusão da alteração de dados, autenticação e remoção de usuários.
4. Refatoração da validação e organização dos arquivos por funcionalidade.
5. Inclusão do menu repetitivo, testes automatizados e correções dos fluxos de confirmação.
6. Atualização dos testes para acompanhar o uso de `sair`, novas tentativas e cancelamentos, com execução em pull requests.
7. Inclusão temporária da consulta de senha e posterior retirada dessa funcionalidade com a adoção do bcrypt.
8. Ajustes das consultas e dos testes para o retorno do ID inteiro na autenticação.
9. Inclusão de regex para reconhecer comandos nos menus e ampliação dos testes de entradas textuais e numéricas.

### Branches, commits e pull requests

A `main` reúne as alterações integradas. O histórico utiliza branches dedicadas a funcionalidades, correções e refatorações, por exemplo:

| Branch | Trabalho registrado |
| --- | --- |
| `feature/update` | Alteração de dados dos usuários. |
| `feature/delete` | Remoção de contas. |
| `refactor/validation` | Simplificação da validação. |
| `fix/duplicate` | Correções relacionadas a nomes duplicados. |
| `fix/delete` | Ajuste da ordem de validação na exclusão. |
| `feature/find_password` | Recurso histórico de consulta de senha, retirado do menu posteriormente. |
| `feature/encrypt` | Incorporação de hashes bcrypt e adaptação dos fluxos de credenciais. |
| `feature/regex` | Reconhecimento de opções dos menus com expressões regulares, criação de `menu/opcaoMenu.py` e testes das novas entradas. |

Os commits usam frequentemente prefixos como `feat:`, `fix:`, `refactor:`, `test:`, `chore:` e `style:` para indicar a finalidade da mudança. O histórico contém tanto merges pelo terminal quanto merges de pull requests no GitHub, incluindo o PR #8 da incorporação do bcrypt e o PR #9 da inclusão de regex nos menus.

O fluxo de desenvolvimento consiste em criar uma branch, implementar as alterações localmente, executar os testes, registrar commits, enviar a branch e abrir um pull request para a `main`. Após o merge no GitHub, a cópia local pode ser atualizada com:

```bash
git switch main
git pull --ff-only origin main
```

O `.gitignore` exclui ambientes virtuais e arquivos compilados do Python. O histórico consultado ainda não possui tags de versão; a evolução está registrada pelos commits e merges.

## Limitações atuais

O projeto tem finalidade de estudo e ainda apresenta pontos para evolução:

- A senha é digitada com `input()`, portanto fica visível no terminal. A regra mínima atual é de apenas três caracteres.
- A autenticação repete as perguntas até receber credenciais válidas, sem opção própria de cancelamento ou limite de tentativas. Com o banco vazio, esse fluxo não consegue concluir normalmente.
- Os comandos reconhecidos dependem dos padrões de cada menu: no submenu de alteração, `0` ou `cancelar alteração` permitem sair, inclusive com as variações previstas de maiúsculas, acentuação e espaços. O comando `sair` não é reconhecido nesse submenu.
- O regex busca comandos dentro do texto, sem interpretar a intenção da frase. Se uma entrada contiver mais de uma opção reconhecida, a função retorna a primeira correspondência na ordem do dicionário de opções.
- O tratamento de interrupções e o fechamento de conexões não são uniformes entre todos os módulos; algumas conexões permanecem abertas durante a sessão.
- A suíte não cobre todos os casos de paginação, autenticação com banco vazio, comandos ambíguos e entradas extremas.

Esses pontos delimitam o comportamento atual e oferecem oportunidades de evolução sem mudar o propósito didático do repositório.

## Licença

Este projeto está disponível sob a **licença MIT**. Consulte o arquivo [LICENSE](LICENSE) para os termos de uso, modificação e distribuição.
