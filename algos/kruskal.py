import networkx as nx
import random
import string

def kruskal(n):
    G = nx.Graph()

    if n > 26:
        raise ValueError("Ce code ne supporte que jusqu'à 26 sommets (A-Z).")
    nodes = list(string.ascii_uppercase[:n])
    G.add_nodes_from(nodes)

    # Générer des arêtes avec poids
    all_possible_edges = [(nodes[i], nodes[j]) for i in range(n) for j in range(i + 1, n)]
    max_edges = random.randint(n, n * (n - 1) // 2)
    selected_edges = random.sample(all_possible_edges, max_edges)

    for u, v in selected_edges:
        G.add_edge(u, v, weight=random.randint(1, 20))

    # S'assurer que le graphe est connexe
    if not nx.is_connected(G):
        base_tree = nx.minimum_spanning_tree(nx.complete_graph(n))
        for u, v in base_tree.edges():
            a, b = nodes[u], nodes[v]
            if not G.has_edge(a, b):
                G.add_edge(a, b, weight=random.randint(1, 20))

    # Calculer l'arbre couvrant minimal
    mst = nx.minimum_spanning_tree(G)
    total_weight = sum(d['weight'] for _, _, d in mst.edges(data=True))
    
    return total_weight, mst, G