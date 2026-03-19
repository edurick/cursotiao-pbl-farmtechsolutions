#!/usr/bin/env Rscript

# FarmTech Solutions - Análise Estatística
# Script para análise estatística dos dados agrícolas

# Ler dados exportados pelo Python
dados <- read.csv("dados_export.csv")

# Exibir resumo dos dados
cat("\n=== FarmTech Solutions - Análise Estatística ===\n\n")
cat("Total de registros:", nrow(dados), "\n\n")

# Verificar se há dados suficientes
if (nrow(dados) == 0) {
  cat("ERRO: Nenhum dado encontrado para análise.\n")
  quit(status = 1)
}

# Estatísticas por cultura
cat("--- Estatísticas por Cultura ---\n\n")

culturas <- unique(dados$cultura)

for (cultura in culturas) {
  subset_dados <- dados[dados$cultura == cultura, ]
  n_registros <- nrow(subset_dados)

  cat(sprintf("Cultura: %s\n", cultura))
  cat(sprintf("  Registros: %d\n", n_registros))
  cat(sprintf("  Área Média: %.2f m²\n", mean(subset_dados$area)))

  # Só exibe desvio padrão se houver 2 ou mais registros
  if (n_registros >= 2) {
    cat(sprintf("  Desvio Padrão (Área): %.2f m²\n", sd(subset_dados$area)))
  }

  cat(sprintf("  Insumo Médio: %.2f litros\n", mean(subset_dados$total_insumo)))

  # Só exibe desvio padrão se houver 2 ou mais registros
  if (n_registros >= 2) {
    cat(sprintf("  Desvio Padrão (Insumo): %.2f litros\n", sd(subset_dados$total_insumo)))
  }

  cat("\n")
}

# Estatísticas gerais
cat("--- Estatísticas Gerais ---\n\n")

n_total <- nrow(dados)

media_area <- mean(dados$area)
area_min <- min(dados$area)
area_max <- max(dados$area)

media_insumo <- mean(dados$total_insumo)
insumo_min <- min(dados$total_insumo)
insumo_max <- max(dados$total_insumo)

cat(sprintf("Área (m²):\n"))
cat(sprintf("  Média: %.2f\n", media_area))

if (n_total >= 2) {
  cat(sprintf("  Desvio Padrão: %.2f\n", sd(dados$area)))
}

cat(sprintf("  Mínima: %.2f\n", area_min))
cat(sprintf("  Máxima: %.2f\n\n", area_max))

cat(sprintf("Insumos (litros):\n"))
cat(sprintf("  Média: %.2f\n", media_insumo))

if (n_total >= 2) {
  cat(sprintf("  Desvio Padrão: %.2f\n", sd(dados$total_insumo)))
}

cat(sprintf("  Mínimo: %.2f\n", insumo_min))
cat(sprintf("  Máximo: %.2f\n\n", insumo_max))

# Distribuição por forma geométrica
cat("--- Distribuição por Forma Geométrica ---\n\n")
table_formas <- table(dados$forma)
print(table_formas)
cat("\n")

cat("=== Análise Concluída ===\n")
