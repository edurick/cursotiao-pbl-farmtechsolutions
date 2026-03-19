from calculos import (
    calcular_area_retangulo,
    calcular_area_circulo,
    calcular_insumos
)
from dados import (
    adicionar_registro,
    listar_registros,
    atualizar_registro,
    deletar_registro,
    exportar_para_csv,
    CULTURAS,
    FORMAS
)


def entrada_dados():
    """Fluxo completo de entrada de dados"""
    print("\n--- Entrada de Dados ---")

    # Selecionar cultura
    print("\nCulturas disponíveis:")
    for i, cultura in enumerate(CULTURAS, 1):
        print(f"{i}. {cultura}")

    while True:
        opcao_cultura = input("\nSelecione a cultura (1-2): ")
        if opcao_cultura in ["1", "2"]:
            cultura = CULTURAS[int(opcao_cultura) - 1]
            forma = FORMAS[cultura]
            break
        print("Opção inválida. Tente novamente.")

    # Solicitar medidas e calcular área
    print(f"\nForma geométrica: {forma}")
    area = 0

    if cultura == "Soja":
        while True:
            try:
                largura = float(input("Digite a largura (m): "))
                comprimento = float(input("Digite o comprimento (m): "))
                if largura > 0 and comprimento > 0:
                    area = calcular_area_retangulo(largura, comprimento)
                    print(f"Área calculada: {area:.2f} m²")
                    break
                print("Valores devem ser positivos.")
            except ValueError:
                print("Entrada inválida. Digite números válidos.")

    elif cultura == "Milho":
        while True:
            try:
                raio = float(input("Digite o raio (m): "))
                if raio > 0:
                    area = calcular_area_circulo(raio)
                    print(f"Área calculada: {area:.2f} m²")
                    break
                print("O raio deve ser positivo.")
            except ValueError:
                print("Entrada inválida. Digite um número válido.")

    # Dados do insumo
    print("\n--- Dados do Insumo ---")
    produto = input("Nome do produto: ")

    while True:
        try:
            dose = float(input("Dose por m² (litros): "))
            if dose >= 0:
                break
            print("A dose não pode ser negativa.")
        except ValueError:
            print("Entrada inválida.")

    while True:
        try:
            num_ruas = int(input("Número de ruas: "))
            if num_ruas > 0:
                break
            print("O número de ruas deve ser positivo.")
        except ValueError:
            print("Entrada inválida. Digite um número inteiro.")

    # Calcular total de insumo
    resultado_insumos = calcular_insumos(area, dose, num_ruas)
    total_insumo = resultado_insumos["total"]

    print(f"\nTotal de insumo necessário: {total_insumo:.2f} {resultado_insumos['unidade']}")

    # Criar registro e adicionar à lista
    registro = [cultura, forma, area, produto, dose, num_ruas, total_insumo]
    adicionar_registro(registro)
    print("\n✓ Registro adicionado com sucesso!")


def saida_dados():
    """Exibe todos os registros cadastrados"""
    print("\n--- Saída de Dados ---")
    listar_registros()


def atualizar_dados():
    """Atualiza um registro existente"""
    print("\n--- Atualização de Dados ---")
    listar_registros()

    if not len(registros_list := __import__("dados", fromlist=["registros"]).registros):
        return

    while True:
        try:
            index = int(input("\nDigite o índice do registro a atualizar: "))
            if 0 <= index < len(registros_list):
                break
            print(f"Índice deve estar entre 0 e {len(registros_list) - 1}.")
        except ValueError:
            print("Entrada inválida.")

    # Exibir registro atual
    reg_atual = registros_list[index]
    print(f"\nRegistro atual: {reg_atual}")

    # Selecionar nova cultura
    print("\nCulturas disponíveis:")
    for i, cultura in enumerate(CULTURAS, 1):
        print(f"{i}. {cultura}")

    while True:
        opcao_cultura = input("\nSelecione a cultura (1-2): ")
        if opcao_cultura in ["1", "2"]:
            cultura = CULTURAS[int(opcao_cultura) - 1]
            forma = FORMAS[cultura]
            break
        print("Opção inválida.")

    # Recalcular área
    area = 0
    if cultura == "Soja":
        while True:
            try:
                largura = float(input("Nova largura (m): "))
                comprimento = float(input("Novo comprimento (m): "))
                if largura > 0 and comprimento > 0:
                    area = calcular_area_retangulo(largura, comprimento)
                    break
                print("Valores devem ser positivos.")
            except ValueError:
                print("Entrada inválida.")
    else:
        while True:
            try:
                raio = float(input("Novo raio (m): "))
                if raio > 0:
                    area = calcular_area_circulo(raio)
                    break
                print("O raio deve ser positivo.")
            except ValueError:
                print("Entrada inválida.")

    # Novos dados do insumo
    produto = input("Novo nome do produto: ")

    while True:
        try:
            dose = float(input("Nova dose por m² (litros): "))
            if dose >= 0:
                break
            print("A dose não pode ser negativa.")
        except ValueError:
            print("Entrada inválida.")

    while True:
        try:
            num_ruas = int(input("Novo número de ruas: "))
            if num_ruas > 0:
                break
            print("O número de ruas deve ser positivo.")
        except ValueError:
            print("Entrada inválida.")

    total_insumo = calcular_insumos(area, dose, num_ruas)["total"]
    novo_registro = [cultura, forma, area, produto, dose, num_ruas, total_insumo]

    if atualizar_registro(index, novo_registro):
        print("\n✓ Registro atualizado com sucesso!")
    else:
        print("\n✗ Erro ao atualizar registro.")


def deletar_dados():
    """Remove um registro da lista"""
    print("\n--- Deleção de Dados ---")
    listar_registros()

    import dados
    if not dados.registros:
        return

    while True:
        try:
            index = int(input("\nDigite o índice do registro a deletar: "))
            if 0 <= index < len(dados.registros):
                break
            print(f"Índice deve estar entre 0 e {len(dados.registros) - 1}.")
        except ValueError:
            print("Entrada inválida.")

    if deletar_registro(index):
        print("\n✓ Registro deletado com sucesso!")
    else:
        print("\n✗ Erro ao deletar registro.")


def exportar_para_r():
    """Exporta dados para CSV compatível com R"""
    print("\n--- Exportar para R ---")
    import dados

    if not dados.registros:
        print("Não há registros para exportar.")
        return

    qtd = exportar_para_csv()
    print(f"\n✓ {qtd} registro(s) exportado(s) para 'dados_export.csv'")
    print("Execute 'Rscript estatisticas.R' para analisar os dados.")


def main():
    """Menu principal da aplicação"""
    while True:
        print("\n" + "=" * 40)
        print("    FarmTech Solutions")
        print("    Sistema de Gestão Agrícola")
        print("=" * 40)
        print("1. Entrada de dados")
        print("2. Saída de dados")
        print("3. Atualização")
        print("4. Deleção")
        print("5. Exportar para R")
        print("0. Sair")
        print("=" * 40)

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            entrada_dados()
        elif opcao == "2":
            saida_dados()
        elif opcao == "3":
            atualizar_dados()
        elif opcao == "4":
            deletar_dados()
        elif opcao == "5":
            exportar_para_r()
        elif opcao == "0":
            print("\nObrigado por usar FarmTech Solutions!")
            break
        else:
            print("\n✗ Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()
