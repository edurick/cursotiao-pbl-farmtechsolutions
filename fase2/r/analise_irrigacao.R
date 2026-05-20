#!/usr/bin/env Rscript

# Analise simples para apoiar a decisao da irrigacao.
# O script usa a mesma regra do ESP32 no ultimo registro da base.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)
script_path <- if (length(file_arg) > 0) sub("^--file=", "", file_arg[1]) else NA_character_
script_dir <- if (!is.na(script_path)) dirname(normalizePath(script_path)) else getwd()
arquivo_padrao <- file.path(script_dir, "..", "dados", "cenarios_irrigacao.csv")

args_trailing <- commandArgs(trailingOnly = TRUE)
arquivo <- if (length(args_trailing) >= 1) args_trailing[1] else arquivo_padrao

dados <- read.csv(arquivo)

colunas_necessarias <- c("umidade_solo", "ph", "n", "p", "k", "chuva_prevista")
faltando <- setdiff(colunas_necessarias, names(dados))

if (length(faltando) > 0) {
  stop(paste("Colunas obrigatorias ausentes:", paste(faltando, collapse = ", ")))
}

media_umidade <- mean(dados$umidade_solo)
mediana_umidade <- median(dados$umidade_solo)
desvio_umidade <- sd(dados$umidade_solo)
quartil_umidade <- as.numeric(quantile(dados$umidade_solo, 0.25))

media_ph <- mean(dados$ph)
desvio_ph <- sd(dados$ph)

ultima <- tail(dados, 1)
irrigar <- with(
  ultima,
  umidade_solo <= 55 &
    ph >= 5.5 &
    ph <= 7.0 &
    n == 1 &
    p == 1 &
    k == 1 &
    chuva_prevista == 0
)

cat("=== FarmTech Solutions | Analise em R ===

")
cat("Arquivo analisado:", arquivo, "
")
cat("Total de cenarios:", nrow(dados), "

")

cat("--- Estatisticas de Umidade ---
")
cat(sprintf("Media: %.2f%%
", media_umidade))
cat(sprintf("Mediana: %.2f%%
", mediana_umidade))
cat(sprintf("Desvio padrao: %.2f
", desvio_umidade))
cat(sprintf("1o quartil: %.2f%%

", quartil_umidade))

cat("--- Estatisticas de pH ---
")
cat(sprintf("Media: %.2f
", media_ph))
cat(sprintf("Desvio padrao: %.2f

", desvio_ph))

cat("--- Ultimo cenario ---
")
cat(sprintf("Umidade: %.1f%%
", ultima$umidade_solo))
cat(sprintf("pH: %.2f
", ultima$ph))
cat(sprintf("N=%d P=%d K=%d
", ultima$n, ultima$p, ultima$k))
cat(sprintf("Chuva prevista: %d

", ultima$chuva_prevista))

if (irrigar) {
  cat("Recomendacao final: LIGAR A BOMBA
")
} else {
  cat("Recomendacao final: DESLIGAR A BOMBA
")
}
