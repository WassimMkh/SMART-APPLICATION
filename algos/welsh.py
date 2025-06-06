import random
import string
import networkx as nx
import matplotlib.pyplot as plt

# Génère des noms alphabétiques : A, B, ..., Z, AA, AB, ...
from itertools import combinations, product as iterprod # iterprod pour la génération robuste des noms


# Utiliser la version robuste de generer_noms_alphabétiques
def generer_noms_alphabétiques_robuste(n):
    noms = []
    alphabet = string.ascii_uppercase
    num_chars = 1
    while len(noms) < n:
        for p in iterprod(alphabet, repeat=num_chars):
            if len(noms) < n:
                noms.append("".join(p))
            else:
                break
        if len(noms) >= n:
            break
        num_chars += 1
    return noms

# Génère un graphe non entièrement connexe avec une densité aléatoire
# Cette fonction retourne maintenant aussi le nombre d'arêtes ajoutées et le max possible.
def genererGraph(nbrSommets):
    if nbrSommets <= 0:
        return {}, 0, 0 # graphe vide, 0 arêtes, 0 max possible
    
    # Utiliser la version robuste pour générer les noms
    noeuds = generer_noms_alphabétiques_robuste(nbrSommets)
    # La structure de `graph` est un dictionnaire de listes (liste d'adjacence)
    graph_adj_list = {n: [] for n in noeuds}
    
    if nbrSommets == 1:
        return graph_adj_list, 0, 0 # 0 arêtes ajoutées, 0 max possible pour 1 nœud

    densite_cible_factor = random.uniform(0.05, 1.0) # Viser au moins une petite densité

    toutes_aretes_possibles_list = list(combinations(noeuds, 2))
    max_aretes_possibles_count = len(toutes_aretes_possibles_list)

    nb_aretes_a_generer = 0
    aretes_ajoutees_count = 0

    if nbrSommets == 2:
        # Cas spécial pour N=2
        if max_aretes_possibles_count == 1: # Toujours vrai
            if random.random() < densite_cible_factor:
                nb_aretes_a_generer = 1
            # else: nb_aretes_a_generer reste 0
    elif nbrSommets > 2:
        if max_aretes_possibles_count > 0:
            nb_aretes_a_generer_float = densite_cible_factor * max_aretes_possibles_count
            nb_aretes_a_generer = round(nb_aretes_a_generer_float)
            if nb_aretes_a_generer == 0 and nb_aretes_a_generer_float > 0.01:
                nb_aretes_a_generer = 1
            nb_aretes_a_generer = min(int(nb_aretes_a_generer), max_aretes_possibles_count)
    
    if nb_aretes_a_generer > 0 and max_aretes_possibles_count > 0:
        aretes_choisies_tuples = random.sample(toutes_aretes_possibles_list, nb_aretes_a_generer)
        for u, v in aretes_choisies_tuples:
            poids = random.randint(1, 200) # Welsh n'utilise pas les poids, mais bon pour la cohérence
            graph_adj_list[u].append((v, poids))
            graph_adj_list[v].append((u, poids))
        aretes_ajoutees_count = nb_aretes_a_generer # ou len(aretes_choisies_tuples)

    return graph_adj_list, aretes_ajoutees_count, max_aretes_possibles_count

