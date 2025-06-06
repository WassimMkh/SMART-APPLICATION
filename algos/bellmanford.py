# algos/bellmanford.py
import random
import string
import networkx as nx
from itertools import product
import math # Pour math.ceil ou round

def generer_noms_alphabétiques(n):
    # ... (fonction inchangée)
    noms = []
    alphabet = string.ascii_uppercase
    num_chars = 1
    while len(noms) < n:
        for p in product(alphabet, repeat=num_chars):
            if len(noms) < n:
                noms.append("".join(p))
            else:
                break
        if len(noms) >= n:
            break
        num_chars += 1
    return noms


def bellman_ford_graph(nb_nodes, source, destination=None):
    if nb_nodes <= 0:
        return "Erreur: Le nombre de nœuds doit être positif.", {}, None, None, 0

    nodes = generer_noms_alphabétiques(nb_nodes)
    if source not in nodes:
        return f"Erreur: Le nœud source '{source}' n'est pas valide pour {nb_nodes} nœuds.", {}, None, None, 0
    if destination and destination not in nodes:
        return f"Erreur: Le nœud destination '{destination}' n'est pas valide pour {nb_nodes} nœuds.", {}, None, None, 0
    
    if destination == source: 
        G_trivial = nx.DiGraph(); G_trivial.add_node(source)
        conn_rate_trivial = 0.0 # Pas d'arêtes, donc 0% de connectivité des arêtes.
                                # Si nb_nodes == 1, on pourrait dire que c'est trivialement "connecté"
                                # mais la métrique ici semble être sur les arêtes.
        return f"Distances depuis {source}:\n{source} : 0\n\nChemin de {source} à {destination} : (aucun)\nDistance : 0", \
               {source: 0}, G_trivial, [], conn_rate_trivial

    G = nx.DiGraph()
    G.add_nodes_from(nodes)

    connectivity_density_factor = random.uniform(0, 1) # Assurer une petite densité minimale si nb_nodes > 1

    # Maximum possible d'arêtes uniques non-bidirectionnelles.
    # Pour N nœuds, chaque paire (u,v) peut avoir soit u->v, soit v->u, soit rien.
    # Il y a N*(N-1)/2 paires de nœuds. Donc au plus N*(N-1)/2 arêtes si l'on respecte la contrainte.
    max_potential_unique_links = (nb_nodes * (nb_nodes - 1)) / 2 if nb_nodes > 1 else 0
    
    # --- MODIFICATION ICI ---
    # Pour les petits graphes, int() peut toujours donner 0. Utiliser round() ou math.ceil().
    # round() est plus "juste" statistiquement.
    if max_potential_unique_links > 0:
        num_edges_to_generate = round(max_potential_unique_links * connectivity_density_factor)
        # S'assurer qu'on génère au moins une arête si la densité est > 0 et nb_nodes=2
        # Ceci est spécifique pour le cas N=2 où max_potential_unique_links = 1.
        # Si N=2, round(1 * factor) peut être 0 si factor < 0.5.
        # On veut peut-être que si factor > 0, on ait au moins une arête.
        if nb_nodes == 2 and num_edges_to_generate == 0 and connectivity_density_factor >= 0.5:
            num_edges_to_generate = 1
        num_edges_to_generate = min(int(num_edges_to_generate), int(max_potential_unique_links))
        # Pour les graphes plus grands, round() est généralement bien.
        # Assurer qu'il ne dépasse pas le maximum.
        

    else: # nb_nodes = 1 ou 0
        num_edges_to_generate = 0
    # --- FIN MODIFICATION ---

    edges_added = 0
    
    possible_undirected_pairs = []
    if nb_nodes > 1:
        # Créer des paires non orientées (u,v) où u < v alphabétiquement pour éviter doublons et auto-boucles
        for i in range(nb_nodes):
            for j in range(i + 1, nb_nodes):
                possible_undirected_pairs.append((nodes[i], nodes[j]))
    random.shuffle(possible_undirected_pairs)

    for u_pair, v_pair in possible_undirected_pairs:
        if edges_added >= num_edges_to_generate:
            break
        
        # Choisir aléatoirement la direction de l'arête pour cette paire
        if random.choice([True, False]):
            u, v = u_pair, v_pair
        else:
            u, v = v_pair, u_pair
            
        # S'assurer que l'arête n'existe pas DÉJÀ (ne devrait pas arriver avec cette logique)
        # et que l'inverse n'existe pas (la logique de paire non-orientée le garantit)
        if not G.has_edge(u,v): # L'inverse ne sera pas là car on traite chaque paire une fois
            weight = random.randint(1, 200) # Poids par défaut, peut inclure négatifs si Bellman-Ford
            # Pour éviter les cycles négatifs faciles, on peut limiter les poids négatifs.
            # Par exemple, faire que les poids négatifs soient moins fréquents ou moins importants.
            # if random.random() < 0.15: # 15% de chance d'avoir un poids négatif
            #    weight = random.randint(-50, -1) 
            G.add_edge(u, v, weight=weight)
            edges_added += 1
            
    # Calcul du taux de connectivité basé sur le nombre d'arêtes ajoutées
    # par rapport au maximum possible sous la contrainte de non-bidirectionnalité.
    if max_potential_unique_links > 0:
        # edges_added est le nombre de liens logiques que nous avons décidé de créer.
        connectivity_rate_percent = (edges_added / max_potential_unique_links) * 100.0
    elif nb_nodes == 1: # Un seul noeud
        connectivity_rate_percent = 0.0 # Pas d'arêtes possibles.
    else: # nb_nodes == 0 (devrait être attrapé plus tôt)
        connectivity_rate_percent = 0.0
    
    connectivity_rate_percent = min(connectivity_rate_percent, 100.0) # Assurer la borne sup

    # --- Bellman-Ford Algorithm Core ---
    # ... (Reste de la fonction inchangé) ...
    distances = {}
    predecessors = {} 
    try:
        for node in G.nodes():
            distances[node] = float('inf')
            predecessors[node] = None
        
        if source not in G: 
             return f"Erreur interne: Nœud source '{source}' non trouvé dans le graphe G.", {}, G, None, connectivity_rate_percent
        distances[source] = 0

        num_graph_nodes = G.number_of_nodes()
        for i in range(num_graph_nodes - 1): # N-1 itérations
            changed_in_iteration = False
            for u_edge, v_edge, data_edge in G.edges(data=True):
                weight_edge = data_edge['weight']
                if distances.get(u_edge, float('inf')) != float('inf') and \
                   distances[u_edge] + weight_edge < distances.get(v_edge, float('inf')):
                    distances[v_edge] = distances[u_edge] + weight_edge
                    predecessors[v_edge] = u_edge
                    changed_in_iteration = True
            # Optimisation: si aucune distance n'a changé lors d'une itération, on peut s'arrêter
            if not changed_in_iteration and i > 0: # i > 0 pour s'assurer qu'au moins une itération complète a eu lieu
                break 
        
        # Vérification des cycles négatifs
        for u_edge, v_edge, data_edge in G.edges(data=True):
            weight_edge = data_edge['weight']
            if distances.get(u_edge, float('inf')) != float('inf') and \
               distances[u_edge] + weight_edge < distances.get(v_edge, float('inf')):
                # Pour rendre le graphe toujours visualisable, même avec cycle négatif,
                # on ne retourne pas None pour G. L'interface affichera le message d'erreur.
                return "Cycle négatif détecté ! Les distances ne sont pas fiables.", distances, G, None, connectivity_rate_percent

        result_text = f"Distances les plus courtes depuis {source} (Bellman-Ford):\n"
        for node_key in sorted(nodes): # Utiliser `nodes` pour un ordre cohérent
            d = distances.get(node_key, float('inf'))
            result_text += f"  - {node_key} : {d if d != float('inf') else '∞ (non accessible)'}\n"
        
        path_to_destination_edges = None
        if destination:
            if distances.get(destination, float('inf')) == float('inf'):
                result_text += f"\nAucun chemin de {source} à {destination}."
            else:
                # Reconstruction du chemin
                path_to_destination_nodes = []
                curr = destination
                path_construction_attempts = 0 
                max_path_attempts = num_graph_nodes + 5 # Limite pour éviter boucle infinie
                
                while curr is not None and path_construction_attempts < max_path_attempts:
                    path_to_destination_nodes.insert(0, curr)
                    if curr == source: break # Chemin trouvé
                    prev_node = predecessors.get(curr)
                    
                    # Vérifications pour robustesse de reconstruction
                    if prev_node is None and curr != source : # Nœud sans prédécesseur avant d'atteindre source
                        path_to_destination_nodes = [] # Invalider chemin
                        break
                    if prev_node == curr : # Auto-boucle dans prédécesseurs (ne devrait pas arriver)
                        path_to_destination_nodes = [] # Invalider chemin
                        break
                    if prev_node in path_to_destination_nodes : # Cycle détecté dans la reconstruction (ne devrait pas si pas de cycle négatif)
                        # This could happen if the graph structure is unusual or if there was an error in pred updates.
                        print(f"Bellman-Ford Warning: Cycle détecté lors de la reconstruction du chemin vers {destination}. Prédécesseurs: {predecessors}")
                        path_to_destination_nodes = []
                        break

                    curr = prev_node
                    path_construction_attempts +=1
                
                if path_construction_attempts >= max_path_attempts and (not path_to_destination_nodes or path_to_destination_nodes[0] != source):
                    path_to_destination_nodes = [] # Chemin invalide si limite atteinte sans succès
                    result_text += f"\nErreur de reconstruction ou limite d'itération atteinte pour chemin vers {destination}."

                if path_to_destination_nodes and path_to_destination_nodes[0] == source:
                    path_to_destination_edges = []
                    if len(path_to_destination_nodes) > 1:
                        for i in range(len(path_to_destination_nodes) - 1):
                            u_path, v_path = path_to_destination_nodes[i], path_to_destination_nodes[i+1]
                            if G.has_edge(u_path, v_path):
                                path_to_destination_edges.append((u_path, v_path))
                            else: 
                                # This is a serious error if Bellman-Ford pred[] implies an edge that G doesn't have.
                                result_text += f"\nErreur critique: L'arête {u_path}->{v_path} du chemin reconstruit n'existe pas dans le graphe."
                                path_to_destination_edges = None 
                                break 
                    
                    if path_to_destination_edges is not None: # (ou est [] si chemin direct source->destination de 1 noeud)
                        result_text += f"\nChemin le plus court de {source} à {destination} : {' → '.join(path_to_destination_nodes)}\n"
                        result_text += f"Distance totale : {distances[destination]}"
                elif distances.get(destination, float('inf')) != float('inf'): 
                     # Il y a une distance, mais on n'a pas pu reconstruire le chemin pour une raison
                     result_text += f"\nUn chemin vers {destination} existe (distance {distances[destination]}), mais la reconstruction détaillée a échoué."

        return result_text, distances, G, path_to_destination_edges, connectivity_rate_percent

    except Exception as e: 
        import traceback # Assurez-vous que c'est importé
        print("--- ERREUR DANS bellman_ford_graph CORE ---")
        traceback.print_exc()
        print("--- FIN ERREUR bellman_ford_graph CORE ---")
        # Retourner G même en cas d'erreur permet de visualiser l'état du graphe si possible.
        return f"Erreur d'exécution majeure dans Bellman-Ford: {type(e).__name__} - {str(e)}", {}, G if 'G' in locals() else None, None, 0.0