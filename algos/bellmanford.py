import random
import string
import networkx as nx

def bellman_ford_graph(nb, source):
    # Construction aléatoire du graphe
    nodes = [chr(65 + i) for i in range(nb)]
    if source not in nodes:
        return f"Erreur: Le nœud source {source} n'existe pas.", {}, None

    G = nx.DiGraph()
    G.add_nodes_from(nodes)

    # Générer des arêtes aléatoires
    for _ in range(nb * 2):
        u, v = random.sample(nodes, 2)
        weight = random.randint(-5, 15)
        G.add_edge(u, v, weight=weight)

    # Algorithme Bellman-Ford
    try:
        lengths = nx.single_source_bellman_ford_path_length(G, source)
        result_text = f"Distances depuis {source} :\n"
        for node in nodes:
            d = lengths.get(node, float('inf'))
            result_text += f"{node} : {d if d != float('inf') else 'inf'}\n"
        
        return result_text, lengths, G
        
    except nx.NetworkXUnbounded:
        return "Cycle négatif détecté !", {}, G