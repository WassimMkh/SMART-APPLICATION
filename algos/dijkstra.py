# algos/dijkstra.py
import networkx as nx
import random
import string
from itertools import combinations, product as iterprod

def generer_noms_alphabétiques_robuste(n): # S'assurer d'utiliser la version robuste
    noms = []
    alphabet = string.ascii_uppercase
    num_chars = 1
    while len(noms) < n:
        for p in iterprod(alphabet, repeat=num_chars):
            if len(noms) < n: noms.append("".join(p))
            else: break
        if len(noms) >= n: break
        num_chars += 1
    return noms

def dijkstra(n, source_node_name, target_node_name_optional):
    if n <= 0:
        return {}, {}, nx.Graph(), 0.0, [], "Erreur: Nombre de nœuds doit être > 0."

    nodes = generer_noms_alphabétiques_robuste(n)

    if source_node_name not in nodes:
        return {}, {}, nx.Graph(), 0.0, [], f"Erreur: Nœud source '{source_node_name}' invalide."
    
    target_is_valid_node = False
    if target_node_name_optional:
        if target_node_name_optional not in nodes:
            return {}, {}, nx.Graph(), 0.0, [], f"Erreur: Nœud cible '{target_node_name_optional}' invalide."
        target_is_valid_node = True
    
    if target_is_valid_node and source_node_name == target_node_name_optional:
        G_trivial = nx.Graph(); G_trivial.add_node(source_node_name)
        dist_trivial = {node: float('inf') for node in nodes}; dist_trivial[source_node_name] = 0
        texte_trivial = f"Distances depuis {source_node_name}:\n - {source_node_name} : 0\n\n"
        texte_trivial += f"✅ Déjà à la destination {target_node_name_optional}. Distance 0."
        return dist_trivial, {}, G_trivial, 0.0, [], texte_trivial

    G = nx.Graph()
    G.add_nodes_from(nodes)

    if n == 1:
        dist_single = {nodes[0]: (0 if nodes[0] == source_node_name else float('inf'))}
        texte_single = f"Distances depuis {source_node_name}:\n - {nodes[0]} : {dist_single[nodes[0]]}\n"
        # ... (logique pour message target comme avant)
        return dist_single, {}, G, 0.0, [], texte_single

    densite_cible_factor = random.uniform(0.05, 1.0)
    possible_edges_list = list(combinations(nodes, 2))
    max_possible_edges_count = len(possible_edges_list)
    
    edges_added_count = 0 # Pour compter les arêtes effectivement ajoutées

    # --- MODIFICATION ICI pour N=2 et N>2 ---
    if n == 2:
        # Cas spécial pour N=2: une seule arête possible.
        # Probabilité d'avoir cette arête = densite_cible_factor.
        if max_possible_edges_count == 1: # Devrait toujours être vrai pour N=2
            if random.random() < densite_cible_factor:
                u, v = possible_edges_list[0] # Prendre l'unique paire possible
                weight = random.randint(1, 200)
                G.add_edge(u, v, weight=weight)
                edges_added_count = 1
        # else: edges_added_count restera 0
    elif n > 2:
        num_edges_to_generate = 0
        if max_possible_edges_count > 0:
            num_edges_to_generate_float = densite_cible_factor * max_possible_edges_count
            num_edges_to_generate = round(num_edges_to_generate_float)
            if num_edges_to_generate == 0 and num_edges_to_generate_float > 0.01:
                num_edges_to_generate = 1 # Assurer au moins une arête si petite chance
            num_edges_to_generate = min(int(num_edges_to_generate), max_possible_edges_count)

        if num_edges_to_generate > 0:
            selected_edges_tuples = random.sample(possible_edges_list, num_edges_to_generate)
            for u, v in selected_edges_tuples:
                weight = random.randint(1, 200)
                G.add_edge(u, v, weight=weight)
            edges_added_count = G.number_of_edges() # Ou num_edges_to_generate si sample a réussi
    # --- FIN MODIFICATION ---

    # Calcul de la DENSITÉ RÉELLE du graphe G généré
    densite_reelle_pourcentage = 0.0
    if max_possible_edges_count > 0: # Pour éviter division par zéro
        densite_reelle_pourcentage = (edges_added_count / max_possible_edges_count) * 100.0
    
    densite_reelle_pourcentage = max(0.0, min(densite_reelle_pourcentage, 100.0))

    # Dijkstra avec NetworkX 
    all_shortest_paths_lengths = {}
    all_shortest_paths_nodes = {}
    try:
        for target_n_sp in G.nodes():
            if target_n_sp == source_node_name:
                all_shortest_paths_lengths[source_node_name] = 0
                all_shortest_paths_nodes[source_node_name] = [] # Pas d'arêtes pour un chemin vers soi-même de longueur 0
            else:
                try:
                    length, path_nodes_list = nx.bidirectional_dijkstra(G, source_node_name, target_n_sp, weight='weight')
                    all_shortest_paths_lengths[target_n_sp] = length
                    path_edges_list = []
                    if len(path_nodes_list) > 1:
                        for i_path in range(len(path_nodes_list) - 1):
                            path_edges_list.append((path_nodes_list[i_path], path_nodes_list[i_path+1]))
                    all_shortest_paths_nodes[target_n_sp] = path_edges_list
                except nx.NetworkXNoPath:
                    all_shortest_paths_lengths[target_n_sp] = float('inf')
                    all_shortest_paths_nodes[target_n_sp] = []
    except Exception as e_dijkstra_nx:
        # ... (gestion d'erreur comme avant)
        import traceback
        print(f"Erreur Dijkstra (NetworkX): {e_dijkstra_nx}")
        traceback.print_exc()
        return {}, {}, G, densite_reelle_pourcentage, [], f"Erreur lors de l'exécution de Dijkstra: {e_dijkstra_nx}"

    # Texte descriptif
    texte_resultat_final = f"Distances depuis {source_node_name} (Dijkstra):\n"
    # ... (logique d'affichage comme avant) ...
    for node_disp in sorted(G.nodes()):
        d_disp = all_shortest_paths_lengths.get(node_disp, float('inf'))
        if d_disp == float('inf'):
            texte_resultat_final += f" - {node_disp} : ∞ (non accessible)\n"
        else:
            texte_resultat_final += f" - {node_disp} : {d_disp}\n"

    chemin_source_target_final = []
    if target_is_valid_node: 
        dist_to_target = all_shortest_paths_lengths.get(target_node_name_optional, float('inf'))
        if dist_to_target != float('inf'):
            texte_resultat_final += f"\n✅ Distance de {source_node_name} à {target_node_name_optional} : {dist_to_target}"
            chemin_source_target_final = all_shortest_paths_nodes.get(target_node_name_optional, [])
        else:
            texte_resultat_final += f"\n❌ Aucun chemin de {source_node_name} à {target_node_name_optional}."
            
    return all_shortest_paths_lengths, all_shortest_paths_nodes, G, densite_reelle_pourcentage, chemin_source_target_final, texte_resultat_final