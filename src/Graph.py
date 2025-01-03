import math
import os
import json
from queue import Queue
from enum import Enum
import networkx as nx
import Vehicle
from matplotlib import pyplot as plt
from Node import Node

class TerrainType(Enum):
    ROAD = 0
    NARROW_ROAD = 1
    WATER = 2

class CONDITIONS(Enum):
    RAIN = 0.10
    STRONG_RAIN = 0.18
    SNOW = 0.30
    BLOCKED = 1

class Graph:
    def __init__(self, directed=False):
        self.nodes = []
        self.directed = directed
        self.graph = {}
        self.heuristics = {}

    def get_node_by_id(self, id):

        for node in self.nodes:
            if node.getId() == id:
                return node

        return None

    def print_edge(self):
        listA = ""
        list = self.graph.keys()
        for node in list:
            for (node2, (node, type, weight, conditions)) in self.graph[node]:
                listA = listA + node + " ->" + node2 + " weight:" + str(weight) + "\n"
        return listA

    def add_edge(self, n1, n2, type, weight):
        self.graph[n1].append((n2, type, weight, None))

        if not self.directed:
            self.graph[n2].append((n1, type, weight, None))

    def get_nodes(self):
        return self.nodes

    def get_arc_cost(self, node1, node2):
        costT = math.inf
        a = self.graph[node1]  # lista de arestas para aquele nodo
        for (node, type, weight, conditions) in a:
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
        if any(n.id == node for n in self.nodes):
            self.heuristics[node] = estima

    def heuristic(self):
        nodes = self.graph.keys()
        for n in nodes:
            self.heuristics[n] = 1  # define a heuristica para cada nodo como 1
        return True  # A atribuição de heuristica foi concluida com sucesso

    def get_heuristic(self, node):
        return self.heuristics[node]

    def getNeighbours(self, node, vehicle):
        list = []
        for (adjacent, type, weight, conditions) in self.graph[node]:
            if self.edgeisCompatible(node, adjacent, vehicle):
                list.append((adjacent, type, weight, conditions))
        return list

    def draw(self):
        list_v = self.nodes
        g = nx.Graph()

        for node in list_v:
            n = node.getId()
            g.add_node(n)
            for (adjacent, type, weight, conditions) in self.graph[n]:
                lista = (n, adjacent)
                # lista_a.append(lista)
                g.add_edge(n, adjacent, weight=weight)

        pos = nx.spring_layout(g)
        nx.draw_networkx(g, pos, with_labels=True, font_weight='bold')
        labels = nx.get_edge_attributes(g, 'weight')
        nx.draw_networkx_edge_labels(g, pos, edge_labels=labels)
        plt.draw()
        plt.show()


    def loadGraph(self):
        filepath = os.path.join(os.path.dirname(__file__), '..', 'data', 'mapa.json')

        with open(filepath, 'r') as file:
            loaded_data = json.load(file)

        for node in loaded_data["nodes"]:
            id = node.get("id")
            population = node.get("population")
            severity = node.get("severity")
            timeLimit = node.get("timeLimit")
            needs = node.get("needs")
            newNode = Node(id, population, severity, timeLimit, needs)
            self.nodes.append(newNode)
            self.graph[id] = []

        for edge in loaded_data["edges"]:
            source = edge["source"]
            target = edge["target"]
            distance = edge["distance"]
            if edge["type"] == "road":
                type = TerrainType.ROAD
            elif edge["type"] == "narrowroad":
                type = TerrainType.NARROW_ROAD
            else:
                type = TerrainType.WATER
            self.add_edge(source, target, type, distance)

        for heuristic in loaded_data["heuristics"]:
            node = heuristic["node"]
            heuristic_value = heuristic["value"]
            self.add_heuristic(node, heuristic_value)


    def get_route(self, start, end, vehicle, algorithm):
        if algorithm == "DFS":
            return self.procura_DFS(start, end, vehicle)
        if algorithm == "BFS":
            return self.procura_BFS(start, end, vehicle)
        if algorithm == "Greedy":
            return self.procura_Greedy(start, end, vehicle)
        if algorithm == "A*":
            return self.procura_aStar(start, end, vehicle)
    
    def actual_speed(self, start, end, speed):
        actual_speed = speed
        a = self.graph[start]
        for (node, type, weight, condition) in a:
            if node == end and condition is not None:
                    actual_speed -= actual_speed * condition.value
                    
        return actual_speed

    def travel_time(self, path, speed):
        time = 0
        i = 0
        while i + 1 < len(path):
            actual_speed = self.actual_speed(path[i], path[i + 1], speed)
            time = time + self.get_arc_cost(path[i], path[i + 1]) / actual_speed
            i = i + 1
        return time
    
    def edgeisCompatible(self, start, end, vehicle):
        a = self.graph[start]
        for (node, type, weight, condition) in a:
            if node == end:
                if condition == CONDITIONS.BLOCKED:
                    return False
                if vehicle.type == Vehicle.VehicleType.TRUCK and type == TerrainType.NARROW_ROAD:
                    return False
                if type == TerrainType.WATER and (vehicle.type == Vehicle.VehicleType.CAR or vehicle.type == Vehicle.VehicleType.TRUCK):
                    return False
                if not type == TerrainType.WATER and vehicle.type == Vehicle.VehicleType.BOAT:
                    return False
        return True

    # Algoritmos de procura

    def procura_DFS(self, start, end, vehicle, path=[], visited=set()):
        path.append(start)
        visited.add(start)

        if start == end:
            custoT = self.calculate_cost(path)
            return (path, custoT)
        for (adjacent, type , peso, condition) in self.graph[start]:
            if adjacent not in visited and self.edgeisCompatible(start, adjacent, vehicle):
                result = self.procura_DFS(adjacent, end, vehicle, path, visited)
                if result is not None:
                    return result
        path.pop()
        return None

    def procura_BFS(self, start, end, vehicle):

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
                for (adjacent, type, peso, condition) in self.graph[node_atual]:
                    if adjacent not in visited and self.edgeisCompatible(node_atual, adjacent, vehicle):
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
        else:
            return None
        

    def procura_Greedy(self, start, end, vehicle):
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
                return None
            if n == end:
                recons_path = []
                while parents[n] != n:
                    recons_path.append(n)
                    n = parents[n]
                recons_path.append(start)
                recons_path.reverse()
                return (recons_path, self.calculate_cost(recons_path))
            for (m, type, weight, condition) in self.getNeighbours(n, vehicle):
                if m not in open_list and m not in closed_list and self.edgeisCompatible(n, m, vehicle):
                    open_list.add(m)
                    parents[m] = n
            open_list.remove(n)
            closed_list.add(n)
        return None

    def procura_aStar(self, start, end, vehicle):
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
            for (m, type, weight, condition) in self.getNeighbours(n, vehicle):  # definir função getneighbours  tem de ter um par nodo peso
                # if the current node isn't in both open_list and closed_list
                # add it to open_list and note n as it's parent
                if m not in open_list and m not in closed_list and self.edgeisCompatible(n, m, vehicle):
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

        return None