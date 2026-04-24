#!/usr/bin/env python3
"""Consulta previsao de chuva na Open-Meteo e gera comando para o ESP32."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from typing import Any
from urllib.parse import urlencode
from urllib.error import URLError
from urllib.request import urlopen


def montar_url(latitude: float, longitude: float, fuso: str) -> str:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "precipitation_probability,precipitation",
        "forecast_days": 2,
        "timezone": fuso,
    }
    return f"https://api.open-meteo.com/v1/forecast?{urlencode(params)}"


def obter_previsao(url: str) -> dict[str, Any]:
    with urlopen(url, timeout=20) as resposta:
        return json.load(resposta)


def selecionar_janela(payload: dict[str, Any], horizonte_horas: int) -> list[dict[str, Any]]:
    horarios = payload["hourly"]["time"]
    probabilidades = payload["hourly"]["precipitation_probability"]
    precipitacoes = payload["hourly"]["precipitation"]

    agora = datetime.now().replace(minute=0, second=0, microsecond=0)
    amostras: list[dict[str, Any]] = []

    for horario, probabilidade, precipitacao in zip(horarios, probabilidades, precipitacoes):
        instante = datetime.fromisoformat(horario)
        if instante < agora:
            continue

        amostras.append(
            {
                "hora": instante,
                "probabilidade": float(probabilidade),
                "precipitacao": float(precipitacao),
            }
        )

        if len(amostras) >= horizonte_horas:
            break

    return amostras


def analisar_chuva(
    amostras: list[dict[str, Any]],
    limiar_probabilidade: float,
    limiar_mm: float,
) -> tuple[bool, float, float]:
    if not amostras:
        return False, 0.0, 0.0

    maior_probabilidade = max(item["probabilidade"] for item in amostras)
    chuva_total = sum(item["precipitacao"] for item in amostras)
    chuva_prevista = maior_probabilidade >= limiar_probabilidade or chuva_total >= limiar_mm
    return chuva_prevista, maior_probabilidade, chuva_total


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Consulta previsao de chuva e sugere CHUVA=1 ou CHUVA=0 para o ESP32."
    )
    parser.add_argument("--cidade", default="Sao Paulo")
    parser.add_argument("--latitude", type=float, default=-23.5505)
    parser.add_argument("--longitude", type=float, default=-46.6333)
    parser.add_argument("--timezone", default="America/Sao_Paulo")
    parser.add_argument("--horizonte", type=int, default=6, help="Horas analisadas a partir de agora.")
    parser.add_argument(
        "--limiar-probabilidade",
        type=float,
        default=60.0,
        help="Probabilidade minima de chuva para bloquear irrigacao.",
    )
    parser.add_argument(
        "--limiar-mm",
        type=float,
        default=2.0,
        help="Precipitacao acumulada minima (mm) para bloquear irrigacao.",
    )
    args = parser.parse_args()

    url = montar_url(args.latitude, args.longitude, args.timezone)
    try:
        payload = obter_previsao(url)
    except URLError as erro:
        print("Nao foi possivel consultar a Open-Meteo.")
        print(f"Erro: {erro}")
        print("Comando sugerido para o ESP32: CHUVA=0")
        return

    janela = selecionar_janela(payload, args.horizonte)
    chuva_prevista, maior_probabilidade, chuva_total = analisar_chuva(
        janela,
        args.limiar_probabilidade,
        args.limiar_mm,
    )

    print("=== Previsao de Chuva para Irrigacao Inteligente ===")
    print(f"Cidade: {args.cidade}")
    print(f"Coordenadas: {args.latitude:.4f}, {args.longitude:.4f}")
    print(f"Horizonte analisado: {args.horizonte} hora(s)")
    print()

    if not janela:
        print("Nao foi possivel montar a janela de previsao.")
        print("Comando sugerido para o ESP32: CHUVA=0")
        return

    print("Amostras consideradas:")
    for item in janela:
        print(
            f"- {item['hora'].strftime('%Y-%m-%d %H:%M')} | "
            f"prob={item['probabilidade']:.0f}% | "
            f"prec={item['precipitacao']:.2f} mm"
        )

    print()
    print(f"Maior probabilidade de chuva: {maior_probabilidade:.0f}%")
    print(f"Precipitacao acumulada prevista: {chuva_total:.2f} mm")
    print(f"Limiar adotado: {args.limiar_probabilidade:.0f}% ou {args.limiar_mm:.1f} mm")
    print()

    if chuva_prevista:
        print("Decisao: ha risco relevante de chuva. Suspender irrigacao automatica.")
        print("Comando sugerido para o ESP32: CHUVA=1")
    else:
        print("Decisao: nao ha chuva relevante na janela analisada.")
        print("Comando sugerido para o ESP32: CHUVA=0")


if __name__ == "__main__":
    main()
