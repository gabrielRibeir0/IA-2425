from src.Graph import Graph
from Graph import Graph
from Node import Node
from Package import Package
from Vehicle import Vehicle


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

                else:
                    print("Invalid option")
                    break







