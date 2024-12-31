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
                system.run()
            case _:
                print("Opção inválida")