# Applique l'algorithme Welsh-Powell
def welsh(nbrSommet):
    if nbrSommet <= 0:
        # graph_adj, graph_couleur, densite_reelle_ratio (0-1)
        return {}, {}, 0.0

    # Générer le graphe
    # genererGraph retourne maintenant: graph_adj_list, edges_added_count, max_possible_edges_count
    graph_adj, edges_added, max_edges_possible = genererGraph(nbrSommet)

    # Calcul de la densité réelle (ratio 0-1)
    densite_reelle_ratio = 0.0
    if max_edges_possible > 0:
        densite_reelle_ratio = edges_added / max_edges_possible
    elif nbrSommet == 1: # 1 noeud, 0 arêtes possibles
        densite_reelle_ratio = 0.0 # Pas d'arêtes, donc 0% de densité
    
    densite_reelle_ratio = max(0.0, min(densite_reelle_ratio, 1.0)) # Borner entre 0 et 1

    # Welsh-Powell pour la coloration
    # Tri des nœuds par degré décroissant
    # Votre `graph_adj` est une liste d'adjacence. `degres` doit être calculé à partir de ça.
    degres_dict = {n: len(adj_nodes) for n, adj_nodes in graph_adj.items()}
    noeuds_tries_par_degre = sorted(degres_dict, key=degres_dict.get, reverse=True)

    # Couleurs disponibles (plus que le nombre de sommets au cas où)
    couleurs_base = ["red", "blue", "yellow", "green", "orange", "purple", "cyan", "magenta", "lime", "gray",
                     "pink", "brown", "olive", "teal", "navy", "maroon", "gold", "silver", "indigo", "violet"]
    # Étendre dynamiquement si plus de couleurs sont nécessaires que celles prédéfinies
    couleurs_disponibles = list(couleurs_base) 
    idx_couleur_next = 0 # Pour sélectionner la prochaine couleur de base
    
    while len(couleurs_disponibles) < nbrSommet + 5 : # Avoir une marge de couleurs
         # Générer des couleurs hex aléatoires uniques
         new_hex_color = "#" + ''.join(random.choices("0123456789ABCDEF", k=6))
         if new_hex_color not in couleurs_disponibles:
             couleurs_disponibles.append(new_hex_color)


    graph_couleur_resultat = {} # Dictionnaire pour stocker la couleur de chaque nœud
    
    for noeud_actuel in noeuds_tries_par_degre:
        couleurs_adjacentes_interdites = set()
        # Récupérer les couleurs des voisins déjà colorés
        # Les voisins sont stockés comme (voisin_nom, poids) dans graph_adj[noeud_actuel]
        for voisin_tuple in graph_adj[noeud_actuel]:
            voisin_nom = voisin_tuple[0] 
            if voisin_nom in graph_couleur_resultat:
                couleurs_adjacentes_interdites.add(graph_couleur_resultat[voisin_nom])
        
        # Trouver la première couleur disponible non utilisée par les voisins
        couleur_assignee = None
        for c in couleurs_disponibles: # Itérer sur la liste des couleurs possibles
            if c not in couleurs_adjacentes_interdites:
                couleur_assignee = c
                break
        
        if couleur_assignee is not None:
            graph_couleur_resultat[noeud_actuel] = couleur_assignee
        else:
            # Cela ne devrait pas arriver si couleurs_disponibles est assez grand, 
            # mais comme fallback, assigner une couleur aléatoire non utilisée (ou une nouvelle).
            # En théorie, le nombre de couleurs ne dépassera jamais N.
            # Mais si couleurs_disponibles était mal géré :
            fallback_color = "#" + ''.join(random.choices("0123456789ABCDEF", k=6))
            while fallback_color in couleurs_adjacentes_interdites or fallback_color in graph_couleur_resultat.values():
                fallback_color = "#" + ''.join(random.choices("0123456789ABCDEF", k=6))
            graph_couleur_resultat[noeud_actuel] = fallback_color
            if fallback_color not in couleurs_disponibles: # Ajouter à la liste si nouvelle
                 couleurs_disponibles.append(fallback_color)


    # Retourner le graphe original (liste d'adjacence), les couleurs des nœuds,
    # et la DENSITÉ RÉELLE (ratio 0-1).
    return graph_adj, graph_couleur_resultat, densite_reelle_ratio

# La fonction dessiner_graphe n'est pas directement appelée par l'interface,
# mais peut être utilisée pour des tests.
def dessiner_graphe_welsh(graph_adj_list, couleurs_noeuds, densite_pourcentage):
    G_nx = nx.Graph() # Convertir la liste d'adjacence en objet Graph NetworkX

    # Ajouter tous les nœuds, même ceux sans arêtes ou isolés
    for noeud_key in graph_adj_list: # graph_adj_list est un dict {noeud: [(voisin,poids),...]}
        G_nx.add_node(noeud_key)
        for voisin_info in graph_adj_list[noeud_key]:
            voisin_nom, poids = voisin_info
            # NetworkX gère automatiquement les doublons d'arêtes dans les graphes non orientés
            G_nx.add_edge(noeud_key, voisin_nom, weight=poids)

    pos = nx.spring_layout(G_nx, seed=42)
    # Récupérer les couleurs pour chaque nœud dans l'ordre de G_nx.nodes()
    node_colors_list = [couleurs_noeuds.get(n, "grey") for n in G_nx.nodes()]

    plt.figure(figsize=(10, 8))
    nx.draw(G_nx, pos, with_labels=True, node_color=node_colors_list, edge_color="black",
            node_size=700, font_size=10, font_weight='bold', width=1.5)
    
    # Afficher les poids des arêtes si vous le souhaitez (Welsh-Powell ne les utilise pas mais genererGraph les crée)
    # edge_labels = nx.get_edge_attributes(G_nx, 'weight')
    # nx.draw_networkx_edge_labels(G_nx, pos, edge_labels=edge_labels, font_size=8)

    plt.title(f"Graphe coloré (Welsh-Powell) - Densité: {densite_pourcentage:.2f}%", fontsize=14)
    plt.tight_layout()
    plt.show()