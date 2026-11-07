import re

def opcoesMenu(resposta_usuario, opcoes):
    for chave, (valor1, valor2) in opcoes.items():
        resultado1 = re.search(valor1, resposta_usuario, flags=re.IGNORECASE) # RECONHECE O PADRÃO QUE FOI ESTABELECIDO NO DICT
        resulatdo2 = re.fullmatch(valor2, resposta_usuario, flags=re.IGNORECASE) # RETORNA O PADRÃO SE FOR IDÊNTICO AO valor2
        if resultado1 or resulatdo2:
            return chave
    return None