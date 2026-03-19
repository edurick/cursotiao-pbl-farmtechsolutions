# Lista principal de registros
# Cada registro: [cultura, forma, area, produto, dose, num_ruas, total_insumo]
registros = []

# Culturas disponíveis
CULTURAS = ["Soja", "Milho"]

# Formas geométricas
FORMAS = {"Soja": "Retângulo", "Milho": "Círculo"}


def adicionar_registro(registro):
    """Insere um novo registro no final da lista"""
    registros.append(registro)


def listar_registros():
    """Exibe todos os registros usando loop for"""
    if not registros:
        print("\nNenhum registro encontrado.")
        return

    print("\n" + "=" * 80)
    print(f"{'Índice':<8}{'Cultura':<12}{'Forma':<12}{'Área (m²)':<12}{'Produto':<15}{'Dose':<10}{'Ruas':<8}{'Total (L)':<10}")
    print("=" * 80)

    for i, reg in enumerate(registros):
        cultura, forma, area, produto, dose, num_ruas, total_insumo = reg
        print(f"{i:<8}{cultura:<12}{forma:<12}{area:<12.2f}{produto:<15}{dose:<10.2f}{num_ruas:<8}{total_insumo:<10.2f}")


def atualizar_registro(index, novo_dados):
    """Modifica um registro em uma posição específica"""
    if 0 <= index < len(registros):
        registros[index] = novo_dados
        return True
    return False


def deletar_registro(index):
    """Remove um registro da lista"""
    if 0 <= index < len(registros):
        del registros[index]
        return True
    return False


def exportar_para_csv():
    """Exporta registros para formato CSV compatível com R"""
    import csv

    with open("dados_export.csv", "w", newline="") as arquivo:
        writer = csv.writer(arquivo)
        writer.writerow(["cultura", "forma", "area", "produto", "dose", "num_ruas", "total_insumo"])
        for reg in registros:
            writer.writerow(reg)

    return len(registros)
