#!/usr/bin/env Rscript

# Analise simples para apoiar a decisao da irrigacao.
# O script usa a mesma regra do ESP32 no ultimo registro da base.

args <- commandArgs(trailingOnly = TRUE)
arquivo <- if (length(args) >= 1) args[1] else "fase2/r/cenarios_irrigacao.csv"

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

cat("=== FarmTech Solutions | Analise em R ===\n\n")
cat("Arquivo analisado:", arquivo, "\n")
cat("Total de cenarios:", nrow(dados), "\n\n")

cat("--- Estatisticas de Umidade ---\n")
cat(sprintf("Media: %.2f%%\n", media_umidade))
cat(sprintf("Mediana: %.2f%%\n", mediana_umidade))
cat(sprintf("Desvio padrao: %.2f\n", desvio_umidade))
cat(sprintf("1o quartil: %.2f%%\n\n", quartil_umidade))

cat("--- Estatisticas de pH ---\n")
cat(sprintf("Media: %.2f\n", media_ph))
cat(sprintf("Desvio padrao: %.2f\n\n", desvio_ph))

cat("--- Ultimo cenario ---\n")
cat(sprintf("Umidade: %.1f%%\n", ultima$umidade_solo))
cat(sprintf("pH: %.2f\n", ultima$ph))
cat(sprintf("N=%d P=%d K=%d\n", ultima$n, ultima$p, ultima$k))
cat(sprintf("Chuva prevista: %d\n\n", ultima$chuva_prevista))

if (irrigar) {
  cat("Recomendacao final: LIGAR A BOMBA\n")
} else {
  cat("Recomendacao final: DESLIGAR A BOMBA\n")
}
