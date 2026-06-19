#!/usr/bin/env python3
"""
FarmTech Solutions - Fase 4
Pipeline de Machine Learning (regressao) com Scikit-Learn.

O que este script faz, passo a passo:
  1. Carrega o dataset gerado (dataset_milho.csv).
  2. Analisa correlacoes entre as variaveis (e salva um heatmap).
  3. Separa os dados em treino (80%) e teste (20%).
  4. Treina DOIS algoritmos para cada alvo:
        - Regressao Linear (modelo simples, base de comparacao)
        - Random Forest  (modelo nao linear, costuma prever melhor)
  5. Avalia cada modelo com as metricas MAE, MSE, RMSE e R2.
  6. Escolhe o melhor modelo de cada alvo (maior R2) e salva em disco.
  7. Salva as metricas (metricas.json) e graficos para o dashboard.

Alvos previstos:
  - rendimento_estimado (sacas/ha)
  - volume_irrigacao    (litros)
"""

from __future__ import annotations
import os
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # backend sem janela (para salvar imagens em servidor)
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ----- Caminhos -----
PASTA_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMINHO_DADOS = os.path.join(PASTA_BASE, "dados", "dataset_milho.csv")
PASTA_MODELOS = os.path.join(PASTA_BASE, "modelos")
PASTA_GRAFICOS = os.path.join(PASTA_BASE, "graficos")

# Variaveis de entrada (features) usadas para prever
FEATURES = ["umidade_solo", "temperatura", "ph", "n", "p", "k", "chuva_prevista"]
# Variaveis que queremos prever (alvos)
ALVOS = ["rendimento_estimado", "volume_irrigacao"]

SEMENTE = 42


def calcular_metricas(y_real, y_previsto) -> dict:
    """Calcula as quatro metricas pedidas no enunciado."""
    mae = mean_absolute_error(y_real, y_previsto)
    mse = mean_squared_error(y_real, y_previsto)
    rmse = np.sqrt(mse)              # RMSE = raiz quadrada do MSE
    r2 = r2_score(y_real, y_previsto)
    return {
        "MAE": round(float(mae), 3),
        "MSE": round(float(mse), 3),
        "RMSE": round(float(rmse), 3),
        "R2": round(float(r2), 4),
    }


def salvar_heatmap_correlacao(df: pd.DataFrame) -> None:
    """Gera e salva o mapa de calor de correlacao entre todas as variaveis."""
    plt.figure(figsize=(9, 7))
    corr = df.corr(numeric_only=True)
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdYlGn", center=0,
                square=True, linewidths=0.5, cbar_kws={"shrink": 0.8})
    plt.title("Correlacao entre variaveis agricolas (milho)")
    plt.tight_layout()
    caminho = os.path.join(PASTA_GRAFICOS, "correlacao.png")
    plt.savefig(caminho, dpi=120)
    plt.close()
    print(f"  Heatmap salvo em: {caminho}")


def grafico_real_vs_previsto(y_real, y_previsto, nome_alvo: str) -> None:
    """Grafico de dispersao: valores reais x valores previstos pelo modelo."""
    plt.figure(figsize=(6, 6))
    plt.scatter(y_real, y_previsto, alpha=0.5, edgecolor="k", linewidth=0.3)
    minimo = min(y_real.min(), y_previsto.min())
    maximo = max(y_real.max(), y_previsto.max())
    plt.plot([minimo, maximo], [minimo, maximo], "r--", label="Previsao perfeita")
    plt.xlabel(f"{nome_alvo} (real)")
    plt.ylabel(f"{nome_alvo} (previsto)")
    plt.title(f"Real vs Previsto - {nome_alvo}")
    plt.legend()
    plt.tight_layout()
    caminho = os.path.join(PASTA_GRAFICOS, f"real_vs_previsto_{nome_alvo}.png")
    plt.savefig(caminho, dpi=120)
    plt.close()
    print(f"  Grafico salvo em: {caminho}")


