import random
import string
import networkx as nx
import matplotlib.pyplot as plt

def genererGraph(nbrSommets):
    noeuds = list(string.ascii_uppercase + string.ascii_lowercase)[:nbrSommets]
    graph = {n: [] for n in noeuds}
    added_edges = set()
    
    for noeud in noeuds:
        k = random.randint(1, len(noeuds) - 1)
        voisins_possibles = [n for n in noeuds if n != noeud and (n, noeud) not in added_edges and (noeud, n) not in added_edges]
        aretes = random.sample(voisins_possibles, k=min(k, len(voisins_possibles)))
        
        for arete in aretes:
            ponderation = random.randint(1, 10)
            graph[noeud].append((arete, ponderation))
            graph[arete].append((noeud, ponderation))
            added_edges.add((noeud, arete))
    
    return graph

def welsh(nbrSommet):
    graph = genererGraph(nbrSommet)
    degres = dict(sorted({n: len(d) for n, d in graph.items()}.items(), key=lambda item: item[1], reverse=True))
    couleurs = ["red", "blue", "yellow", "green", "orange", "purple", "cyan", "magenta", "lime", "gray"]

    graph_couleur = {}
    for noeud in degres:
        noeudAdjCoul = [graph_couleur[n[0]] for n in graph[noeud] if n[0] in graph_couleur]
        for couleur in couleurs:
            if couleur not in noeudAdjCoul:
                graph_couleur[noeud] = couleur
                break

    return graph, graph_couleur
