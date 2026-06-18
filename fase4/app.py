#!/usr/bin/env python3
"""
FarmTech Solutions - Fase 4
Dashboard interativo (Streamlit) para o gestor agricola.

Este painel conecta os modelos de Machine Learning treinados a uma
interface visual. O gestor pode:
  - Ver as metricas de desempenho dos modelos (Visao Geral).
  - Explorar correlacoes entre as variaveis (Correlacoes).
  - Simular cenarios e receber previsoes + recomendacoes (Previsao).
  - Observar tendencias de produtividade e irrigacao (Tendencias).

Como rodar:
  streamlit run app.py
"""

from __future__ import annotations
import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# Permite importar o modulo de recomendacoes que esta em src/
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from recomendacoes import gerar_recomendacoes  # noqa: E402

# ---------------------------------------------------------------------------
# Configuracao da pagina
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="FarmTech Solutions | Assistente Agricola",
    page_icon="🌽",
    layout="wide",
)

PASTA_BASE = os.path.dirname(os.path.abspath(__file__))
CAMINHO_DADOS = os.path.join(PASTA_BASE, "dados", "dataset_milho.csv")
PASTA_MODELOS = os.path.join(PASTA_BASE, "modelos")

FEATURES = ["umidade_solo", "temperatura", "ph", "n", "p", "k", "chuva_prevista"]

# Paleta de cores do tema (agro / milho)
VERDE_ESCURO = "#1b5e20"
VERDE = "#2e7d32"
DOURADO = "#f9a825"

# CSS leve para dar identidade visual ao painel
st.markdown(
    f"""
    <style>
    .bloco-titulo {{
        background: linear-gradient(90deg, {VERDE_ESCURO}, {VERDE});
        padding: 18px 24px; border-radius: 12px; color: white; margin-bottom: 8px;
    }}
    .bloco-titulo h1 {{ margin: 0; font-size: 30px; }}
    .bloco-titulo p  {{ margin: 4px 0 0 0; opacity: 0.9; }}
    .card-rec {{
        padding: 14px 16px; border-radius: 10px; margin-bottom: 10px;
        border-left: 6px solid {VERDE};
    }}
    .rec-ok     {{ background: #e8f5e9; border-left-color: #2e7d32; }}
    .rec-atencao{{ background: #fff8e1; border-left-color: #f9a825; }}
    .rec-alerta {{ background: #ffebee; border-left-color: #c62828; }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Carregamento de dados e modelos (com cache para nao recarregar a cada clique)
# ---------------------------------------------------------------------------
@st.cache_data
def carregar_dados() -> pd.DataFrame:
    return pd.read_csv(CAMINHO_DADOS)


@st.cache_resource
def carregar_modelos():
    modelo_rend = joblib.load(os.path.join(PASTA_MODELOS, "modelo_rendimento_estimado.pkl"))
    modelo_vol = joblib.load(os.path.join(PASTA_MODELOS, "modelo_volume_irrigacao.pkl"))
    with open(os.path.join(PASTA_MODELOS, "metricas.json"), encoding="utf-8") as f:
        metricas = json.load(f)
    return modelo_rend, modelo_vol, metricas


# Verifica se os arquivos existem antes de tentar carregar
faltando = [
    p for p in [
        CAMINHO_DADOS,
        os.path.join(PASTA_MODELOS, "modelo_rendimento_estimado.pkl"),
        os.path.join(PASTA_MODELOS, "modelo_volume_irrigacao.pkl"),
        os.path.join(PASTA_MODELOS, "metricas.json"),
    ] if not os.path.exists(p)
]
if faltando:
    st.error(
        "Arquivos necessarios nao encontrados. Rode antes, no terminal:\n\n"
        "python src/gerar_dados.py\n"
        "python src/treinar_modelo.py"
    )
    st.stop()

df = carregar_dados()
modelo_rend, modelo_vol, metricas = carregar_modelos()

# ---------------------------------------------------------------------------
# Cabecalho
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="bloco-titulo">
        <h1>🌽 FarmTech Solutions — Assistente Agricola Inteligente</h1>
        <p>Previsao de rendimento e irrigacao do milho com Machine Learning</p>
    </div>
    """,
    unsafe_allow_html=True,
)

