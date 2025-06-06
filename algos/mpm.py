# algos/mpm.py
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
import matplotlib.patches as mpatches # Pour FancyArrowPatch et FancyBboxPatch
import random

def get_rect_border_point(center_x, center_y, angle_rad, rect_width, rect_height):
    """
    Calcule le point d'intersection d'un rayon partant du centre d'un rectangle
    avec le bord de ce rectangle.
    L'angle est par rapport à l'horizontale positive.
    """
    # Les demi-largeurs et demi-hauteurs
    w2 = rect_width / 2.0
    h2 = rect_height / 2.0

    # Cas limites pour éviter division par zéro ou angles extrêmes
    cos_a = np.cos(angle_rad)
    sin_a = np.sin(angle_rad)

    if abs(cos_a) < 1e-6: # Rayon vertical
        return center_x, center_y + np.sign(sin_a) * h2
    if abs(sin_a) < 1e-6: # Rayon horizontal
        return center_x + np.sign(cos_a) * w2, center_y

    # Calculer les intersections avec les 4 côtés du rectangle
    # t_x = w2 / |cos_a|, t_y = h2 / |sin_a|
    # Si t_x < t_y, intersection avec un côté vertical, sinon horizontal
    
    tan_a = sin_a / cos_a # np.tan(angle_rad)

    # Intersection avec les côtés verticaux (x = +/- w2)
    # y_at_x_w2 = tan_a * w2
    # Intersection avec les côtés horizontaux (y = +/- h2)
    # x_at_y_h2 = h2 / tan_a

    # Si l'angle est tel que le rayon coupe un côté vertical avant un horizontal
    if abs(h2 / sin_a) > abs(w2 / cos_a) : # ou abs(y_at_x_w2) <= h2
        intersect_x = np.sign(cos_a) * w2
        intersect_y = tan_a * intersect_x
    else: # Coupe un côté horizontal avant un vertical
        intersect_y = np.sign(sin_a) * h2
        intersect_x = intersect_y / tan_a
        
    return center_x + intersect_x, center_y + intersect_y


