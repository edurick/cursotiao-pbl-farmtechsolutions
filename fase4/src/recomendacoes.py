#!/usr/bin/env python3
"""
FarmTech Solutions - Fase 4
Regras de recomendacao de manejo agricola.

Este modulo transforma as PREVISOES dos modelos + as condicoes atuais
do solo em ACOES praticas e legiveis para o gestor agricola.

E aqui que o projeto cumpre o objetivo de "sugerir acoes futuras de
irrigacao e manejo", combinando IA (as previsoes) com regras agronomicas
(a mesma faixa de pH e a logica de umidade usadas no ESP32 da Fase 2).
"""

from __future__ import annotations

# Faixas ideais para o milho (iguais as do sketch do ESP32 na Fase 2)
PH_MINIMO = 5.5
PH_MAXIMO = 7.0
UMIDADE_ALVO = 65.0
UMIDADE_LIGAR_BOMBA = 55.0


def recomendar_irrigacao(umidade: float, chuva_prevista: int,
                         volume_previsto: float) -> dict:
    """Decide se deve irrigar e quanto, combinando regra + previsao do modelo."""
    if chuva_prevista == 1:
        return {
            "acao": "NAO irrigar",
            "detalhe": "Ha previsao de chuva. A irrigacao automatica fica suspensa "
                       "para economizar agua e evitar encharcamento.",
            "volume_litros": 0.0,
            "nivel": "ok",
        }

    if umidade >= UMIDADE_ALVO:
        return {
            "acao": "NAO irrigar",
            "detalhe": f"A umidade do solo ({umidade:.0f}%) ja esta no alvo "
                       f"(>= {UMIDADE_ALVO:.0f}%). Nao e necessario irrigar agora.",
            "volume_litros": 0.0,
            "nivel": "ok",
        }

    if umidade <= UMIDADE_LIGAR_BOMBA:
        return {
            "acao": "IRRIGAR agora",
            "detalhe": f"Solo seco ({umidade:.0f}%). O modelo sugere aplicar cerca de "
                       f"{volume_previsto:.0f} litros para retornar ao alvo de umidade.",
            "volume_litros": round(volume_previsto, 0),
            "nivel": "alerta",
        }

    return {
        "acao": "Monitorar",
        "detalhe": f"Umidade intermediaria ({umidade:.0f}%). Acompanhar; "
                   f"irrigacao sugerida de ~{volume_previsto:.0f} litros se continuar caindo.",
        "volume_litros": round(volume_previsto, 0),
        "nivel": "atencao",
    }


def recomendar_ph(ph: float) -> dict:
    """Avalia o pH e sugere correcao quando fora da faixa do milho."""
    if ph < PH_MINIMO:
        return {
            "acao": "Corrigir pH (calagem)",
            "detalhe": f"pH {ph:.1f} esta acido demais para o milho. Aplicar calcario "
                       f"para elevar o pH em direcao a faixa ideal ({PH_MINIMO}-{PH_MAXIMO}).",
            "nivel": "alerta",
        }
    if ph > PH_MAXIMO:
        return {
            "acao": "Corrigir pH",
            "detalhe": f"pH {ph:.1f} esta alcalino demais. Considerar enxofre ou materia "
                       f"organica para baixar o pH ate a faixa ideal ({PH_MINIMO}-{PH_MAXIMO}).",
            "nivel": "alerta",
        }
    return {
        "acao": "pH adequado",
        "detalhe": f"pH {ph:.1f} esta dentro da faixa ideal do milho ({PH_MINIMO}-{PH_MAXIMO}).",
        "nivel": "ok",
    }


def recomendar_fertilizacao(n: int, p: int, k: int) -> dict:
    """Sugere fertilizacao com base nos nutrientes que estiverem baixos."""
    faltando = []
    if n == 0:
        faltando.append("Nitrogenio (N)")
    if p == 0:
        faltando.append("Fosforo (P)")
    if k == 0:
        faltando.append("Potassio (K)")

    if not faltando:
        return {
            "acao": "Nutrientes OK",
            "detalhe": "N, P e K estao adequados. Nenhuma adubacao corretiva necessaria agora.",
            "nivel": "ok",
        }

    return {
        "acao": "Aplicar fertilizante",
        "detalhe": "Nutriente(s) abaixo do ideal: " + ", ".join(faltando) +
                   ". Recomenda-se adubacao corretiva para nao limitar o rendimento.",
        "nivel": "alerta",
    }


def gerar_recomendacoes(umidade: float, temperatura: float, ph: float,
                        n: int, p: int, k: int, chuva_prevista: int,
                        rendimento_previsto: float,
                        volume_previsto: float) -> dict:
    """Funcao principal: junta todas as recomendacoes em um unico relatorio."""
    return {
        "rendimento_previsto": round(rendimento_previsto, 1),
        "volume_previsto": round(volume_previsto, 0),
        "irrigacao": recomendar_irrigacao(umidade, chuva_prevista, volume_previsto),
        "ph": recomendar_ph(ph),
        "fertilizacao": recomendar_fertilizacao(n, p, k),
    }


# Teste rapido ao rodar o arquivo diretamente
if __name__ == "__main__":
    exemplo = gerar_recomendacoes(
        umidade=48, temperatura=30, ph=5.1, n=1, p=0, k=1,
        chuva_prevista=0, rendimento_previsto=110.5, volume_previsto=720,
    )
    import json
    print(json.dumps(exemplo, indent=2, ensure_ascii=False))
