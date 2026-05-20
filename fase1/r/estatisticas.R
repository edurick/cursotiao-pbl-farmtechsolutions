#!/usr/bin/env Rscript

# FarmTech Solutions - Analise Estatistica
# Script para analise estatistica dos dados agricolas

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)
script_path <- if (length(file_arg) > 0) sub("^--file=", "", file_arg[1]) else NA_character_
script_dir <- if (!is.na(script_path)) dirname(normalizePath(script_path)) else getwd()
arquivo_padrao <- file.path(script_dir, "..", "dados", "dados_export.csv")

# Ler dados exportados pelo Python
arquivo <- if (length(commandArgs(trailingOnly = TRUE)) >= 1) commandArgs(trailingOnly = TRUE)[1] else arquivo_padrao

dados <- read.csv(arquivo)

# Exibir resumo dos dados
cat("
=== FarmTech Solutions - Analise Estatistica ===

")
cat("Total de registros:", nrow(dados), "

")

# Verificar se ha dados suficientes
if (nrow(dados) == 0) {
  cat("ERRO: Nenhum dado encontrado para analise.
")
  quit(status = 1)
}

# Estatisticas por cultura
cat("--- Estatisticas por Cultura ---

")

culturas <- unique(dados$cultura)

for (cultura in culturas) {
  subset_dados <- dados[dados$cultura == cultura, ]
  n_registros <- nrow(subset_dados)

  cat(sprintf("Cultura: %s
", cultura))
  cat(sprintf("  Registros: %d
", n_registros))
  cat(sprintf("  Area Media: %.2f m²
", mean(subset_dados$area)))

  # So exibe desvio padrao se houver 2 ou mais registros
  if (n_registros >= 2) {
    cat(sprintf("  Desvio Padrao (Area): %.2f m²
", sd(subset_dados$area)))
  }

  cat(sprintf("  Insumo Medio: %.2f litros
", mean(subset_dados$total_insumo)))

  # So exibe desvio padrao se houver 2 ou mais registros
  if (n_registros >= 2) {
    cat(sprintf("  Desvio Padrao (Insumo): %.2f litros
", sd(subset_dados$total_insumo)))
  }

  cat("
")
}

# Estatisticas gerais
cat("--- Estatisticas Gerais ---

")

n_total <- nrow(dados)

media_area <- mean(dados$area)
area_min <- min(dados$area)
area_max <- max(dados$area)

media_insumo <- mean(dados$total_insumo)
insumo_min <- min(dados$total_insumo)
insumo_max <- max(dados$total_insumo)

cat(sprintf("Area (m²):
"))
cat(sprintf("  Media: %.2f
", media_area))

if (n_total >= 2) {
  cat(sprintf("  Desvio Padrao: %.2f
", sd(dados$area)))
}

cat(sprintf("  Minima: %.2f
", area_min))
cat(sprintf("  Maxima: %.2f

", area_max))

cat(sprintf("Insumos (litros):
"))
cat(sprintf("  Media: %.2f
", media_insumo))

if (n_total >= 2) {
  cat(sprintf("  Desvio Padrao: %.2f
", sd(dados$total_insumo)))
}

cat(sprintf("  Minimo: %.2f
", insumo_min))
cat(sprintf("  Maximo: %.2f

", insumo_max))

# Distribuicao por forma geometrica
cat("--- Distribuicao por Forma Geometrica ---

")
table_formas <- table(dados$forma)
print(table_formas)
cat("
")

cat("=== Analise Concluida ===
")
