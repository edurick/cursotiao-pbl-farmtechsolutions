# FarmTech Solutions - Fase 2

Esta pasta concentra a entrega da fase 2, com simulacao no Wokwi, codigo para ESP32, integracao em Python e analise em R.

## Estrutura

- `esp32/`: `sketch.ino`, `diagram.json` e `libraries.txt`
- `python/`: integracao opcional com API meteorologica
- `r/`: analise estatistica simples da irrigacao
- `dados/`: bases de apoio usadas na analise
- `docs/`: documentacao visual do circuito

## Arquivos principais

- `esp32/sketch.ino`
- `esp32/diagram.json`
- `esp32/libraries.txt`
- `python/previsao_chuva.py`
- `r/analise_irrigacao.R`
- `dados/cenarios_irrigacao.csv`
- `docs/circuito-fase2.svg`

## Video de demonstracao

- https://youtu.be/E9An0S39GFg

## Cultura escolhida

Foi adotado o milho, porque a regiao tecnica do projeto precisa de uma cultura que reaja de forma clara a chuva, umidade, pH e nutrientes.

## Como simular no Wokwi

1. Crie um projeto novo com ESP32.
2. Copie `esp32/sketch.ino` para o `sketch.ino` do projeto.
3. Copie `esp32/diagram.json` para o `diagram.json`.
4. Copie `esp32/libraries.txt` para o `libraries.txt`.
5. Rode a simulacao.

## Integracao em Python

O script `python/previsao_chuva.py` consulta a API Open-Meteo e gera um comando para o Serial Monitor do ESP32.

## Analise em R

O script `r/analise_irrigacao.R` faz uma analise simples sobre cenarios de sensores e aplica a regra de irrigacao usada no ESP32.
