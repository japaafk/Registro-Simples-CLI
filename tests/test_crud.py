"""Testes isolados do CRUD, executados com pytest.

Execute a partir da raiz do projeto:
    python tests/test_crud.py
    python tests/test_crud.py -k test_cadastrar_usuario
    python -m pytest tests -v
    python -m pytest tests/test_crud.py::test_cadastrar_usuario -v

O teste de armazenamento da senha permanece falhando enquanto a aplicação
armazenar senhas em texto puro, inclusive no GitHub Actions.
"""

import importlib
import io
import runpy
import sqlite3
import sys
import uuid
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace

import pytest

RAIZ = Path(__file__).resolve().parents[1]
# A execução direta adiciona apenas a pasta tests ao caminho de importação.
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from database import conexao


MODULOS = {
    "auth": "auth.validacaoConta",
    "cadastro": "repositories.cadastrar",
    "listagem": "repositories.listagem",
    "alteracao": "repositories.alterarConta",
    "remocao": "repositories.deletarUsuario",
}


@pytest.fixture
def crud(monkeypatch):
    uri = f"file:teste_{uuid.uuid4().hex}?mode=memory&cache=shared"
    conexoes = []
    anteriores = {}
    atributos_anteriores = {}
    ausente = object()

    def nova_conexao():
        connection = sqlite3.connect(uri, uri=True, timeout=1)
        conexoes.append(connection)
        return connection

    def executar(funcao, respostas=()):
        entradas = iter(respostas)
        saida = io.StringIO()

        def responder(prompt=""):
            try:
                resposta = next(entradas)
            except StopIteration:
                pytest.fail(
                    "A função pediu entradas além das previstas. "
                    "Verifique o cancelamento ou o retorno ao menu."
                )
            # Instâncias dessas exceções simulam o cancelamento pelo usuário.
            if isinstance(resposta, (EOFError, KeyboardInterrupt)):
                raise resposta
            return resposta

        with monkeypatch.context() as contexto:
            contexto.setattr("builtins.input", responder)
            with redirect_stdout(saida):
                resultado = funcao()

        return resultado, saida.getvalue()

    try:
        # Esta conexão mantém o banco vivo durante o teste.
        banco = nova_conexao()
        monkeypatch.setattr(conexao, "PegarConexao", nova_conexao)
        conexao.InicializarBanco()

        # Isola também os cursores criados na importação dos módulos.
        for nome in MODULOS.values():
            pacote, atributo = nome.rsplit(".", 1)
            pai = importlib.import_module(pacote)
            atributos_anteriores[nome] = getattr(
                pai, atributo, ausente
            )
            anteriores[nome] = sys.modules.pop(nome, None)
            pai.__dict__.pop(atributo, None)

        app = SimpleNamespace(
            banco=banco,
            executar=executar,
        )

        for apelido, nome in MODULOS.items():
            setattr(app, apelido, importlib.import_module(nome))

        def cadastrar(nome="ana", senha="123"):
            return executar(
                app.cadastro.CadastroUsuario,
                [nome, senha],
            )

        def usuarios():
            return banco.execute(
                "SELECT user_name FROM user ORDER BY user_name"
            ).fetchall()

        app.cadastrar = cadastrar
        app.usuarios = usuarios

        yield app

    finally:
        for connection in reversed(conexoes):
            connection.close()

        for nome, anterior in anteriores.items():
            sys.modules.pop(nome, None)
            if anterior is not None:
                sys.modules[nome] = anterior

            pacote, atributo = nome.rsplit(".", 1)
            pai = sys.modules[pacote]
            valor = atributos_anteriores[nome]

            if valor is ausente:
                pai.__dict__.pop(atributo, None)
            else:
                setattr(pai, atributo, valor)


def test_cadastrar_usuario(crud):
    crud.cadastrar()
    assert crud.usuarios() == [("ana",)]


def test_cadastro_rejeita_nome_vazio_e_senha_curta(crud):
    crud.executar(
        crud.cadastro.CadastroUsuario,
        ["", "ana", "12", "123"],
    )
    assert crud.usuarios() == [("ana",)]


def test_listar_banco_vazio(crud):
    _, saida = crud.executar(crud.listagem.ListarUsuarios, ["sair"])
    assert "Nenhum usuário" in saida


def test_listar_usuario_cadastrado(crud):
    crud.cadastrar()
    _, saida = crud.executar(crud.listagem.ListarUsuarios, ["sair"])
    assert "ana" in saida


