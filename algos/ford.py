# algos/ford.py
import networkx as nx
import random
import string
from itertools import product # For generating node names
import math # Pour round ou ceil

def generer_noms_alphabétiques(n):
    """Génère une liste de n noms de nœuds uniques (A, B,..., Z, AA, AB,...)."""
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

def ford_fulkerson(nb_nodes, source_node_name, sink_node_name):
    if nb_nodes <= 0:
        raise ValueError("Le nombre de nœuds doit être positif.")
    if nb_nodes == 1 and source_node_name == sink_node_name: 
        G_trivial = nx.DiGraph(); G_trivial.add_node(source_node_name)
        return 0, set(), G_trivial, 0.0 # Pas d'arêtes, donc 0% de connectivité des arêtes
    if nb_nodes < 2 : 
        G_single = nx.DiGraph()
        if nb_nodes == 1: G_single.add_node(generer_noms_alphabétiques(1)[0])
        return 0, set(), G_single, 0.0

    nodes = generer_noms_alphabétiques(nb_nodes)

    if source_node_name not in nodes:
        raise ValueError(f"Nœud source '{source_node_name}' invalide.")
    if sink_node_name not in nodes:
        raise ValueError(f"Nœud puits '{sink_node_name}' invalide.")
    if source_node_name == sink_node_name:
        # This case might already be handled by nb_nodes == 1 check if only one node overall
        # but good to keep as a safeguard if nb_nodes > 1 but src=sink
        G_error = nx.DiGraph(); G_error.add_nodes_from(nodes)
        return 0, set(), G_error, 0.0 # No meaningful flow if source is sink with multiple nodes

    G = nx.DiGraph()
    G.add_nodes_from(nodes)

    connectivity_density_factor = random.uniform(0, 1) # Densité minimale pour avoir des arêtes si N>1

    # Maximum possible d'arêtes uniques non-bidirectionnelles.
    max_potential_unique_links = (nb_nodes * (nb_nodes - 1)) / 2 if nb_nodes > 1 else 0
    
    # --- MODIFICATION ICI pour num_edges_to_generate ---
    if max_potential_unique_links > 0:
        num_edges_to_generate = round(max_potential_unique_links * connectivity_density_factor)
        # Pour N=2, si round donne 0 mais densité >= 0.5, forcer 1 arête.
        if nb_nodes == 2 and num_edges_to_generate == 0 and connectivity_density_factor >= 0.5:
            num_edges_to_generate = 1
        num_edges_to_generate = min(int(num_edges_to_generate), int(max_potential_unique_links))
    else: # nb_nodes = 1 ou 0
        num_edges_to_generate = 0
    # --- FIN MODIFICATION ---

    edges_added_count = 0
    
    # Itérer sur les paires non-orientées uniques, puis choisir une direction aléatoire
    possible_undirected_pairs = []
    if nb_nodes > 1:
        for i in range(nb_nodes):
            for j in range(i + 1, nb_nodes):
                possible_undirected_pairs.append((nodes[i], nodes[j]))
    random.shuffle(possible_undirected_pairs)

    for u_pair, v_pair in possible_undirected_pairs:
        if edges_added_count >= num_edges_to_generate:
            break
        
        # Choisir aléatoirement la direction
        if random.choice([True, False]):
            u, v = u_pair, v_pair
        else:
            u, v = v_pair, u_pair
        
        # Ajouter l'arête si elle n'existe pas (l'inverse ne sera pas là par construction)
        if not G.has_edge(u,v):
            capacity = random.randint(5, 100) # Capacités typiques pour Ford-Fulkerson
            G.add_edge(u, v, capacity=capacity)
            edges_added_count += 1

    # Calcul du taux de connectivité
    if max_potential_unique_links > 0:
        connectivity_rate_percent = (edges_added_count / max_potential_unique_links) * 100.0
    elif nb_nodes == 1:
        connectivity_rate_percent = 0.0 
    else: 
        connectivity_rate_percent = 0.0
    connectivity_rate_percent = min(connectivity_rate_percent, 100.0)

    # Ford-Fulkerson (using Edmonds-Karp implementation from NetworkX)
    try:
        # nx.maximum_flow gère les cas où source/sink non dans G ou pas de chemin.
        # Vérifier explicitement si les nœuds sont dans le graphe généré.
        if source_node_name not in G or sink_node_name not in G:
            # Devrait être impossible si la logique de nodes/generation est correcte
            # mais sécurité supplémentaire.
             return 0, set(), G, connectivity_rate_percent 


        # Si le graphe est vide (aucun edge ajouté), le flux sera 0.
        if G.number_of_edges() == 0:
            flow_value = 0
            min_cut_edges = set()
        else:
            flow_value, flow_dict = nx.maximum_flow(
                G, source_node_name, sink_node_name, 
                capacity='capacity', # S'assurer de spécifier le nom de l'attribut de capacité
                flow_func=nx.algorithms.flow.edmonds_karp 
            )

            if flow_value > 0 : 
                try:
                    # La fonction minimum_cut peut échouer si le graphe est malformé ou si la source/puits ne sont pas joignables.
                    # S'assurer que source et puits sont joignables avant d'appeler minimum_cut peut être plus sûr.
                    # Ou attraper l'exception NetworkXUnfeasible.
                    if nx.has_path(G, source_node_name, sink_node_name): # Check path existence for cut
                        cut_value, (reachable, non_reachable) = nx.minimum_cut(
                            G, source_node_name, sink_node_name, capacity='capacity'
                        )
                        min_cut_edges = set()
                        for u_cut in reachable:
                            for v_cut in G.successors(u_cut): 
                                if v_cut in non_reachable:
                                    min_cut_edges.add((u_cut, v_cut))
                    else: # No path means flow is 0, cut value also 0.
                        min_cut_edges = set()
                        if flow_value != 0 : # Inconsistency check
                            print(f"Ford-Fulkerson Warning: flow_value {flow_value} > 0 mais pas de chemin trouvé pour la coupe.")

                except nx.NetworkXUnfeasible: # Parfois levée par minimum_cut si s et t sont identiques ou non connectés
                    min_cut_edges = set() 
                except nx.NetworkXError as e_cut: # Autres erreurs de NetworkX pour la coupe
                     print(f"Ford-Fulkerson Warning: Erreur lors du calcul de la coupe minimale: {e_cut}")
                     min_cut_edges = set() # Par défaut, un ensemble vide si la coupe ne peut être calculée.

            else: 
                min_cut_edges = set() 

    except nx.NetworkXUnbounded: # Si les capacités ne sont pas toutes finies ou des cycles de capacité infinie
        raise ValueError(f"Erreur Ford-Fulkerson: Le problème de flux est non borné (capacités infinies ou cycles ?).")
    except nx.NetworkXError as e_nx_flow:
        # Ceci peut arriver si, par ex., source_node_name ou sink_node_name ne sont pas dans G
        # bien qu'on essaie de les valider avant.
        print(f"Ford-Fulkerson Algo - NetworkXError pendant le calcul de flux: {e_nx_flow}")
        # Retourner des valeurs par défaut si le calcul de flux échoue
        # G est toujours retourné pour inspection.
        return 0, set(), G, connectivity_rate_percent 
    except Exception as e_ff_main: 
        import traceback
        print("--- ERREUR FORD-FULKERSON ALGORITHME (CALCUL) ---")
        traceback.print_exc()
        print("--- FIN ERREUR ---")
        raise RuntimeError(f"Erreur inattendue dans le calcul Ford-Fulkerson: {type(e_ff_main).__name__} - {str(e_ff_main)}")

    return flow_value, min_cut_edges, G, connectivity_rate_percent