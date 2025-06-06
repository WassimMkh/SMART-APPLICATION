# algos/kruskal.py
import networkx as nx
import random
import string
from itertools import combinations, product as iterprod # Utiliser product renommé

# Utiliser la version robuste de generer_noms_alphabétiques
def generer_noms_alphabétiques_robuste(n):
    noms = []
    alphabet = string.ascii_uppercase
    num_chars = 1
    while len(noms) < n:
        for p in iterprod(alphabet, repeat=num_chars): # Utiliser iterprod
            if len(noms) < n:
                noms.append("".join(p))
            else:
                break
        if len(noms) >= n:
            break
        num_chars += 1
    return noms

def kruskal(n):
    if n <= 0:
        # total_weight, mst, G, densite_reelle_pourcentage
        return 0, nx.Graph(), nx.Graph(), 0.0 

    G = nx.Graph() # Kruskal fonctionne sur des graphes non orientés
    nodes = generer_noms_alphabétiques_robuste(n)
    G.add_nodes_from(nodes)

    if n == 1: # Cas d'un seul nœud
        return 0, nx.Graph(), G, 0.0 # Pas d'arêtes, donc 0% de densité d'arêtes

    # Facteur de densité cible pour la génération
    densite_cible_factor = random.uniform(0.05, 1.0) # Viser au moins une petite densité si n > 1
    
    all_possible_edges_list = list(combinations(nodes, 2))
    max_possible_edges_count = len(all_possible_edges_list)

    edges_added_count = 0 # Pour compter les arêtes effectivement ajoutées

    # --- MODIFICATION ICI pour N=2 et N>2 ---
    if n == 2:
        # Cas spécial pour N=2: une seule arête possible.
        # Probabilité d'avoir cette arête = densite_cible_factor.
        if max_possible_edges_count == 1: # Devrait toujours être vrai pour N=2
            if random.random() < densite_cible_factor:
                u, v = all_possible_edges_list[0] # Prendre l'unique paire possible
                poids = random.randint(1, 200)
                G.add_edge(u, v, weight=poids)
                edges_added_count = 1
        # else: edges_added_count restera 0
    elif n > 2:
        num_edges_to_generate = 0
        if max_possible_edges_count > 0:
            num_edges_to_generate_float = densite_cible_factor * max_possible_edges_count
            num_edges_to_generate = round(num_edges_to_generate_float)
            if num_edges_to_generate == 0 and num_edges_to_generate_float > 0.01: # Au moins une
                num_edges_to_generate = 1
            num_edges_to_generate = min(int(num_edges_to_generate), max_possible_edges_count)

        if num_edges_to_generate > 0 : # S'assurer qu'on a des arêtes à échantillonner
            selected_edges_tuples = random.sample(all_possible_edges_list, num_edges_to_generate)
            for u, v in selected_edges_tuples:
                poids = random.randint(1, 200)
                G.add_edge(u, v, weight=poids)
            edges_added_count = G.number_of_edges() # ou num_edges_to_generate
    # --- FIN MODIFICATION ---
    
    # Calcul de l'arbre couvrant minimal
    mst = nx.Graph() 
    total_weight = 0
    # Kruskal peut être appliqué à un graphe non connexe; il produit une forêt couvrante minimale.
    # nx.minimum_spanning_tree retournera un arbre si connexe, ou lèvera une exception si pas d'option pour `algorithm='kruskal'` 
    # si on veut juste les arêtes, nx.minimum_spanning_edges est plus direct.
    try:
        if G.number_of_edges() > 0 : # Un MST n'a de sens que s'il y a des arêtes
            # Pour un graphe potentiellement non connexe, on trouve une forêt couvrante.
            # Si on veut un seul arbre, on vérifie d'abord la connexité.
            if nx.is_connected(G):
                mst_edges = list(nx.minimum_spanning_edges(G, algorithm='kruskal', data=True))
                if mst_edges:
                    mst.add_nodes_from(G.nodes()) # S'assurer que tous les noeuds originaux sont dans mst même s'ils sont isolés dans l'MST final (forêt)
                    mst.add_edges_from(mst_edges)
                    total_weight = sum(d['weight'] for _, _, d in mst.edges(data=True))
            # else: Le graphe n'est pas connexe. mst reste vide et total_weight=0 comme initialisé.
            # On pourrait aussi choisir de calculer une forêt couvrante minimale:
            # else:
            #     forest_edges = list(nx.minimum_spanning_edges(G, algorithm='kruskal', data=True))
            #     if forest_edges:
            #         mst.add_nodes_from(G.nodes())
            #         mst.add_edges_from(forest_edges) # mst serait alors une forêt
            #         total_weight = sum(d['weight'] for _, _, d in mst.edges(data=True))
    except Exception as e_kruskal_mst:
        print(f"Erreur Kruskal MST: {e_kruskal_mst}")
        # mst et total_weight restent à leurs valeurs initiales (vide/0)


    # --- Calcul de la DENSITÉ RÉELLE du graphe G généré ---
    densite_reelle_pourcentage = 0.0
    if max_possible_edges_count > 0: 
        densite_reelle_pourcentage = (edges_added_count / max_possible_edges_count)
    # Pour n=1, max_possible_edges_count est 0, donc densite_reelle_pourcentage reste 0.0.
    
    densite_reelle_pourcentage = max(0.0, min(densite_reelle_pourcentage, 100.0))

    return total_weight, mst, G, densite_reelle_pourcentage