def new_visualiser(taches_data, task_arrow_labels=None, dummy_links=None, title="Diagramme MPM / PERT (AON)"):
    if task_arrow_labels is None: task_arrow_labels = {}
    if dummy_links is None: dummy_links = []

    G = nx.DiGraph()
    nodes_to_process_keys = set(taches_data.keys())
    # ... (filtrage Début/Fin comme avant) ...

    if not nodes_to_process_keys:
        fig = Figure(figsize=(10, 8), dpi=100); ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, "Aucune tâche.", ha='center', va='center'); ax.axis('off'); return fig

    for t_name in nodes_to_process_keys:
        t_info = taches_data[t_name]
        G.add_node(t_name)
        for succ_name in t_info.get('succ', []):
            if succ_name in nodes_to_process_keys: G.add_edge(t_name, succ_name)

    if not G.nodes():
        fig = Figure(figsize=(10, 8), dpi=100); ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, "Graphe vide.", ha='center', va='center'); ax.axis('off'); return fig

    pos = {}
    node_levels = {}
    for node_name_layout in G.nodes():
        level = taches_data[node_name_layout]['tot']
        if level not in node_levels: node_levels[level] = []
        node_levels[level].append(node_name_layout)

    sorted_levels_values = sorted(node_levels.keys())
    if not sorted_levels_values:
        fig = Figure(figsize=(10, 8), dpi=100); ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, "Pas de niveaux.", ha='center', va='center'); ax.axis('off'); return fig

    x_coord_indices = {level_val: i for i, level_val in enumerate(sorted_levels_values)}
    
    node_width = 2.0; node_height = 1.0
    horizontal_spacing_factor = node_width + 1.8 # Augmenté
    vertical_spacing_factor = node_height + 1.0   # Augmenté

    max_nodes_in_a_level = 0
    for level_val_orig in sorted_levels_values:
        nodes_in_this_level_sorted = sorted(node_levels[level_val_orig], 
                                            key=lambda n_sort: (taches_data[n_sort].get('marge', float('inf')), n_sort))
        max_nodes_in_a_level = max(max_nodes_in_a_level, len(nodes_in_this_level_sorted))
        num_nodes_current_level = len(nodes_in_this_level_sorted)
        y_level_start_pos = -(num_nodes_current_level - 1) * vertical_spacing_factor / 2.0
        for i_node_layout, node_name_layout_assign in enumerate(nodes_in_this_level_sorted):
            pos[node_name_layout_assign] = (
                x_coord_indices[level_val_orig] * horizontal_spacing_factor, 
                y_level_start_pos + i_node_layout * vertical_spacing_factor
            )
            
    for node_layout_missed in G.nodes():
        if node_layout_missed not in pos: 
            rand_x = (len(sorted_levels_values)+1)*horizontal_spacing_factor 
            rand_y = random.uniform(-1,1)*max_nodes_in_a_level*vertical_spacing_factor/2.0
            pos[node_layout_missed] = (rand_x, rand_y)

    fig_width = max(15, len(sorted_levels_values) * (horizontal_spacing_factor + 1.0) ) 
    fig_height = max(10, max_nodes_in_a_level * (vertical_spacing_factor + 1.0) )
    
    fig, ax = plt.subplots(figsize=(fig_width, fig_height)); fig.patch.set_facecolor('white')

    # --- Dessiner les Arcs (Edges) ---
    for u, v in G.edges():
        if u not in pos or v not in pos: continue
        
        pos_u_center = np.array(pos[u])
        pos_v_center = np.array(pos[v])
        
        if np.allclose(pos_u_center, pos_v_center): continue # Eviter erreur pour nœuds superposés

        # Angle de la ligne reliant les centres
        dx = pos_v_center[0] - pos_u_center[0]
        dy = pos_v_center[1] - pos_v_center[1]
        angle_rad = np.arctan2(dy, dx)

        # Point de départ sur le bord du rectangle u
        pos_u_edge = get_rect_border_point(pos_u_center[0], pos_u_center[1], angle_rad, node_width, node_height)
        # Point d'arrivée sur le bord du rectangle v (angle opposé pour le calcul depuis v)
        pos_v_edge = get_rect_border_point(pos_v_center[0], pos_v_center[1], angle_rad + np.pi, node_width, node_height)
        
        is_critical_edge = (taches_data[u]['marge']==0 and taches_data[v]['marge']==0 and taches_data[u]['tft']==taches_data[v]['tot'])
        is_dummy_edge = (u,v) in dummy_links
        
        arrow_color = 'red' if is_critical_edge else 'black'
        line_style = '--' if is_dummy_edge else '-'
        line_width = 2.5 if is_critical_edge else 1.0
        arrow_mutation_scale = 22 # Taille de la tête de flèche

        rad_val_curve = 0.15 # Légère courbure par défaut
        if G.has_edge(v,u): rad_val_curve = 0.3 
        # Augmenter la courbure si les nœuds sont sur le même niveau verticalement (difficile à faire sans plus de contexte)
        if abs(pos_u_center[0] - pos_v_center[0]) < 0.1 * horizontal_spacing_factor and abs(pos_u_center[1] - pos_v_center[1]) > 0.1 * vertical_spacing_factor :
            rad_val_curve = np.sign(pos_v_center[0]-pos_u_center[0]+1e-6) *0.25 # side-stepping arcs

        arrow = mpatches.FancyArrowPatch(
            pos_u_edge, pos_v_edge, 
            arrowstyle='-|>', 
            mutation_scale=arrow_mutation_scale, color=arrow_color, 
            linestyle=line_style, linewidth=line_width, zorder=1,
            connectionstyle=f"arc3,rad={rad_val_curve}"
        )
        ax.add_patch(arrow)

        if v in taches_data and v not in ['Début','Fin'] and not is_dummy_edge:
            duration_on_arc = taches_data[v]['duree']
            # Positionner l'étiquette de durée le long de l'arc
            # Utiliser le milieu de l'arc entre les points de bordure calculés
            label_x_pos = pos_u_edge[0] * 0.5 + pos_v_edge[0] * 0.5
            label_y_pos = pos_u_edge[1] * 0.5 + pos_v_edge[1] * 0.5
            
            edge_angle_rad_label = np.arctan2(pos_v_edge[1]-pos_u_edge[1], pos_v_edge[0]-pos_u_edge[0])
            perp_offset_dist = 0.25
            offset_x_val = -np.sin(edge_angle_rad_label) * perp_offset_dist
            offset_y_val = np.cos(edge_angle_rad_label) * perp_offset_dist
            
            ax.text(label_x_pos + offset_x_val, label_y_pos + offset_y_val, f"{duration_on_arc}",
                    ha='center', va='center', fontsize=8, color='dimgray', 
                    bbox=dict(facecolor='white',alpha=0.7,pad=0.05,edgecolor='none'), zorder=2)

    # --- Dessiner les Nœuds ---
    node_font_size_name = 9
    node_font_size_values = 8
    for node_name_draw, (x_center, y_center) in pos.items():
        is_critical_node = taches_data[node_name_draw]['marge'] == 0
        node_fill_color = '#fff0f0' if is_critical_node else '#f4f4f4' # Un peu plus distinct
        node_edge_color = 'darkred' if is_critical_node else 'black'
        node_line_width = 1.8 if is_critical_node else 1.2

        rect_patch = mpatches.FancyBboxPatch(
            (x_center - node_width/2, y_center - node_height/2), 
            node_width, node_height,
            boxstyle="round,pad=0.1,rounding_size=0.15", # Plus arrondi
            facecolor=node_fill_color, edgecolor=node_edge_color, 
            linewidth=node_line_width, zorder=3)
        ax.add_patch(rect_patch)
        
        text_color_node = 'darkred' if is_critical_node else 'black'
        task_name_display = node_name_draw
        tot_val_node = taches_data[node_name_draw].get('tot','-')
        val2_node = taches_data[node_name_draw].get('tard','-') # Ou 'tft', 'marge'

        ax.text(x_center, y_center + node_height*0.25, task_name_display, 
                ha='center', va='center', fontsize=node_font_size_name, fontweight='bold', 
                color=text_color_node, zorder=4)
        ax.plot([x_center - node_width/2*0.85, x_center + node_width/2*0.85], [y_center, y_center], 
                color=node_edge_color, linewidth=0.6, zorder=4, alpha=0.7) # Ligne plus subtile
        ax.text(x_center - node_width*0.25, y_center - node_height*0.25, f"{tot_val_node}", 
                ha='center', va='center', fontsize=node_font_size_values, color=text_color_node, zorder=4)
        ax.text(x_center + node_width*0.25, y_center - node_height*0.25, f"{val2_node}", 
                ha='center', va='center', fontsize=node_font_size_values, color=text_color_node, zorder=4)
        ax.plot([x_center, x_center], [y_center - node_height/2*0.85, y_center], 
                color=node_edge_color, linewidth=0.6, zorder=4, alpha=0.7) # Ligne plus subtile

    # --- Configuration finale ---
    critical_patch_legend = mpatches.Patch(facecolor='#fff0f0', edgecolor='darkred', linewidth=1.5, label='Chemin Critique (Nœud/Arc)')
    ax.legend(handles=[critical_patch_legend], loc='upper left', frameon=True, fontsize=9, facecolor='white', framealpha=0.8)
    ax.autoscale_view(); x_min_lim, x_max_lim = ax.get_xlim(); y_min_lim, y_max_lim = ax.get_ylim()
    ax.set_xlim(x_min_lim - node_width*0.8, x_max_lim + node_width*0.8)    
    ax.set_ylim(y_min_lim - node_height*0.8, y_max_lim + node_height*0.8) 
    ax.set_aspect('equal', adjustable='datalim'); ax.axis('off')
    plt.title(title, fontsize=14, fontweight='bold', pad=15)
    fig.tight_layout(pad=1.5)
    return fig