def grafico_importancia(modelo, nome_alvo: str) -> None:
    """Mostra quais variaveis o Random Forest considerou mais importantes."""
    if not hasattr(modelo, "feature_importances_"):
        return
    importancias = pd.Series(modelo.feature_importances_, index=FEATURES)
    importancias = importancias.sort_values()
    plt.figure(figsize=(7, 5))
    importancias.plot(kind="barh", color="seagreen")
    plt.xlabel("Importancia")
    plt.title(f"Importancia das variaveis - {nome_alvo}")
    plt.tight_layout()
    caminho = os.path.join(PASTA_GRAFICOS, f"importancia_{nome_alvo}.png")
    plt.savefig(caminho, dpi=120)
    plt.close()
    print(f"  Grafico salvo em: {caminho}")


def treinar_para_alvo(df: pd.DataFrame, alvo: str) -> dict:
    """
    Treina e compara dois modelos para um alvo especifico.
    Retorna um dicionario com metricas e o melhor modelo escolhido.
    """
    print(f"\n=== Treinando modelos para: {alvo} ===")

    X = df[FEATURES]
    y = df[alvo]

    # Divisao treino/teste (80/20). O modelo aprende no treino e e avaliado no teste.
    X_treino, X_teste, y_treino, y_teste = train_test_split(
        X, y, test_size=0.20, random_state=SEMENTE
    )

    candidatos = {
        "Regressão Linear": LinearRegression(),
        "Random Forest": RandomForestRegressor(
            n_estimators=200, random_state=SEMENTE, n_jobs=-1
        ),
    }

    resultados = {}
    melhor_nome = None
    melhor_r2 = -np.inf
    melhor_modelo = None

    for nome, modelo in candidatos.items():
        modelo.fit(X_treino, y_treino)               # treina
        y_prev = modelo.predict(X_teste)             # preve no conjunto de teste
        metricas = calcular_metricas(y_teste, y_prev)
        resultados[nome] = metricas
        print(f"  {nome:18s} -> R2={metricas['R2']:.4f} | "
              f"MAE={metricas['MAE']:.2f} | RMSE={metricas['RMSE']:.2f}")

        if metricas["R2"] > melhor_r2:
            melhor_r2 = metricas["R2"]
            melhor_nome = nome
            melhor_modelo = modelo

    print(f"  >> Melhor modelo: {melhor_nome} (R2={melhor_r2:.4f})")

    # Gera graficos usando o melhor modelo
    y_prev_melhor = melhor_modelo.predict(X_teste)
    grafico_real_vs_previsto(y_teste, y_prev_melhor, alvo)
    grafico_importancia(melhor_modelo, alvo)

    # Salva o melhor modelo em disco (formato .pkl via joblib)
    caminho_modelo = os.path.join(PASTA_MODELOS, f"modelo_{alvo}.pkl")
    joblib.dump(melhor_modelo, caminho_modelo)
    print(f"  Modelo salvo em: {caminho_modelo}")

    return {
        "melhor_modelo": melhor_nome,
        "metricas_por_modelo": resultados,
        "metricas_melhor": resultados[melhor_nome],
    }


def main() -> None:
    os.makedirs(PASTA_MODELOS, exist_ok=True)
    os.makedirs(PASTA_GRAFICOS, exist_ok=True)

    if not os.path.exists(CAMINHO_DADOS):
        raise FileNotFoundError(
            "dataset_milho.csv nao encontrado. Rode antes: python src/gerar_dados.py"
        )

    df = pd.read_csv(CAMINHO_DADOS)
    print(f"Dataset carregado: {len(df)} linhas, {len(df.columns)} colunas")

    # Analise de correlacao
    print("\nGerando heatmap de correlacao...")
    salvar_heatmap_correlacao(df)

    # Treina os modelos de cada alvo
    relatorio = {"features": FEATURES}
    for alvo in ALVOS:
        relatorio[alvo] = treinar_para_alvo(df, alvo)

    # Salva as metricas e a lista de features para o dashboard usar
    caminho_metricas = os.path.join(PASTA_MODELOS, "metricas.json")
    with open(caminho_metricas, "w", encoding="utf-8") as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)
    print(f"\nMetricas salvas em: {caminho_metricas}")
    print("\nPipeline concluido com sucesso!")


if __name__ == "__main__":
    main()
