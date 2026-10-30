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

from database import conexao


RAIZ = Path(__file__).resolve().parents[1]

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

        with monkeypatch.context() as contexto:
            contexto.setattr(
                "builtins.input",
                lambda prompt="": next(entradas),
            )
            with redirect_stdout(saida):
                try:
                    resultado = funcao()
                except StopIteration:
                    pytest.fail(
                        "A função pediu entradas além das previstas. "
                        "Verifique o cancelamento ou o retorno ao menu."
                    )

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
    _, saida = crud.executar(crud.listagem.ListarUsuarios)
    assert "Nenhum usuário" in saida


def test_listar_usuario_cadastrado(crud):
    crud.cadastrar()
    _, saida = crud.executar(crud.listagem.ListarUsuarios)
    assert "ana" in saida


def test_cadastrar_duas_vezes(crud):
    crud.cadastrar("ana", "123")
    crud.cadastrar("bia", "456")
    assert crud.usuarios() == [("ana",), ("bia",)]


def test_listar_duas_vezes(crud):
    crud.cadastrar()

    for _ in range(2):
        _, saida = crud.executar(crud.listagem.ListarUsuarios)
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


def test_cadastro_duplicado_nao_gera_excecao(crud):
    crud.banco.execute(
        "INSERT INTO user (user_name, user_password) VALUES (?, ?)",
        ("ana", "123"),
    )
    crud.banco.commit()

    crud.executar(
        crud.cadastro.CadastroUsuario,
        ["ana", "456"],
    )

    assert crud.usuarios() == [("ana",)]


def test_renomear_para_nome_existente_preserva_contas(crud):
    crud.cadastrar("ana", "123")
    crud.banco.execute(
        "INSERT INTO user (user_name, user_password) VALUES (?, ?)",
        ("bia", "456"),
    )
    crud.banco.commit()

    crud.executar(
        crud.alteracao.AlterarUsuario,
        ["ana", "123", "1", "bia", "123", "0"],
    )

    assert crud.usuarios() == [("ana",), ("bia",)]


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
        ["4", "4", "0"],
    )

    assert "Encerrando programa" in saida