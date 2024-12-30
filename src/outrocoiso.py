import math
import networkx as nx
import matplotlib.pyplot as plt
import os
import time
from queue import Queue
from dataclasses import dataclass
from typing import List, Dict, Set, Tuple, Optional

@dataclass
class Node:
    id: str
    priority: int  # 1-10 scale
    population: int
    supplies_needed: float = 0.0
    supplies_current: float = 0.0
    terrain_type: str = "urban"  # urban, water, mountain, forest
    coordinates: Tuple[float, float] = (0.0, 0.0)

    def getId(self):
        return self.id

    def get_supply_percentage(self):
        if self.supplies_needed == 0:
            return 100.0
        return (self.supplies_current / self.supplies_needed) * 100


class Graph:
    def __init__(self, directed=False):
        self.nodes: List[Node] = []
        self.directed = directed
        # node1 -> [(node2, (type, distance))]
        self.graph: Dict[str, List[Tuple[str, Tuple[str, float]]]] = {}
        self.heuristics: Dict[str, float] = {}
        self.temporarily_blocked_edges: Dict[str, Tuple[str, Tuple[str, float, float]]] = {}
        self.delayed_edges: Dict[str, Tuple[str, Tuple[str, float, float]]] = {}

    def get_node_by_id(self, id: str) -> Optional[Node]:
        return next((node for node in self.nodes if node.getId() == id), None)

    def print_edge(self) -> str:
        return "\n".join(f"{node} -> {node2} weight:{weight}"
                         for node in self.graph.keys()
                         for node2, (type_road, weight) in self.graph[node])

    def add_edge(self, node1: Node, node2: Node, type_road: str, weight: float):
        n1 = node1.getId()
        n2 = node2.getId()

        if self.get_node_by_id(n1) is None:
            self.nodes.append(node1)
            self.graph[n1] = []

        if self.get_node_by_id(n2) is None:
            self.nodes.append(node2)
            self.graph[n2] = []

        self.graph[n1].append((n2, (type_road, weight)))

        if not self.directed:
            self.graph[n2].append((n1, (type_road, weight)))

    def get_arc_cost(self, node1: str, node2: str) -> float:
        if node1 not in self.graph:
            return math.inf

        for node, (_, weight) in self.graph[node1]:
            if node == node2:
                return weight
        return math.inf

    def calculate_cost(self, path: List[str]) -> float:
        return sum(self.get_arc_cost(path[i], path[i + 1])
                   for i in range(len(path) - 1))

    def add_heuristic(self, node: str, estimate: float):
        self.heuristics[node] = estimate

    def get_heuristic(self, node: str) -> float:
        return self.heuristics.get(node, 1.0)

    def getNeighbours(self, node: str) -> List[Tuple[str, float]]:
        if node not in self.graph:
            return []
        return [(adj, weight) for adj, (_, weight) in self.graph[node]]

    def draw(self):
        g = nx.Graph()

        # Add nodes with attributes
        for node in self.nodes:
            g.add_node(node.getId(),
                       priority=node.priority,
                       population=node.population,
                       supplies_needed=node.supplies_needed,
                       supplies_current=node.supplies_current,
                       pos=node.coordinates)

        # Add edges with attributes
        for n1 in self.graph:
            for n2, (road_type, weight) in self.graph[n1]:
                g.add_edge(n1, n2, weight=weight, road_type=road_type)

        # Get node positions
        pos = nx.get_node_attributes(g, 'pos')
        if not pos:
            pos = nx.spring_layout(g)

        # Draw nodes with colors based on priority
        priorities = nx.get_node_attributes(g, 'priority')
        node_colors = [plt.cm.RdYlGn_r(float(priorities[node]) / 10) for node in g.nodes()]

        # Draw the graph
        plt.figure(figsize=(12, 8))

        # Draw edges with different colors based on road type
        edge_colors = {'road': 'gray', 'water': 'blue', 'air': 'lightblue'}
        for road_type, color in edge_colors.items():
            edge_list = [(u, v) for (u, v, d) in g.edges(data=True)
                         if d['road_type'] == road_type]
            nx.draw_networkx_edges(g, pos, edgelist=edge_list, edge_color=color)

        # Draw nodes
        nx.draw_networkx_nodes(g, pos, node_color=node_colors,
                               node_size=[n * 100 for n in priorities.values()])

        # Add labels
        nx.draw_networkx_labels(g, pos)
        edge_labels = nx.get_edge_attributes(g, 'weight')
        nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels)

        # Add legend
        legend_elements = [plt.Line2D([0], [0], color=color, label=road_type)
                           for road_type, color in edge_colors.items()]
        plt.legend(handles=legend_elements)

        plt.title("Disaster Relief Distribution Network")
        plt.axis('off')
        plt.show()

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


# Create example disaster relief scenario
def create_disaster_scenario():
    graph = Graph(directed=False)

    # Create nodes representing different affected areas
    nodes = [
        Node("Base", 1, 0, coordinates=(0, 0), terrain_type="urban"),
        Node("City1", 8, 5000, supplies_needed=1000, coordinates=(2, 3), terrain_type="urban"),
        Node("Village1", 7, 2000, supplies_needed=500, coordinates=(4, 1), terrain_type="forest"),
        Node("Coast1", 9, 3000, supplies_needed=800, coordinates=(1, 5), terrain_type="water"),
        Node("Mountain1", 6, 1000, supplies_needed=300, coordinates=(5, 4), terrain_type="mountain"),
        Node("City2", 9, 8000, supplies_needed=1500, coordinates=(3, 6), terrain_type="urban")
    ]

    # Add edges representing different types of connections
    connections = [
        (nodes[0], nodes[1], "road", 10),  # Base to City1
        (nodes[0], nodes[2], "road", 15),  # Base to Village1
        (nodes[1], nodes[3], "water", 20),  # City1 to Coast1
        (nodes[1], nodes[4], "air", 25),  # City1 to Mountain1
        (nodes[2], nodes[4], "road", 18),  # Village1 to Mountain1
        (nodes[3], nodes[5], "water", 12),  # Coast1 to City2
        (nodes[4], nodes[5], "air", 22),  # Mountain1 to City2
    ]

    # Add nodes and connections to graph
    for node in nodes:
        if graph.get_node_by_id(node.getId()) is None:
            graph.nodes.append(node)
            graph.graph[node.getId()] = []

    for n1, n2, type_road, weight in connections:
        graph.add_edge(n1, n2, type_road, weight)

    # Add heuristics based on straight-line distance to City2 (example destination)
    target = nodes[5].coordinates
    for node in nodes:
        dx = node.coordinates[0] - target[0]
        dy = node.coordinates[1] - target[1]
        distance = math.sqrt(dx * dx + dy * dy)
        graph.add_heuristic(node.getId(), distance)

    return graph

if __name__ == "__main__":
    # Create and visualize the disaster relief scenario
    relief_graph = create_disaster_scenario()
    relief_graph.draw()

    # Example: Find path from Base to City2 using A*
    path = relief_graph.procura_aStar("Base", "City2")
    if path:
        print(f"Path found: {' -> '.join(path[0])}")
        print(f"Total cost: {path[1]}")