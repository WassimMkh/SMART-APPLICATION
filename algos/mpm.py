# algos/mpm.py
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

def algo_potentiel_metra(taches_input, afficher_console=False):
    taches = {}
    for t, data in taches_input.items():
        taches[t] = {
            'duree': data['duree'],
            'pred': list(data['pred']),
            'succ': [],
            'tot': 0,
            'tft': 0,
            'tard': float('inf'),
            'tftard': float('inf'),
            'marge': 0
        }

    taches['Début'] = {'duree': 0, 'pred': [], 'succ': [], 'tot': 0, 'tft': 0, 'tard': 0, 'tftard': 0, 'marge': 0}
    taches['Fin'] = {'duree': 0, 'pred': [], 'succ': [], 'tot': 0, 'tft': 0, 'tard': float('inf'), 'tftard': float('inf'), 'marge': 0}

    for t in list(taches_input.keys()):
        if not taches[t]['pred']:
            taches[t]['pred'].append('Début')
            taches['Début']['succ'].append(t)

    for t, data in taches.items():
        for p in data['pred']:
            if t not in taches[p]['succ']:
                taches[p]['succ'].append(t)

    taches_terminales = [t for t in taches_input.keys() if not taches[t]['succ']]

    for t in taches_terminales:
        taches[t]['succ'].append('Fin')
        taches['Fin']['pred'].append(t)


    def calc_tot():
        visit = set()
        def dfs(t):
            if t in visit:
                return
            for p in taches[t]['pred']:
                dfs(p)
            if taches[t]['pred']:
                taches[t]['tot'] = max(taches[p]['tft'] for p in taches[t]['pred'])
            taches[t]['tft'] = taches[t]['tot'] + taches[t]['duree']
            visit.add(t)
        for t in taches:
            dfs(t)

    def calc_tard():
        fin_proj = taches['Fin']['tft']
        taches['Fin']['tftard'] = fin_proj
        taches['Fin']['tard'] = fin_proj - taches['Fin']['duree']

        # Ordre topologique inversé
        ordre = []

        visited = set()
        def dfs(t):
            if t in visited:
                return
            visited.add(t)
            for succ in taches[t]['succ']:
                dfs(succ)
            ordre.append(t)

        dfs('Début')
        ordre.reverse()

        for t in ordre:
            if t == 'Fin':
                continue
            succs = taches[t]['succ']
            taches[t]['tftard'] = min(taches[s]['tot'] for s in succs)
            taches[t]['tard'] = taches[t]['tftard'] - taches[t]['duree']

    def calc_marges():
        for t in taches:
            taches[t]['marge'] = taches[t]['tard'] - taches[t]['tot']

    def visualiser():
        G = nx.DiGraph()
        for t in taches:
            d = taches[t]
            label = f"{t}\nTOT:{d['tot']}\nTFT:{d['tft']}"
            G.add_node(t, label=label, tot=d['tot'])
        
        edges_critique = set()
        for t in taches:
            for succ in taches[t]['succ']:
                if taches[t]['marge'] == 0 and taches[succ]['marge'] == 0 and taches[t]['tft'] == taches[succ]['tot']:
                    edges_critique.add((t, succ))
                G.add_edge(t, succ)

        # Calcul des positions par niveau (TOT)
        levels = {}
        for node in G.nodes:
            tot = G.nodes[node]['tot']
            if tot not in levels:
                levels[tot] = []
            levels[tot].append(node)
        
        # Trier les niveaux
        sorted_levels = sorted(levels.keys())
        
        # Calculer les positions
        pos = {}
        vertical_spacing = 1.0
        for level in sorted_levels:
            nodes_in_level = levels[level]
            y_positions = np.linspace(0, (len(nodes_in_level) - 1) * vertical_spacing, len(nodes_in_level))
            for idx, node in enumerate(nodes_in_level):
                pos[node] = (level, y_positions[idx])
        
        # Définir les couleurs
        node_colors = ['red' if taches[n]['marge'] == 0 else 'lightblue' for n in G.nodes]
        edge_colors = ['red' if (u, v) in edges_critique else 'gray' for u, v in G.edges]
        
        # Créer la figure
        fig = Figure(figsize=(10, 8), dpi=100)
        ax = fig.add_subplot(111)
        
        # Dessiner le graphe
        nx.draw_networkx_nodes(
            G, pos, 
            node_color=node_colors, 
            node_size=1500,
            ax=ax
        )
        nx.draw_networkx_edges(
            G, pos, 
            edge_color=edge_colors, 
            arrows=True,
            arrowstyle='-|>',
            arrowsize=20,
            ax=ax
        )
        labels = nx.get_node_attributes(G, 'label')
        nx.draw_networkx_labels(G, pos, labels, font_size=10, ax=ax)
        
        # Ajouter les étiquettes de niveau
        for level in sorted_levels:
            ax.text(
                level, -1, 
                f"J+{level}", 
                ha='center', 
                va='top',
                fontsize=9,
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray')
            )
        
        # Configuration de l'axe
        ax.set_title("Diagramme de Gantt (MPM) - Organisation par niveaux de TOT", fontsize=14)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.set_axisbelow(True)
        ax.set_xlabel("Temps (TOT)")
        ax.set_ylabel("Tâches par niveau")
        ax.set_xticks(sorted_levels)
        ax.set_yticks([])
        ax.set_xlim(min(sorted_levels) - 1, max(sorted_levels) + 1)
        
        # Légende
        critical_patch = plt.Line2D(
            [], [], 
            marker='o', 
            color='w', 
            markerfacecolor='red',
            markersize=10,
            label='Tâche critique'
        )
        normal_patch = plt.Line2D(
            [], [], 
            marker='o', 
            color='w', 
            markerfacecolor='lightblue',
            markersize=10,
            label='Tâche normale'
        )
        ax.legend(handles=[critical_patch, normal_patch], loc='upper right')
        
        return fig

    calc_tot()
    calc_tard()
    calc_marges()

    fig = visualiser()
    return taches, fig