@pytest.mark.parametrize("resposta", ["SAIR", " sair ", " SaIr "])
def test_listagem_aceita_saida_com_maiusculas_e_espacos(crud, resposta):
    crud.cadastrar()
    _, saida = crud.executar(crud.listagem.ListarUsuarios, [resposta])
    assert "ana" in saida
    assert "opção valída" not in saida


def test_listagem_rejeita_entrada_invalida_e_permite_sair(crud):
    crud.cadastrar()
    _, saida = crud.executar(
        crud.listagem.ListarUsuarios,
        ["continuar", "sair"],
    )
    assert "ana" in saida
    assert "digite-a para deixar de ver a lista de usuários" in saida
    assert crud.usuarios() == [("ana",)]


def test_cadastrar_duas_vezes(crud):
    crud.cadastrar("ana", "123")
    crud.cadastrar("bia", "456")
    assert crud.usuarios() == [("ana",), ("bia",)]


def test_listar_duas_vezes(crud):
    crud.cadastrar()

    for _ in range(2):
        _, saida = crud.executar(crud.listagem.ListarUsuarios, ["sair"])
        assert "ana" in saida


def test_autenticar_duas_vezes(crud):
    crud.cadastrar()
    esperado = crud.banco.execute(
        "SELECT id FROM user WHERE user_name = ?",
        ("ana",),
    ).fetchone()

    for _ in range(2):
        resultado, _ = crud.executar(
            crud.auth.ValidarUsuario,
            ["ana", "123"],
        )
        assert resultado == esperado


def test_credenciais_incorretas_permitem_nova_tentativa(crud):
    crud.cadastrar()
    esperado = crud.banco.execute(
        "SELECT id FROM user WHERE user_name = ?",
        ("ana",),
    ).fetchone()

    resultado, saida = crud.executar(
        crud.auth.ValidarUsuario,
        ["ana", "errada", "ana", "123"],
    )

    assert resultado == esperado
    assert "inválidos" in saida


def test_alterar_nome(crud):
    crud.cadastrar()
    crud.executar(
        crud.alteracao.AlterarUsuario,
        ["ana", "123", "1", "bia", "123", "0"],
    )
    assert crud.usuarios() == [("bia",)]


def test_alterar_duas_vezes(crud):
    crud.cadastrar()

    crud.executar(
        crud.alteracao.AlterarUsuario,
        ["ana", "123", "1", "bia", "123", "0"],
    )
    crud.executar(
        crud.alteracao.AlterarUsuario,
        ["bia", "123", "1", "carla", "123", "0"],
    )

    assert crud.usuarios() == [("carla",)]


def test_trocar_senha_invalida_a_anterior(crud):
    crud.cadastrar()
    crud.executar(
        crud.alteracao.AlterarUsuario,
        ["ana", "123", "2", "456", "s", "0"],
    )

    esperado = crud.banco.execute(
        "SELECT id FROM user WHERE user_name = ?",
        ("ana",),
    ).fetchone()

    resultado, saida = crud.executar(
        crud.auth.ValidarUsuario,
        ["ana", "123", "ana", "456"],
    )

    assert resultado == esperado
    assert "inválidos" in saida


def test_cancelar_troca_de_senha_preserva_valor(crud):
    crud.cadastrar()
    anterior = crud.banco.execute(
        "SELECT user_password FROM user"
    ).fetchone()

    crud.executar(
        crud.alteracao.AlterarUsuario,
        ["ana", "123", "2", "456", "n", "0"],
    )

    atual = crud.banco.execute(
        "SELECT user_password FROM user"
    ).fetchone()

    assert atual == anterior


def test_remover_usuario(crud):
    crud.cadastrar()
    crud.executar(
        crud.remocao.RemoverUsuario,
        ["n", "s", "ana", "123"],
    )
    assert crud.usuarios() == []


def test_cancelar_exclusao_preserva_usuario(crud):
    crud.cadastrar()
    crud.executar(
        crud.remocao.RemoverUsuario,
        ["n", "n"],
    )
    assert crud.usuarios() == [("ana",)]


def test_alterar_e_depois_remover_na_mesma_sessao(crud):
    crud.cadastrar()
    crud.executar(
        crud.alteracao.AlterarUsuario,
        ["ana", "123", "1", "bia", "123", "0"],
    )
    crud.executar(
        crud.remocao.RemoverUsuario,
        ["n", "s", "bia", "123"],
    )
    assert crud.usuarios() == []


