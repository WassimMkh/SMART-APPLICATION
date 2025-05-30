import networkx as nx
import random
import string
from itertools import combinations

def dijkstra(n, source):
    G = nx.Graph()
    nodes = list(string.ascii_uppercase[:n])

    if source not in nodes:
        return "Source invalide.", None, None

    G.add_nodes_from(nodes)

    # Générer des arêtes aléatoires
    possible_edges = list(combinations(nodes, 2))
    total_edges = random.randint(n, min(len(possible_edges), n * 2))
    selected_edges = random.sample(possible_edges, total_edges)

    for u, v in selected_edges:
        weight = random.randint(1, 20)
        G.add_edge(u, v, weight=weight)

    # Algorithme Dijkstra
    dist = {node: float('inf') for node in nodes}
    prev = {node: None for node in nodes}
    dist[source] = 0
    unvisited = set(nodes)

    while unvisited:
        u = min(unvisited, key=lambda node: dist[node])
        unvisited.remove(u)

        for v in G.neighbors(u):
            weight = G[u][v]['weight']
            if dist[u] + weight < dist[v]:
                dist[v] = dist[u] + weight
                prev[v] = u

    # Construction des chemins
    chemins = {}
    for node in nodes:
        if node == source or dist[node] == float('inf'):
            continue
        path = []
        current = node
        while current and prev[current] is not None:
            path.insert(0, (prev[current], current))
            current = prev[current]
        if path:
            chemins[node] = path

    return dist, chemins, G