# --- La fonction algo_potentiel_metra reste la même qu'avant ---
# Elle appellera cette version de new_visualiser
# Dans algos/mpm.py
def algo_potentiel_metra(taches_input, afficher_console=False):
    taches = {} # Dictionnaire final avec Début, Fin et les tâches utilisateur
    if not taches_input: # Cas où aucune tâche n'est fournie par l'utilisateur
        # Créer un graphe simple Début -> Fin
        taches['Début'] = {'duree': 0, 'pred': [], 'succ': ['Fin'], 'tot': 0, 'tft': 0, 'tard': 0, 'tftard': 0, 'marge': 0}
        taches['Fin'] = {'duree': 0, 'pred': ['Début'], 'succ': [], 'tot': 0, 'tft': 0, 'tard': 0, 'tftard': 0, 'marge': 0}
        # Le reste des calculs MPM se fera sur cette structure simple.
    else:
        # Initialiser les tâches utilisateur
        for t_name_user, data_user in taches_input.items():
            taches[t_name_user] = {
                'duree': data_user['duree'], 
                'pred': list(data_user['pred']), # Copie de la liste
                'succ': [], # Sera rempli ensuite
                'tot': 0, 'tft': 0, 
                'tard': float('inf'), 'tftard': float('inf'), 
                'marge': 0
            }
        
        # Initialiser Début et Fin
        taches['Début'] = {'duree': 0, 'pred': [], 'succ': [], 'tot': 0, 'tft': 0, 'tard': 0, 'tftard': 0, 'marge': 0}
        taches['Fin'] = {'duree': 0, 'pred': [], 'succ': [], 'tot': 0, 'tft': 0, 'tard': float('inf'), 'tftard': float('inf'), 'marge': 0}

        all_user_task_names = set(taches_input.keys())

        # 1. Construire les listes de successeurs pour les tâches utilisateur
        #    et connecter les tâches sans prédécesseurs à 'Début'
        for t_name_curr in all_user_task_names:
            # Remplir la liste 'succ' des prédécesseurs de t_name_curr
            for pred_name_of_curr in taches[t_name_curr]['pred']:
                if pred_name_of_curr in taches: # S'assurer que le prédécesseur est une tâche valide (ou Début)
                    if t_name_curr not in taches[pred_name_of_curr]['succ']:
                        taches[pred_name_of_curr]['succ'].append(t_name_curr)
            
            # Si t_name_curr n'a pas de prédécesseur (ou seulement 'Début' si déjà traité), le connecter à 'Début'
            # Note: La validation dans l'interface assure que les prédécesseurs sont valides.
            # Une tâche est une "tâche de départ" si sa liste de prédécesseurs (venant de l'utilisateur) est vide.
            if not taches_input[t_name_curr]['pred']: # Basé sur l'input original
                if t_name_curr not in taches['Début']['succ']:
                    taches['Début']['succ'].append(t_name_curr)
                # Assurer la réciprocité dans la structure 'taches'
                if 'Début' not in taches[t_name_curr]['pred']:
                    taches[t_name_curr]['pred'].insert(0, 'Début') # Mettre Début en premier pour la clarté

        # 2. Connecter les tâches terminales (celles sans successeur parmi les tâches utilisateur) à 'Fin'
        for t_name_curr in all_user_task_names:
            is_terminal_among_user_tasks = True
            # Vérifier si t_name_curr est un prédécesseur d'une AUTRE tâche utilisateur
            for other_t_name in all_user_task_names:
                if t_name_curr == other_t_name: continue
                if t_name_curr in taches_input[other_t_name]['pred']: # Vérifier l'input original
                    is_terminal_among_user_tasks = False
                    break
            
            if is_terminal_among_user_tasks:
                if 'Fin' not in taches[t_name_curr]['succ']:
                    taches[t_name_curr]['succ'].append('Fin')
                # Assurer la réciprocité dans la structure 'taches'
                if t_name_curr not in taches['Fin']['pred']:
                    taches['Fin']['pred'].append(t_name_curr)

        # Cas spécial : si après tout ça, Début n'a aucun successeur mais il y avait des tâches,
        # cela signifie que toutes les tâches avaient des prédécesseurs, ce qui est une erreur de logique d'entrée (cycle ou graphe mal formé)
        # Cependant, notre validation de cycle devrait l'attraper.
        # De même pour Fin.
        # Si Début OU Fin est isolé alors qu'il y a des tâches utilisateur, c'est un problème.
        # Le plus probable : Début n'a pas de successeurs OU Fin n'a pas de prédécesseurs.
        if taches_input: # S'il y avait des tâches utilisateur
            if not taches['Début']['succ']:
                 print("MPM Warning: Le nœud 'Début' n'a aucun successeur malgré la présence de tâches. Le graphe est peut-être mal formé ou toutes les tâches ont des prédécesseurs (cycle probable).")
                 # On pourrait tenter de forcer la connexion aux tâches sans pred listés par l'utilisateur, mais c'est déjà fait plus haut.
            if not taches['Fin']['pred']:
                 print("MPM Warning: Le nœud 'Fin' n'a aucun prédécesseur malgré la présence de tâches. Le graphe est peut-être mal formé ou aucune tâche n'est réellement terminale.")

    # --- La suite du code est pour la construction de temp_G_calc et les calculs MPM ---
    # temp_G_calc est construit en utilisant les listes 'succ' du dictionnaire 'taches' finalisé.
    
    temp_G_calc = nx.DiGraph()
    for t_name_graph, t_data_graph in taches.items():
        temp_G_calc.add_node(t_name_graph) # Assurer que tous les nœuds sont ajoutés
    for t_name_graph, t_data_graph in taches.items():
        for succ_name_graph in t_data_graph.get('succ', []):
            if succ_name_graph in taches: # S'assurer que le successeur est une clé valide
                temp_G_calc.add_edge(t_name_graph, succ_name_graph)
            # else: # Debug: un successeur listé n'est pas une clé dans 'taches'
            # print(f"MPM Debug: Successeur '{succ_name_graph}' pour tâche '{t_name_graph}' non trouvé dans le dictionnaire 'taches'.")


    # Vérification de la connectivité à Début et Fin pour le tri topologique
    # Si Début n'est pas une source ou Fin n'est pas un puits, le tri peut échouer.
    if 'Début' in temp_G_calc and temp_G_calc.in_degree('Début') != 0 and taches_input: # Sauf si pas de tâches
        print(f"MPM Warning: 'Début' a des prédécesseurs dans le graphe de calcul: {list(temp_G_calc.predecessors('Début'))}")
    if 'Fin' in temp_G_calc and temp_G_calc.out_degree('Fin') != 0 and taches_input:
        print(f"MPM Warning: 'Fin' a des successeurs dans le graphe de calcul: {list(temp_G_calc.successors('Fin'))}")

    try:
        order_fwd = list(nx.topological_sort(temp_G_calc))
    except nx.NetworkXUnfeasible: 
        # Si un cycle est détecté, cela signifie souvent une erreur dans les dépendances saisies.
        # La validation dans l'interface devrait attraper les auto-prédécesseurs.
        # Des cycles plus longs doivent être détectés ici ou avant par l'interface.
        raise nx.NetworkXUnfeasible("Cycle détecté dans les dépendances des tâches. Impossible de calculer MPM.")
    except nx.NetworkXError as e_topo: 
        # Autres erreurs potentielles du graphe (par ex., si Début/Fin mal connectés rendant le tri impossible)
        # Pourrait être utile de vérifier `nx.is_directed_acyclic_graph(temp_G_calc)` avant `topological_sort`.
        is_dag = nx.is_directed_acyclic_graph(temp_G_calc)
        sources = [node for node, in_degree in temp_G_calc.in_degree() if in_degree == 0]
        sinks = [node for node, out_degree in temp_G_calc.out_degree() if out_degree == 0]
        print(f"MPM Debug: Erreur tri topologique. Est DAG: {is_dag}. Sources: {sources}. Puits: {sinks}. Graphe nodes: {temp_G_calc.nodes}. Graphe edges: {temp_G_calc.edges}. Erreur: {e_topo}")
        raise nx.NetworkXError(f"Erreur de tri topologique: {e_topo}. Graphe mal formé?")

    # --- Calculs MPM (TOT, TFT, TARD, TFTARD, Marge) ---
    # ... (le reste des calculs comme avant) ...
    # Calcul des dates au plus tôt (TOT, TFT)
    for t_name in order_fwd:
        t_node = taches[t_name]; max_pred_tft = 0
        for p_name in t_node.get('pred',[]): # Utiliser .get avec défaut pour robustesse
            if p_name in taches: max_pred_tft = max(max_pred_tft, taches[p_name].get('tft',0))
        t_node['tot'] = max_pred_tft
        t_node['tft'] = t_node['tot'] + t_node.get('duree',0)

    # Date au plus tôt de fin du projet
    project_eft = taches.get('Fin',{}).get('tft',0) # Robustesse avec .get
    if 'Fin' in taches: 
        taches['Fin']['tftard'] = project_eft
        taches['Fin']['tard'] = project_eft 

    # Calcul des dates au plus tard (TARD, TFTARD) en parcourant à l'envers
    for t_name in reversed(order_fwd):
        t_node = taches[t_name]; min_succ_tard = float('inf')
        if t_name == 'Fin': continue # Déjà fait pour Fin
        
        for s_name in t_node.get('succ',[]):
            if s_name in taches: min_succ_tard = min(min_succ_tard, taches[s_name].get('tard', project_eft))
        
        t_node['tftard'] = min_succ_tard if min_succ_tard != float('inf') else project_eft
        t_node['tard'] = t_node['tftard'] - t_node.get('duree',0)

    # Calcul des marges
    for t_name in taches: 
        # Utiliser .get pour éviter KeyError si une clé manque (devrait pas arriver)
        taches[t_name]['marge'] = taches[t_name].get('tard',0) - taches[t_name].get('tot',0)
            
    # Appel au visualiseur
    vis_fig_aon = new_visualiser(taches, {}, [], title="Diagramme MPM") # task_arrow_labels et dummy_links simplifiés/omis pour l'instant
    
    return taches, vis_fig_aon