def test_remover_duas_vezes(crud, monkeypatch):
    # Isola a repetição da remoção das falhas de cadastro/autenticação.
    crud.banco.executemany(
        "INSERT INTO user (user_name, user_password) VALUES (?, ?)",
        [("ana", "123"), ("bia", "456")],
    )
    crud.banco.commit()

    ids = iter(
        crud.banco.execute(
            "SELECT id FROM user ORDER BY id"
        ).fetchall()
    )
    monkeypatch.setattr(
        crud.remocao,
        "ValidarUsuario",
        lambda: next(ids),
    )

    for _ in range(2):
        crud.executar(crud.remocao.RemoverUsuario, ["n", "s"])

    assert crud.usuarios() == []


def test_cadastro_duplicado_permite_novo_nome(crud):
    crud.cadastrar()
    anterior = crud.banco.execute("SELECT * FROM user").fetchone()

    _, saida = crud.executar(
        crud.cadastro.CadastroUsuario,
        ["ana", "456", "bia", "456"],
    )

    assert "Esse nome ja existe" in saida
    assert crud.usuarios() == [("ana",), ("bia",)]
    assert crud.banco.execute(
        "SELECT * FROM user WHERE user_name = ?", ("ana",)
    ).fetchone() == anterior


@pytest.mark.parametrize("interrupcao", [EOFError, KeyboardInterrupt])
def test_cancelar_cadastro_duplicado_preserva_conta(crud, interrupcao):
    crud.cadastrar()
    anteriores = crud.banco.execute("SELECT * FROM user ORDER BY id").fetchall()

    _, saida = crud.executar(
        crud.cadastro.CadastroUsuario,
        ["ana", "456", interrupcao()],
    )

    assert "Esse nome ja existe" in saida
    assert "Cadastro cancelado pelo usuário" in saida
    assert crud.banco.execute(
        "SELECT * FROM user ORDER BY id"
    ).fetchall() == anteriores


def test_renomear_para_nome_existente_permite_nova_tentativa(crud):
    crud.cadastrar("ana", "123")
    crud.cadastrar("bia", "456")
    anteriores = crud.banco.execute("SELECT * FROM user ORDER BY id").fetchall()

    _, saida = crud.executar(
        crud.alteracao.AlterarUsuario,
        ["ana", "123", "1", "bia", "123", "carla", "123", "0"],
    )

    assert "Esse nome ja existe" in saida
    assert crud.banco.execute(
        "SELECT * FROM user ORDER BY id"
    ).fetchall() == [
        (anteriores[0][0], "carla", anteriores[0][2]),
        anteriores[1],
    ]


@pytest.mark.parametrize("interrupcao", [EOFError, KeyboardInterrupt])
def test_cancelar_renomeacao_duplicada_preserva_contas(crud, interrupcao):
    crud.cadastrar("ana", "123")
    crud.cadastrar("bia", "456")
    anteriores = crud.banco.execute("SELECT * FROM user ORDER BY id").fetchall()

    _, saida = crud.executar(
        crud.alteracao.AlterarUsuario,
        ["ana", "123", "1", "bia", "123", interrupcao(), "0"],
    )

    assert "Esse nome ja existe" in saida
    assert "Alteração interrompida" in saida
    assert crud.banco.execute(
        "SELECT * FROM user ORDER BY id"
    ).fetchall() == anteriores


def test_senha_nao_e_armazenada_em_texto_puro(crud):
    crud.cadastrar("ana", "segredo123")

    armazenada = crud.banco.execute(
        "SELECT user_password FROM user WHERE user_name = ?",
        ("ana",),
    ).fetchone()[0]

    assert armazenada
    assert armazenada != "segredo123"


def test_menu_permite_repetir_operacoes_e_sair(crud):
    _, saida = crud.executar(
        lambda: runpy.run_path(
            str(RAIZ / "main.py"),
            run_name="__main__",
        ),
        ["4", "sair", "4", "sair", "0"],
    )

    assert "Encerrando programa" in saida
    assert saida.count("Nenhum usuário foi cadastrado ainda!") == 2


if __name__ == "__main__":
    raise SystemExit(pytest.main([str(Path(__file__).resolve()), "-v", *sys.argv[1:]]))
