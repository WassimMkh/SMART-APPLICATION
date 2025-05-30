import networkx as nx
import matplotlib.pyplot as plt
import random

def int_to_label(i):
    label = ''
    while True:
        i, r = divmod(i, 26)
        label = chr(65 + r) + label
        if i == 0:
            break
        i -= 1
    return label

def generate_labels(n):
    return [int_to_label(i) for i in range(n)]

def generate_random_graph(labels):
    G = nx.DiGraph()
    num_nodes = len(labels)
    for i, u in enumerate(labels):
        num_edges = random.randint(1, num_nodes - 1)
        neighbors = random.sample([v for v in labels if v != u], num_edges)
        for v in neighbors:
            if not G.has_edge(u, v):
                capacity = random.randint(5, 20)
                G.add_edge(u, v, capacity=capacity)
    return G

def bfs(rGraph, s, parent):
    visited = [False] * len(rGraph)
    queue = [s]
    visited[s] = True

    while queue:
        u = queue.pop(0)
        for v, cap in enumerate(rGraph[u]):
            if not visited[v] and cap > 0:
                queue.append(v)
                visited[v] = True
                parent[v] = u
    return visited

import networkx as nx
import random

def ford_fulkerson(nb, source, sink):
    nodes = [chr(65 + i) for i in range(nb)]
    G = nx.DiGraph()
    G.add_nodes_from(nodes)

    edges_added = set()  # Pour éviter arêtes en double ou inverses
    for u in nodes:
        possible_targets = [n for n in nodes if n != u and (n, u) not in edges_added]
        nb_arcs = random.randint(1, max(1, min(3, len(possible_targets))))
        targets = random.sample(possible_targets, nb_arcs)
        for v in targets:
            if (u, v) in edges_added or (v, u) in edges_added or u == v:
                continue
            capacity = random.randint(1, 20)
            G.add_edge(u, v, capacity=capacity)
            edges_added.add((u, v))

    if source not in nodes or sink not in nodes:
        raise ValueError("Source ou puits invalide")

    flow_value, flow_dict = nx.maximum_flow(G, source, sink, flow_func=nx.algorithms.flow.edmonds_karp)

    cut_value, (reachable, non_reachable) = nx.minimum_cut(G, source, sink)
    cutset = set()
    for u in reachable:
        for v in G.successors(u):
            if v in non_reachable:
                cutset.add((u, v))

    return flow_value, cutset, G