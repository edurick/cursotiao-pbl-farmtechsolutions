#!/usr/bin/env python3
"""
FarmTech Solutions - Fase 4
Gerador de dataset sintetico realista para o milho.

Por que este script existe?
---------------------------
O CSV da Fase 2 (cenarios_irrigacao.csv) tem apenas 8 linhas e nao possui
nenhuma coluna de "resultado" (alvo) para um modelo de regressao aprender.
8 linhas sao insuficientes para treinar Machine Learning de forma confiavel.

O enunciado da Fase 4 permite explicitamente o uso de "dados simulados de
sensores virtuais". Entao aqui geramos um dataset MAIOR e COERENTE com a
Fase 2: mesmas variaveis (umidade, pH, N, P, K, chuva), mesma cultura (milho)
e a mesma logica agronomica. Apenas adicionamos os dois alvos que o modelo
vai prever:
  - rendimento_estimado  -> produtividade do milho em sacas por hectare
  - volume_irrigacao     -> litros de agua sugeridos para a irrigacao

As relacoes entre as variaveis seguem agronomia basica + a regra do ESP32.
Adicionamos um pouco de "ruido" aleatorio para simular a imprevisibilidade
do mundo real (sem ruido, o modelo aprenderia formulas perfeitas e as
metricas nao teriam significado pratico).
"""

from __future__ import annotations
import os
import numpy as np
import pandas as pd

# Semente aleatoria fixa: garante que os dados gerados sejam sempre os mesmos.
# Isso torna o trabalho reproduzivel (qualquer pessoa que rodar gera o mesmo CSV).
SEMENTE = 42
N_LINHAS = 1000

# Caminho de saida (a pasta dados/ fica um nivel acima de src/)
PASTA_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMINHO_SAIDA = os.path.join(PASTA_BASE, "dados", "dataset_milho.csv")


def gerar_features(rng: np.random.Generator, n: int) -> pd.DataFrame:
    """Gera as variaveis de entrada (o que os sensores mediriam)."""

    # Umidade do solo (%): centrada em ~58, parecida com a faixa da Fase 2 (45-72).
    umidade_solo = np.clip(rng.normal(58, 12, n), 25, 95)

    # Temperatura (C): o DHT22 tambem le temperatura. Milho gosta de ~26 C.
    temperatura = np.clip(rng.normal(26, 4, n), 14, 40)

    # pH do solo: faixa ideal do milho e 5.5-7.0 (igual ao sketch do ESP32).
    ph = np.clip(rng.normal(6.2, 0.6, n), 4.3, 8.2)

    # Nutrientes N, P, K: 1 = OK, 0 = baixo. ~80% de chance de estarem OK.
    n_nutriente = rng.binomial(1, 0.80, n)
    p_nutriente = rng.binomial(1, 0.78, n)
    k_nutriente = rng.binomial(1, 0.80, n)

    # Previsao de chuva: 0 = sem chuva, 1 = chuva prevista (~20% dos casos).
    chuva_prevista = rng.binomial(1, 0.20, n)

    return pd.DataFrame({
        "umidade_solo": umidade_solo.round(1),
        "temperatura": temperatura.round(1),
        "ph": ph.round(2),
        "n": n_nutriente,
        "p": p_nutriente,
        "k": k_nutriente,
        "chuva_prevista": chuva_prevista,
    })


def calcular_rendimento(df: pd.DataFrame, rng: np.random.Generator) -> np.ndarray:
    """
    Calcula o rendimento (sacas/ha) do milho a partir das condicoes do solo.

    Logica agronomica (simplificada, mas coerente):
      - Existe um rendimento base (terreno saudavel).
      - pH longe do ideal (6.2) reduz o rendimento.
      - Umidade ideal fica perto de 65%. Solo seco penaliza bastante;
        solo encharcado (>80%) penaliza um pouco (falta de oxigenio nas raizes).
      - Temperatura ideal perto de 26 C.
      - Cada nutriente presente (N, P, K) soma rendimento.
    """
    base = 120.0

    # Penalidade pelo desvio de pH em relacao ao ideal
    pen_ph = -9.0 * np.abs(df["ph"] - 6.2)

    # Penalidade por umidade: assimetrica (seca e pior que excesso)
    desvio_umid = df["umidade_solo"] - 65.0
    pen_umid = np.where(
        desvio_umid < 0,
        desvio_umid * 0.9,          # solo seco: penalidade forte
        -np.maximum(0, df["umidade_solo"] - 80) * 0.6,  # encharcado: penalidade leve
    )

    # Penalidade por temperatura fora do ideal
    pen_temp = -1.2 * np.abs(df["temperatura"] - 26.0)

    # Bonus dos nutrientes
    bonus_npk = 13.0 * df["n"] + 9.0 * df["p"] + 11.0 * df["k"]

    # Ruido aleatorio (variabilidade natural do campo)
    ruido = rng.normal(0, 6, len(df))

    rendimento = base + pen_ph + pen_umid + pen_temp + bonus_npk + ruido
    return np.clip(rendimento, 30, 200).round(1)


def calcular_volume_irrigacao(df: pd.DataFrame, rng: np.random.Generator) -> np.ndarray:
    """
    Calcula o volume de irrigacao sugerido (litros).

    Logica (coerente com a regra do ESP32):
      - O alvo de umidade e ~65%. Quanto mais seco o solo, mais agua.
      - Calor aumenta a evapotranspiracao -> precisa de mais agua.
      - Se ha previsao de chuva, reduzimos bastante a irrigacao.
      - Se o solo ja esta umido o suficiente, o volume tende a zero.
    """
    deficit = np.maximum(0, 65.0 - df["umidade_solo"])   # quanto falta de umidade
    extra_calor = np.maximum(0, df["temperatura"] - 25.0) * 7.0

    volume = deficit * 42.0 + extra_calor

    # Se chuva prevista, reduz para 30% (a chuva ajuda a irrigar)
    volume = np.where(df["chuva_prevista"] == 1, volume * 0.30, volume)

    # Ruido pequeno
    volume = volume + rng.normal(0, 25, len(df))
    return np.clip(volume, 0, None).round(0)


def main() -> None:
    rng = np.random.default_rng(SEMENTE)

    df = gerar_features(rng, N_LINHAS)
    df["rendimento_estimado"] = calcular_rendimento(df, rng)
    df["volume_irrigacao"] = calcular_volume_irrigacao(df, rng)

    os.makedirs(os.path.dirname(CAMINHO_SAIDA), exist_ok=True)
    df.to_csv(CAMINHO_SAIDA, index=False)

    print("=== Gerador de dados FarmTech - Fase 4 ===")
    print(f"Linhas geradas: {len(df)}")
    print(f"Arquivo salvo em: {CAMINHO_SAIDA}")
    print("\nPrimeiras linhas:")
    print(df.head())
    print("\nResumo estatistico:")
    print(df.describe().round(2))


if __name__ == "__main__":
    main()
