# FarmTech Solutions — Fase 4

Assistente Agrícola Inteligente: aplicação de **Machine Learning (regressão)**
sobre os dados agrícolas do milho, com um **dashboard interativo em Streamlit**
para apoiar a tomada de decisão do gestor.

Esta fase dá continuidade às anteriores (mesmos sensores, mesma cultura e mesma
lógica de irrigação da Fase 2) e adiciona a camada de Inteligência Artificial:
previsão de **rendimento** e de **volume de irrigação**, com recomendações
automáticas de manejo.

---

## O que o projeto faz

- Prevê o **rendimento do milho** (sacas/ha) a partir das condições do solo.
- Prevê o **volume de irrigação** necessário (litros).
- Sugere **ações de manejo**: irrigar ou não, corrigir pH, aplicar fertilizante.
- Exibe tudo num **dashboard web** com métricas, correlações, simulador e tendências.

---

## Estrutura da pasta

```
fase4/
├── app.py                  # Dashboard Streamlit (interface do gestor)
├── requirements.txt        # Dependências do projeto
├── README.md               # Este arquivo
├── src/
│   ├── gerar_dados.py      # Gera o dataset sintético realista do milho
│   ├── treinar_modelo.py   # Pipeline de ML: treino, avaliação e gráficos
│   └── recomendacoes.py    # Regras de manejo a partir das previsões
├── dados/
│   └── dataset_milho.csv   # Base gerada (criada pelo gerar_dados.py)
├── modelos/
│   ├── modelo_rendimento_estimado.pkl
│   ├── modelo_volume_irrigacao.pkl
│   └── metricas.json       # Métricas MAE, MSE, RMSE e R² dos modelos
└── graficos/               # Imagens geradas no treino (correlação, etc.)
```

> **Sobre os dados:** o CSV da Fase 2 tinha apenas 8 linhas e nenhuma variável de
> resultado, o que é insuficiente para treinar ML. Como o enunciado permite
> "dados simulados de sensores virtuais", geramos um dataset maior e **coerente
> com a Fase 2** (mesmas variáveis, mesma cultura, mesma lógica agronômica),
> acrescentando os dois alvos a prever.

---

## Como executar (passo a passo)

### 1. Instalar as dependências

Recomendado usar um ambiente virtual:

```bash
cd fase4
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Gerar os dados

```bash
python src/gerar_dados.py
```

### 3. Treinar os modelos (gera .pkl, métricas e gráficos)

```bash
python src/treinar_modelo.py
```

### 4. Abrir o dashboard

```bash
streamlit run app.py
```

O navegador abre automaticamente em `http://localhost:8501`.

---

## Pipeline de Machine Learning

1. **Carregamento** do dataset (`dataset_milho.csv`).
2. **Análise de correlação** entre as variáveis (heatmap salvo em `graficos/`).
3. **Divisão treino/teste** (80% / 20%).
4. **Treino de dois algoritmos** para cada alvo:
   - Regressão Linear (base de comparação)
   - Random Forest (modelo não linear)
5. **Avaliação** com MAE, MSE, RMSE e R².
6. **Seleção** do melhor modelo (maior R²) e salvamento em `.pkl`.

### Resultados obtidos (conjunto de teste)

| Alvo                  | Melhor modelo  | R²    | MAE    | RMSE   |
|-----------------------|----------------|-------|--------|--------|
| Rendimento (sacas/ha) | Random Forest  | ~0,73 | ~5,6   | ~7,3   |
| Volume de irrigação   | Random Forest  | ~0,99 | ~22    | ~28    |

O Random Forest supera a Regressão Linear porque captura relações **não lineares**
(por exemplo, o efeito do déficit de umidade sobre o volume de irrigação).

---

## Bibliotecas utilizadas

- **scikit-learn** — modelos de regressão e métricas.
- **pandas / numpy** — manipulação e geração dos dados.
- **plotly** — gráficos interativos no dashboard.
- **matplotlib / seaborn** — gráficos salvos no treino.
- **streamlit** — interface web interativa.
- **joblib** — salvar/carregar os modelos treinados.

---

## Publicação online (opcional, Streamlit Community Cloud)

1. Suba a pasta `fase4/` no GitHub (já está no repositório).
2. Acesse share.streamlit.io e conecte sua conta GitHub.
3. Aponte o app para `fase4/app.py` e faça o deploy.
4. Garanta que `dados/` e `modelos/` estejam versionados no repositório, para o
   app encontrar os arquivos no servidor.
