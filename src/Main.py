from jeepney.low_level import Boolean

from src.Graph import Graph
from Graph import Graph
from Node import Node
from Package import Package
from Vehicle import Vehicle

import os

class Main:
    def __init__(self):
        self.graph = Graph()
        self.packages = []
        self.vehicles = []
        self.time = 1 # ver depois como se faz a cena do tempo

        def interface(self):
            exit=0

            while exit==0:
                print("1-Load graph")
                print("2-Load nodes")
                print("3-Load packages")
                print("4-Load vehicles")
                # mais ideias de cenas
                print("0-Exit")


                option = int(input("Choose Option: "))

                if option == 0:
                    exit=1
                elif option == 1:
                    filename = (input("Write the name of the graph file: "))
                    aux = False
                    while not aux:
                        if self.graph.loadGrapFile(filename):
                            aux = True
                    break
                elif option == 2:
                    filename = (input("Write the name of the nodes file: "))
                    aux = False
                    while not aux:
                        if self.graph.loadNodesFile(filename):
                            aux = True
                    break
                elif option == 3:
                    filename = (input("Write the name of the packages file: "))
                    aux = False
                    while not aux:
                        if self.loadPackagesFile(filename):
                            aux = True
                    break
                elif option == 4:
                    filename = (input("Write the name of the vehicles file: "))
                    aux = False
                    while not aux:
                        if self.loadVehicles(filename):
                            aux = True
                    break

                else:
                    print("Invalid option")
                    break




    def loadVehiclesFile(self, file_name):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_directory, '..', 'input', file_name)

        if not os.path.exists(file_path):
            print("Error: File '{file_name}' not found in 'graphs' directory.")
            return False
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line.startswith("#") or not line:  # Ignore comments and empty lines
                        continue
                    id, type, gas, location = line.split()
                    gas = int(gas)
                    v = Vehicle(id, type, gas, location)
                    self.vehicles.append(v)
            print("Vehicles loaded successfully.")
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            return False

    def loadPackagesFile(self, file_name):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_directory, '..', 'input', file_name)

        if not os.path.exists(file_path):
            print("Error: File '{file_name}' not found in 'graphs' directory.")
            return False
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line.startswith("#") or not line:  # Ignore comments and empty lines
                        continue
                    id, location, destination, weight = line.split() # é preciso ver como se vai pôr a data limite de entrega
                    weight = int(weight)
                    p = Package(id, location, destination, weight)
                    self.packages.append(p)
            print("Vehicles loaded successfully.")
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            return False





