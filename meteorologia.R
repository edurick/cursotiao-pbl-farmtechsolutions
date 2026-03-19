#!/usr/bin/env Rscript

# FarmTech Solutions - Dados Meteorológicos
# Script para obter dados climáticos em tempo real
# NÃO requer pacotes externos - usa apenas R base

# Configuração da localização (São Paulo - pode ser alterado)
LATITUDE <- -23.5505
LONGITUDE <- -46.6333
CIDADE <- "São Paulo"

cat("\n=== FarmTech Solutions - Dados Meteorológicos ===\n\n")
cat(sprintf("Obtendo dados para: %s\n", CIDADE))
cat(sprintf("Coordenadas: %.4f, %.4f\n\n", LATITUDE, LONGITUDE))

# Construir URL da API Open-Meteo
url <- sprintf(
  "https://api.open-meteo.com/v1/forecast?latitude=%.4f&longitude=%.4f&current_weather=true",
  LATITUDE, LONGITUDE
)

# Baixar dados usando R base (sem pacotes externos)
tryCatch({
  resposta <- readLines(url, warn = FALSE)
  conteudo <- paste(resposta, collapse = "")

  # Extrair temperatura usando regex
  temp_match <- regmatches(conteudo, regexpr('"temperature":[0-9.-]+', conteudo))
  temperatura <- as.numeric(sub('"temperature":', '', temp_match))

  # Extrair velocidade do vento
  vento_match <- regmatches(conteudo, regexpr('"windspeed":[0-9.-]+', conteudo))
  vento <- as.numeric(sub('"windspeed":', '', vento_match))

  # Extrair direção do vento
  direcao_match <- regmatches(conteudo, regexpr('"winddirection":[0-9.-]+', conteudo))
  direcao_vento <- as.numeric(sub('"winddirection":', '', direcao_match))

  # Extrair horário
  tempo_match <- regmatches(conteudo, regexpr('"time":"[^"]+"', conteudo))
  horario <- sub('"time":"', '', tempo_match)
  horario <- sub('"', '', horario)

  # Exibir dados atuais
  cat("--- Condições Atuais ---\n\n")
  cat(sprintf("Temperatura: %.1f°C\n", temperatura))
  cat(sprintf("Velocidade do Vento: %.1f km/h\n", vento))
  cat(sprintf("Direção do Vento: %.0f°\n", direcao_vento))
  cat(sprintf("Horário da medição: %s\n\n", horario))

  # Recomendações agrícolas baseadas nas condições
  cat("--- Recomendações Agrícolas ---\n\n")

  if (temperatura < 10) {
    cat("A Temperatura baixa. Atencao ao risco de geada em culturas sensíveis.\n")
  } else if (temperatura >= 10 && temperatura < 20) {
    cat("+ Temperatura adequada para desenvolvimento vegetativo.\n")
  } else if (temperatura >= 20 && temperatura < 32) {
    cat("+ Temperatura ideal para crescimento da maioria das culturas.\n")
  } else {
    cat("A Temperatura elevada. Aumentar frequência de irrigacao se necessário.\n")
  }

  if (vento < 10) {
    cat("+ Vento fraco. Boas condicoes para aplicacao de insumos.\n")
  } else if (vento >= 10 && vento < 25) {
    cat("A Vento moderado. Cuidado com deriva de produtos químicos.\n")
  } else {
    cat("A Vento forte. Nao recomendado aplicar insumos.\n")
  }

  cat("\n=== Dados Meteorológicos Obtidos ===\n")

}, error = function(e) {
  cat("ERRO: Nao foi possivel obter os dados meteorologicos.\n")
  cat("Verifique sua conexao com a internet.\n")
  cat("Erro:", conditionMessage(e), "\n")
  quit(status = 1)
})
