def mainMenu(system):
    while True:
        print("\n--- Menu Principal ---\n")
        print("1 - Iniciar simulação")
        print("0 - Sair")

        try:
            opcao = int(input("\nIntroduza a sua opção - "))
        except ValueError:
            opcao = -1

        match opcao:
            case 0:
                print("... A sair ...")
                break
            case 1:
                menuEscolhas(system)
            case _:
                print("Opção inválida")

def menuEscolhas(system):
    print("\n--- Critério de ordenação das zonas ---\n")
    print("1 - Janela de tempo restante")
    print("2 - Prioridade das zonas")
    print("0 - Voltar")

    try:
        opcao = int(input("\nIntroduza a sua opção - "))
    except ValueError:
        opcao = -1
    
    match opcao:
        case 0:
            return
        case 1:
            criterio = "Tempo"
        case 2:
            criterio = "Prioridade"
        case _:
            print("Opção inválida")
            return

    results = system.run(criterio)
    while True:
        print("\n--- Algoritmo a consultar ---\n")
        print("1 - A*")
        print("2 - Greedy")
        print("3 - DFS")
        print("4 - BFS")
        print("5 - Ver Condições")
        print("0 - Voltar")

        try:
            opcao = int(input("\nIntroduza a sua opção - "))
        except ValueError:
            opcao = -1
        
        match opcao:
            case 0:
                return
            case 1:
                print(results["A*"])
            case 2:
                print(results["Greedy"])
            case 3:
                print(results["DFS"])
            case 4:
                print(results["BFS"])
            case 5:
                print(results["CONDITIONS"])
            case _:
                print("Opção inválida")