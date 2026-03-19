import math


def calcular_area_retangulo(largura: float, comprimento: float) -> float:
    """Retorna área do retângulo em m²"""
    return largura * comprimento


def calcular_area_circulo(raio: float) -> float:
    """Retorna área do círculo em m²"""
    return math.pi * (raio ** 2)


def calcular_insumos(area: float, dose_por_m2: float, num_ruas: int) -> dict:
    """Retorna total de insumo necessário"""
    total = dose_por_m2 * area
    return {"total": total, "unidade": "litros"}