aba_visao, aba_corr, aba_prev, aba_tend = st.tabs(
    ["📊 Visao Geral", "🔗 Correlacoes", "🔮 Previsao Interativa", "📈 Tendencias"]
)

# ===========================================================================
# ABA 1 - VISAO GERAL (metricas dos modelos)
# ===========================================================================
with aba_visao:
    st.subheader("Desempenho dos modelos de regressao")
    st.caption(
        "Metricas calculadas no conjunto de teste (20% dos dados nunca vistos "
        "pelo modelo durante o treino). R2 mais perto de 1 e melhor; "
        "MAE e RMSE mais baixos sao melhores."
    )

    col1, col2 = st.columns(2)

    for coluna, alvo, titulo, unidade in [
        (col1, "rendimento_estimado", "Rendimento do milho", "sacas/ha"),
        (col2, "volume_irrigacao", "Volume de irrigacao", "litros"),
    ]:
        with coluna:
            info = metricas[alvo]
            m = info["metricas_melhor"]
            st.markdown(f"#### {titulo}")
            st.markdown(f"Melhor modelo: **{info['melhor_modelo']}**")
            sub1, sub2 = st.columns(2)
            sub1.metric("R² (qualidade)", f"{m['R2']:.3f}")
            sub2.metric(f"MAE ({unidade})", f"{m['MAE']:.2f}")
            sub3, sub4 = st.columns(2)
            sub3.metric(f"RMSE ({unidade})", f"{m['RMSE']:.2f}")
            sub4.metric("MSE", f"{m['MSE']:.1f}")

            # Tabela comparando os dois algoritmos testados
            comp = pd.DataFrame(info["metricas_por_modelo"]).T
            comp.index.name = "Modelo"
            st.dataframe(comp, use_container_width=True)

    st.info(
        "Interpretacao: o **Random Forest** captura relacoes nao lineares "
        "(ex.: o efeito do deficit de umidade no volume de irrigacao), por isso "
        "supera a Regressao Linear, especialmente na previsao de irrigacao."
    )

# ===========================================================================
# ABA 2 - CORRELACOES
# ===========================================================================
with aba_corr:
    st.subheader("Correlacao entre as variaveis agricolas")
    st.caption(
        "Valores proximos de +1 (verde) indicam que as variaveis crescem juntas; "
        "proximos de -1 (vermelho) indicam relacao inversa; perto de 0, sem relacao."
    )

    corr = df.corr(numeric_only=True)
    fig_corr = px.imshow(
        corr, text_auto=".2f", color_continuous_scale="RdYlGn", zmin=-1, zmax=1,
        aspect="auto",
    )
    fig_corr.update_layout(height=550, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_corr, use_container_width=True)

    st.markdown("**Relacao entre duas variaveis (escolha os eixos):**")
    c1, c2, c3 = st.columns(3)
    eixo_x = c1.selectbox("Eixo X", df.columns, index=0)
    eixo_y = c2.selectbox("Eixo Y", df.columns, index=list(df.columns).index("rendimento_estimado"))
    cor = c3.selectbox("Colorir por", ["(nenhum)"] + list(df.columns), index=0)

    fig_disp = px.scatter(
        df, x=eixo_x, y=eixo_y,
        color=None if cor == "(nenhum)" else df[cor],
        opacity=0.6, color_continuous_scale="Viridis",
    )
    fig_disp.update_layout(height=450, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_disp, use_container_width=True)

