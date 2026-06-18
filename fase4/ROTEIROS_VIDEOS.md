# Roteiros dos vídeos — FarmTech Solutions Fase 4

Dois vídeos de até 5 minutos cada. O sistema é o mesmo; cada vídeo enfatiza um
ângulo. Grave a tela (ex.: OBS, Loom ou a gravação nativa do sistema) com o
dashboard já aberto e os modelos já treinados.

Antes de gravar, rode uma vez:
```
python src/gerar_dados.py
python src/treinar_modelo.py
streamlit run app.py
```

---

## VÍDEO 1 — Parte 1 (integração ML + dashboard Streamlit)

Foco: mostrar que o modelo treinado está conectado a um dashboard que o gestor usa.

**(0:00–0:30) Abertura**
- "Olá, sou [nome]. Este é o projeto FarmTech Solutions, Fase 4. O objetivo é
  aplicar Machine Learning sobre os dados do milho e entregar as previsões num
  dashboard para o gestor agrícola."
- Mostre a estrutura de pastas rapidamente (src, dados, modelos, app.py).

**(0:30–1:30) Bibliotecas e pipeline**
- Abra `src/treinar_modelo.py`. Explique: "Uso scikit-learn para os modelos de
  regressão, pandas e numpy para os dados, e joblib para salvar os modelos."
- Cite o pipeline: carregar dados, analisar correlação, dividir treino/teste,
  treinar Regressão Linear e Random Forest, avaliar com MAE, MSE, RMSE e R².

**(1:30–3:30) Dashboard em funcionamento**
- Abra o dashboard no navegador.
- Aba **Visão Geral**: mostre as métricas dos dois modelos e explique que R²
  perto de 1 é melhor.
- Aba **Correlações**: mostre o heatmap e explique uma correlação (ex.: umidade
  do solo tem relação negativa forte com o volume de irrigação).
- Aba **Previsão Interativa**: mova os sliders (deixe o solo seco, pH baixo) e
  mostre a previsão e as recomendações mudando em tempo real.

**(3:30–4:30) Integração explicada**
- "O dashboard carrega os modelos .pkl com joblib e, a cada ajuste dos sliders,
  chama o modelo para prever e o módulo de recomendações para sugerir a ação."

**(4:30–5:00) Fechamento**
- Resuma: dados → modelo → dashboard interativo. Encerre.

---

## VÍDEO 2 — Parte 2 (modelos preditivos e recomendações)

Foco: a modelagem, as métricas e a justificativa das recomendações.

**(0:00–0:30) Abertura**
- "Neste vídeo mostro o pipeline de Machine Learning da Fase 4: tratamento de
  dados, treino, validação e as recomendações geradas."

**(0:30–1:30) Tratamento e geração de dados**
- Abra `src/gerar_dados.py`. Explique por que foi necessário simular dados
  (o CSV da Fase 2 tinha só 8 linhas e nenhum alvo) e que o dataset é coerente
  com a Fase 2 (mesmas variáveis, cultura milho, lógica agronômica).
- Rode `python src/gerar_dados.py` e mostre o resumo no terminal.

**(1:30–3:00) Treino e validação**
- Rode `python src/treinar_modelo.py`.
- Mostre no terminal as métricas dos dois modelos para cada alvo.
- Explique: "Comparo Regressão Linear e Random Forest. O Random Forest vence
  porque captura relações não lineares. Para o volume de irrigação o R² chega
  perto de 0,99; para o rendimento fica em torno de 0,73, pois há mais ruído,
  o que é realista."
- Mostre os gráficos em `graficos/` (correlação, real vs previsto, importância).

**(3:00–4:30) Previsões e recomendações**
- No dashboard, aba **Previsão Interativa**: monte um cenário de seca + nutriente
  faltando. Mostre a previsão de rendimento, o volume sugerido e as três
  recomendações (irrigar, corrigir pH, fertilizar).
- Aba **Tendências**: mostre como o rendimento sobe conforme o número de
  nutrientes OK e como a irrigação cresce quando a umidade cai.

**(4:30–5:00) Interpretação e fechamento**
- "As recomendações combinam a previsão do modelo com regras agronômicas (faixa
  de pH e alvo de umidade), oferecendo ao gestor uma decisão clara e justificada."
- Encerre.

---

## Dicas rápidas

- Fale com calma; é melhor cobrir bem 80% do que correr por 100%.
- Deixe o dashboard e o terminal já abertos antes de gravar.
- Se passar de 5 minutos, corte a parte de explicar código e priorize a demo.
