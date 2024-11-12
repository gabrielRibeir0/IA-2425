import csv
import math
import os
import time
from queue import Queue
from queue import PriorityQueue

import networkx as nx
from matplotlib import pyplot as plt
from networkx.classes import Graph
from Node import Node

class Graph:
    def __init__(self, directed=False):
        self.nodes = []
        self.directed = directed
        self.graph = {} # node1 -> (node2,(type,distance)) //type-road,water,air
        self.heuristics = {}
        self.temporarily_blocked_edges = {}
        self.temporarily_delayed_edges = {}

    def get_node_by_id(self, id):

        for node in self.nodes:
            if node.getId() == id:
                return node

        return None

    def print_edge(self):
        listA = ""
        list = self.graph.keys()
        for node in list:
            for (node2, (type,weight)) in self.graph[node]:
                listA = listA + node + " ->" + node2 + " weight:" + str(weight) + "\n"
        return listA

    def add_edge(self, node1, node2, type, weight):
        n1 = node1.getId()
        n2 = node2.getId()

        if self.get_node_by_id(n1) is None:
            # ver depois se aqui é que se tem de dar o id ao node
            self.nodes.append(node1)
            self.graph[n1] = []

        if self.get_node_by_id(n2) is None:
            # ver depois se aqui é que se tem de dar o id ao node
            self.nodes.append(node2)
            self.graph[n2] = []

        self.graph[n1].append((n2, (type,weight)))

        if not self.directed:
            self.graph[n2].append((n1, (type,weight)))

    def get_nodes(self):
        return self.nodes

    def get_arc_cost(self, node1, node2):
        costT = math.inf
        a = self.graph[node1]  # lista de arestas para aquele nodo
        for (node, (type,weight)) in a:
            if node == node2:
                costT = weight

        return costT

    def calculate_cost(self, path):
        # path é uma lista de nodos
        test = path
        cost = 0
        i = 0
        while i + 1 < len(test):
            cost = cost + self.get_arc_cost(test[i], test[i + 1])
            i = i + 1
        return cost

    def add_heuristic(self, node, estima):
        if node in self.nodes:
            self.heuristics[node] = estima

    def heuristic(self):
        nodes = self.graph.keys()
        for n in nodes:
            self.heuristics[n] = 1  # define a heuristica para cada nodo como 1
        return True  # A atribuição de heuristica foi concluida com sucesso

    def get_heuristic(self, node):
        return self.heuristics[node]

    def getNeighbours(self, node):
        list = []
        for (adjacent, (type,weight)) in self.graph[node]:
            list.append((adjacent, weight))
        return list

    def draw(self):
        list_v = self.nodes
        g = nx.Graph()

        for node in list_v:
            n = node.getId()
            g.add_node(n)
            for (adjacent, (type,weight)) in self.graph[n]:
                lista = (n, adjacent)
                # lista_a.append(lista)
                g.add_edge(n, adjacent, weight=weight)

        pos = nx.spring_layout(g)
        nx.draw_networkx(g, pos, with_labels=True, font_weight='bold')
        labels = nx.get_edge_attributes(g, 'weight')
        nx.draw_networkx_edge_labels(g, pos, edge_labels=labels)
        plt.draw()
        plt.show()

        def loadGraphFile(self, file_name):
            current_directory = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(current_directory, '..', 'graphs', file_name)

            if not os.path.exists(file_path):
                print("Error: File '{file_name}' not found in 'graphs' directory.")
                return False
            try:
                with open(file_path, 'r') as file:
                    for line in file:
                        line = line.strip()
                        if line.startswith("#") or not line:  # Ignore comments and empty lines
                            continue
                        node1, node2, connection_type, weight = line.split()
                        weight = int(weight)
                        self.add_edge(node1, node2, connection_type, weight)
                print("Graph loaded successfully.")
                return True
            except Exception as e:
                print(f"An error occurred: {e}")
                return False

        def loadNodeFile(self, file_name):
            current_directory = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(current_directory, '..', 'input', file_name)

            if not os.path.exists(file_path):
                print("Error: File '{file_name}' not found in 'input' directory.")
                return
            try:
                with open(file_path, 'r') as file:
                    for line in file:
                        line = line.strip()
                        if line.startswith("#") or not line:  # Ignore comments and empty lines
                            continue
                        id, priority, population= line.split()
                        population = int(population)
                        node = Node(id, priority, population)
                        self.nodes.append(node)
                print("Graph loaded successfully.")
            except Exception as e:
                print("An error occurred: {e}")

        def block_edge(self, node1, node2, temporary_duration=None): # duração está em horas
            if node1 in self.graph:
                for (adjacent, (type,weight)) in self.graph[node1]:
                    if adjacent == node2:
                        if temporary_duration: # bloquear temporariamente
                            unblock_time = time.time() + (temporary_duration*3600) # passar horas para segundos
                            self.temporarily_blocked_edges[node1] = (node2,(type,weight,unblock_time))
                            self.graph[node1].remove(adjacent, (type, weight))
                            if not self.directed:
                                self.temporarily_blocked_roads[node2] = (node1, (type, weight, unblock_time))
                                self.graph[node2].remove(adjacent, (type, weight))
                        else: # apagar para sempre
                            self.graph[node1].remove(adjacent, (type, weight))
                            if not self.directed:
                                self.graph[node2].remove(adjacent,(type,weight))
                        break


        def reenable_edges(self): # provavelmente vai ter de funcionar em loop ou de x em x tempo
            current_time = time.time()
            edges_to_restore = []

            for node1,(node2,(type,weight,unblock_time)) in self.temporarily_blocked_edges.items():
                if current_time >= unblock_time:
                    edges_to_restore.append((node1,node2,type,weight))


            for node1,node2,type,weight in edges_to_restore:
                self.add_edge(node1, node2, type, weight)
                del self.temporarily_blocked_edges[node1]
                # ver melhor se é preciso meter algum caso para self directed

        def delay_edge(self, node1, node2, delay_duration):
            if node1 in self.graph:
                for adjacent, (edge_type, weight) in enumerate(self.graph[node1]):
                    if adjacent == node2:
                        new_weight = weight*2 # duplica a distancia -> vai duplicar o tempo a percorrer
                        self.graph[node1].remove((node2, (edge_type, weight)))
                        self.graph[node1].append((node2, (edge_type, new_weight)))
                        unblock_time = time.time() + (delay_duration * 3600)
                        self.delayed_edges[node1] = (node2, (edge_type, weight, unblock_time))

                        if not self.directed:
                            self.graph[node2].remove((node1, (edge_type, weight)))
                            self.graph[node2].append((node1, (edge_type, new_weight)))
                            self.delayed_edges[node2] = (node1, (edge_type, weight, unblock_time))
                        break

        def reenable_delayed_edges(self):
            current_time = time.time()
            edges_to_restore = []

            for node1, (node2, (edge_type, original_weight, unblock_time)) in self.delayed_edges.items():
                if current_time >= unblock_time:
                    edges_to_restore.append((node1, node2, edge_type, original_weight))

            for node1, node2, edge_type, original_weight in edges_to_restore:
                # Find and restore the original weight
                for adjacent, (edge_type, weight) in self.graph[node1]:
                    if adjacent == node2:
                        self.graph[node1].remove(adjacent, (edge_type, weight))
                        self.graph[node1].append((adjacent, (edge_type, original_weight)))
                        del self.delayed_edges[node1]

                        if not self.directed:
                            self.graph[node2].remove(node1, (edge_type, weight))
                            self.graph[node2].append((node1, (edge_type, original_weight)))
                            del self.delayed_edges[node2]
                        break

    # ver se faz sentido as alterações do clima alterarem a distancia(de forma a demorar mais)
    # ou se faz mais sentido alterarem a velocidade média dos veículos

    # Algoritmos de procura

    def procura_DFS(self, start, end, path=[], visited=set()):
        path.append(start)
        visited.add(start)

        if start == end:
            custoT = self.calculate_cost(path)
            return (path, custoT)
        for (adjacent, peso) in self.graph[start]:
            if adjacent not in visited:
                result = self.procura_DFS(adjacent, end, path, visited)
                if result is not None:
                    return result
        path.pop()
        return None

    def procura_BFS(self, start, end):

        visited = set()
        fila = Queue()

        fila.put(start)
        visited.add(start)

        parent = dict()
        parent[start] = None

        path_found = False

        while not fila.empty() and path_found == False:
            node_atual = fila.get()
            if node_atual == end:
                path_found = True
            else:
                for (adjacent, peso) in self.graph[node_atual]:
                    if adjacent not in visited:
                        fila.put(adjacent)
                        parent[adjacent] = node_atual
                        visited.add(adjacent)
        path = []
        if path_found:
            path.append(end)
            while parent[end] is not None:
                path.append(parent[end])
                parent = parent[end]
                end = parent[end]

            path.reverse()
            cost = self.calculate_cost(path)

        return (path, cost)

    def procura_Greedy(self, start, end):
        open_list = set([start])  # lista de nodos visitados, mas com vizinhos que ainda não foram visitados
        closed_list = set([])  # lista de nodos visitados
        parents = {}  # dicionário que mantem o antecessor de um nodo
        parents[start] = start
        while len(open_list) > 0:
            n = None
            # encontra nodo com a menor heuristica
            for v in open_list:
                if n is None or self.heuristics[v] < self.heuristics[n]:
                    n = v
            if n is None:
                print('Path does not exist!')
                return None
            if n == end:
                recons_path = []
                while parents[n] != n:
                    recons_path.append(n)
                    n = parents[n]
                recons_path.append(start)
                recons_path.reverse()
                return (recons_path, self.calculate_cost(recons_path))
            for (m, weight) in self.getNeighbours(n):
                if m not in open_list and m not in closed_list:
                    open_list.add(m)
                    parents[m] = n
            open_list.remove(n)
            closed_list.add(n)
        print('Path does not exist!')
        return None

    def procura_aStar(self, start, end):
        # open_list is a list of nodes which have been visited, but who's neighbors
        # haven't all been inspected, starts off with the start node
        # closed_list is a list of nodes which have been visited
        # and who's neighbors have been inspected
        open_list = {start}
        closed_list = set([])

        # g contains current distances from start_node to all other nodes
        # the default value (if it's not found in the map) is +infinity
        g = {}

        g[start] = 0

        # parents contains an adjacency map of all nodes
        parents = {}
        parents[start] = start
        # n = None
        while len(open_list) > 0:
            # find a node with the lowest value of f() - evaluation function
            n = None
            # find a node with the lowest value of f() - evaluation function
            for v in open_list:
                if n is None or g[v] + self.get_heuristic(v) < g[n] + self.get_heuristic(n):
                    n = v
            if n is None:
                print('Path does not exist!')
                return None
            # if the current node is the stop_node
            # then we begin reconstructin the path from it to the start_node
            if n == end:
                reconst_path = []

                while parents[n] != n:
                    reconst_path.append(n)
                    n = parents[n]

                reconst_path.append(start)
                reconst_path.reverse()

                return (reconst_path, self.calculate_cost(reconst_path))

            # for all neighbors of the current node do
            for (m, weight) in self.getNeighbours(n):  # definir função getneighbours  tem de ter um par nodo peso
                # if the current node isn't in both open_list and closed_list
                # add it to open_list and note n as it's parent
                if m not in open_list and m not in closed_list:
                    open_list.add(m)
                    parents[m] = n
                    g[m] = g[n] + weight
                # otherwise, check if it's quicker to first visit n, then m
                # and if it is, update parent data and g data
                # and if the node was in the closed_list, move it to open_list
                else:
                    if g[m] > g[n] + weight:
                        g[m] = g[n] + weight
                        parents[m] = n

                        if m in closed_list:
                            closed_list.remove(m)
                            open_list.add(m)
            # remove n from the open_list, and add it to closed_list
            # because all of his neighbors were inspected
            open_list.remove(n)
            closed_list.add(n)

        print('Path does not exist!')
        return None