# ===========================================================================
# ABA 3 - PREVISAO INTERATIVA
# ===========================================================================
with aba_prev:
    st.subheader("Simule um cenario e receba a recomendacao")
    st.caption("Ajuste os sensores no painel da esquerda. As previsoes atualizam na hora.")

    entrada, saida = st.columns([1, 1.4])

    with entrada:
        st.markdown("##### Leituras dos sensores")
        umidade = st.slider("Umidade do solo (%)", 20.0, 95.0, 50.0, 1.0)
        temperatura = st.slider("Temperatura (°C)", 14.0, 40.0, 27.0, 0.5)
        ph = st.slider("pH do solo", 4.3, 8.2, 6.2, 0.1)
        st.markdown("##### Nutrientes e clima")
        col_n, col_p, col_k = st.columns(3)
        n = 1 if col_n.checkbox("N ok", value=True) else 0
        p = 1 if col_p.checkbox("P ok", value=True) else 0
        k = 1 if col_k.checkbox("K ok", value=True) else 0
        chuva = 1 if st.checkbox("Previsao de chuva", value=False) else 0

    # Monta a entrada para os modelos (mesma ordem das FEATURES)
    X_novo = pd.DataFrame([{
        "umidade_solo": umidade, "temperatura": temperatura, "ph": ph,
        "n": n, "p": p, "k": k, "chuva_prevista": chuva,
    }])[FEATURES]

    rend_prev = float(modelo_rend.predict(X_novo)[0])
    vol_prev = float(modelo_vol.predict(X_novo)[0])

    rec = gerar_recomendacoes(
        umidade, temperatura, ph, n, p, k, chuva, rend_prev, vol_prev
    )

    with saida:
        st.markdown("##### Previsoes do modelo")
        mp1, mp2 = st.columns(2)
        mp1.metric("Rendimento previsto", f"{rec['rendimento_previsto']:.0f} sacas/ha")
        mp2.metric("Irrigacao sugerida", f"{rec['volume_previsto']:.0f} L")

        st.markdown("##### Recomendacoes de manejo")
        for item in [rec["irrigacao"], rec["ph"], rec["fertilizacao"]]:
            classe = {"ok": "rec-ok", "atencao": "rec-atencao", "alerta": "rec-alerta"}[item["nivel"]]
            st.markdown(
                f'<div class="card-rec {classe}"><b>{item["acao"]}</b><br>{item["detalhe"]}</div>',
                unsafe_allow_html=True,
            )

# ===========================================================================
# ABA 4 - TENDENCIAS
# ===========================================================================
with aba_tend:
    st.subheader("Tendencias de produtividade e irrigacao")
    st.caption("Como o rendimento e a irrigacao variam conforme as condicoes do solo.")

    col_a, col_b = st.columns(2)

    # Rendimento medio por faixa de pH
    df_ph = df.copy()
    df_ph["faixa_ph"] = pd.cut(df_ph["ph"], bins=[4, 5, 5.5, 6, 6.5, 7, 7.5, 8.5])
    rend_ph = df_ph.groupby("faixa_ph", observed=True)["rendimento_estimado"].mean().reset_index()
    rend_ph["faixa_ph"] = rend_ph["faixa_ph"].astype(str)
    fig_ph = px.bar(rend_ph, x="faixa_ph", y="rendimento_estimado",
                    color_discrete_sequence=[VERDE], title="Rendimento medio por faixa de pH")
    fig_ph.update_layout(height=400, xaxis_title="Faixa de pH", yaxis_title="Rendimento (sacas/ha)")
    col_a.plotly_chart(fig_ph, use_container_width=True)

    # Volume de irrigacao vs umidade do solo
    fig_vol = px.scatter(df, x="umidade_solo", y="volume_irrigacao",
                         color="chuva_prevista", opacity=0.6,
                         color_continuous_scale=["#2e7d32", "#1565c0"],
                         title="Irrigacao necessaria vs umidade do solo")
    fig_vol.update_layout(height=400, xaxis_title="Umidade do solo (%)",
                          yaxis_title="Volume de irrigacao (L)")
    col_b.plotly_chart(fig_vol, use_container_width=True)

    # Rendimento medio conforme presenca de nutrientes
    df["nutrientes_ok"] = df["n"] + df["p"] + df["k"]
    rend_npk = df.groupby("nutrientes_ok")["rendimento_estimado"].mean().reset_index()
    fig_npk = px.line(rend_npk, x="nutrientes_ok", y="rendimento_estimado", markers=True,
                      color_discrete_sequence=[DOURADO],
                      title="Rendimento medio conforme nutrientes presentes (0 a 3)")
    fig_npk.update_layout(height=380, xaxis_title="Quantidade de nutrientes OK (N+P+K)",
                          yaxis_title="Rendimento (sacas/ha)")
    st.plotly_chart(fig_npk, use_container_width=True)

st.markdown("---")
st.caption("FarmTech Solutions · Fase 4 · Machine Learning aplicado ao agronegocio")
