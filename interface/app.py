# interface.py
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib
import networkx as nx
import algos.bellmanford
import algos.kruskal
import algos.welsh
import algos.dijkstra
import algos.ford
import algos.mpm
import algos.NordO
import algos.moindre_cout
import algos.stepping_stone
import numpy as np
import re
import random
import string

# Utiliser le backend TkAgg pour Matplotlib
matplotlib.use("TkAgg")

# Thème réseaux/télécom
PRIMARY_COLOR = "#003f5c"
ACCENT_COLOR = "#2f4b7c"
HIGHLIGHT_COLOR = "#ffa600"
BG_COLOR = "#e5ecf6"
TEXT_COLOR = "#0b0c10"

class Application:
    def __init__(self):
        self.gui = tk.Tk()
        self.gui.title("SMART-APPLICATION - Réseaux & Télécommunications")
        self.gui.geometry("1200x800")
        self.gui.configure(bg=BG_COLOR)
        
        # Garder une référence aux fenêtres ouvertes
        self.algo_win = None
        self.input_win = None
        self.current_algo_data = {}
        
        self.setup_styles()
        self.create_main_interface()
        
        # Gérer la fermeture propre de l'application
        self.gui.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(".", background=BG_COLOR, foreground=TEXT_COLOR, font=("Arial", 11))
        self.style.configure("TButton", background=PRIMARY_COLOR, foreground="white", padding=8)
        self.style.map("TButton", background=[("active", HIGHLIGHT_COLOR)])
        self.style.configure("Title.TLabel", font=("Helvetica", 20, "bold"), foreground=PRIMARY_COLOR)
        self.style.configure("Subtitle.TLabel", font=("Helvetica", 12), foreground=ACCENT_COLOR)
        self.style.configure("TLabelframe", background=BG_COLOR)
        self.style.configure("TLabelframe.Label", background=BG_COLOR, foreground=PRIMARY_COLOR)
    
    def create_main_interface(self):
        main_frame = ttk.Frame(self.gui)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        header_frame = ttk.Frame(main_frame, padding=20)
        header_frame.pack(fill=tk.X)
        
        ttk.Label(header_frame, 
                 text="SMART APPLICATION", 
                 style="Title.TLabel").pack(pady=10)
                 
        ttk.Label(header_frame, 
                 text="Recherche Opérationnelle pour les Réseaux & Télécommunications", 
                 style="Subtitle.TLabel").pack(pady=5)

        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)
        
        launch_btn = ttk.Button(
            content_frame, 
            text="Lancer un Algorithme", 
            command=self.open_algo_window,
            width=20
        )
        launch_btn.pack(expand=True)

        # Boutons en bas de la fenêtre principale
        footer_frame = ttk.Frame(self.gui)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=10)
        
        ttk.Button(
            footer_frame, 
            text="🚪 Quitter",
            command=self.on_closing
        ).pack(side=tk.RIGHT)

    def open_algo_window(self):
        if self.algo_win and self.algo_win.winfo_exists():
            self.algo_win.lift()
            return
            
        self.algo_win = tk.Toplevel(self.gui)
        self.algo_win.title("Choisissez un algorithme")
        self.algo_win.geometry("1000x600")
        self.algo_win.configure(bg=BG_COLOR)
        self.algo_win.grab_set()
        
        # Gérer la fermeture de cette fenêtre
        self.algo_win.protocol("WM_DELETE_WINDOW", lambda: self.close_window(self.algo_win))

        title_frame = ttk.Frame(self.algo_win)
        title_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Label(title_frame, 
                 text="📡 Sélectionnez un algorithme d'optimisation réseau :", 
                 font=("Arial", 14, "bold"), 
                 foreground=PRIMARY_COLOR,
                 background=BG_COLOR).pack(pady=10)

        algo_buttons = [
            ("🧠 Welsh Powel (coloration)", "welsh", 0, 0),
            ("📡 Dijkstra (chemin court)", "dijkstra", 0, 1),
            ("📆 Metra (planification)", "metra", 0, 2),
            ("🔌 Kruskal (connexion minimale)", "kruskal", 1, 0),
            ("📶 Bellman-Ford", "bellman", 1, 1),
            ("🌐 Ford-Fulkerson (flux)", "ford", 1, 2),
            ("🏭 Nord-Ouest (transport)", "nordouest", 2, 0),
            ("💰 Moindre Coût", "cout", 2, 1),
            ("🪨 Stepping-Stone", "steep", 2, 2),
        ]

        button_frame = ttk.Frame(self.algo_win)
        button_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        for name, key, row, col in algo_buttons:
            btn = ttk.Button(
                button_frame,
                text=name,
                width=30,
                command=lambda k=key: self.show_input_window(k)
            )
            btn.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
            button_frame.grid_columnconfigure(col, weight=1)
        
        for i in range(3):
            button_frame.grid_rowconfigure(i, weight=1)

        # Bouton Retour
        back_btn = ttk.Button(
            self.algo_win, 
            text="⬅️ Retour",
            command=lambda: self.close_window(self.algo_win)
        )
        back_btn.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Bouton Quitter
        quit_btn = ttk.Button(
            self.algo_win, 
            text="🚪 Quitter",
            command=self.on_closing
        )
        quit_btn.pack(side=tk.RIGHT, padx=20, pady=10)

    def show_input_window(self, algo_key):
        if self.input_win and self.input_win.winfo_exists():
            self.input_win.destroy()
            
        self.input_win = tk.Toplevel()
        self.input_win.title(f"🔧 {algo_key.capitalize()}")
        self.input_win.geometry("1200x900")
        self.input_win.configure(bg=BG_COLOR)
        self.input_win.grab_set()
        self.current_algo_data = {}
        
        # Gérer la fermeture de cette fenêtre
        self.input_win.protocol("WM_DELETE_WINDOW", lambda: self.close_window(self.input_win))

        # Header avec titre et boutons
        header_frame = ttk.Frame(self.input_win)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(header_frame, 
                 text=f"⚙️ {algo_key.capitalize()}", 
                 font=("Arial", 16, "bold"), 
                 foreground=PRIMARY_COLOR,
                 background=BG_COLOR).pack(side=tk.LEFT, padx=10)
        
        # Frame pour les boutons d'action
        action_frame = ttk.Frame(header_frame)
        action_frame.pack(side=tk.RIGHT, padx=10)
        
        # Bouton Retour
        back_btn = ttk.Button(
            action_frame, 
            text="⬅️ Retour",
            command=lambda: self.back_to_algo_selection()
        )
        back_btn.grid(row=0, column=0, padx=5)
        
        # Bouton Quitter
        quit_btn = ttk.Button(
            action_frame, 
            text="🚪 Quitter",
            command=self.on_closing
        )
        quit_btn.grid(row=0, column=1, padx=5)

        # Conteneur principal
        main_container = ttk.Frame(self.input_win)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Panneau de paramètres
        param_frame = ttk.LabelFrame(main_container, text="Paramètres", padding=10)
        param_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.input_vars = {}
        placeholders = {
            "welsh": [("Nombre de sommets", "e.g. 5")],
            "kruskal": [("Nombre de sommets", "e.g. 6")],
            "dijkstra": [("Nombre de sommets", "e.g. 6"), ("Noeud source", "e.g. A")],
            "bellman": [("Nombre de sommets", "e.g. 6"), ("Noeud source", "e.g. A")],
            "ford": [("Nombre de sommets", "e.g. 6"), ("Noeud source", "e.g. A"), ("Noeud puits", "e.g. F")],
            "metra": [("Nombre de tâches", "e.g. 4")],
            "nordouest": [("Nombre d'usines", "e.g. 3"), ("Nombre de magasins", "e.g. 3")],
            "cout": [("Nombre d'usines", "e.g. 3"), ("Nombre de magasins", "e.g. 3")],
            "steep": [("Nombre d'usines", "e.g. 3"), ("Nombre de magasins", "e.g. 3")],
        }

        param_grid = ttk.Frame(param_frame)
        param_grid.pack(fill=tk.X, pady=5)
        
        for i, (label_text, placeholder) in enumerate(placeholders.get(algo_key, [])):
            frame = ttk.Frame(param_grid)
            frame.grid(row=i, column=0, sticky="ew", pady=5)
            param_grid.columnconfigure(0, weight=1)
            
            ttk.Label(frame, text=label_text, width=20, anchor="w").pack(side=tk.LEFT, padx=5)
            
            var = tk.StringVar()
            self.input_vars[label_text] = var
            
            entry = ttk.Entry(frame, textvariable=var, width=20)
            entry.insert(0, placeholder)
            entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            if "sommets" in label_text:
                ttk.Label(frame, text="(1-26)").pack(side=tk.LEFT, padx=5)

        # Boutons d'exécution
        btn_frame = ttk.Frame(param_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        run_btn = ttk.Button(
            btn_frame, 
            text="▶️ Exécuter l'algorithme", 
            width=20,
            command=lambda: self.run_algorithm(algo_key)
        )
        run_btn.pack(side=tk.LEFT, padx=5)

        # Panneau de résultats
        result_frame = ttk.LabelFrame(main_container, text="Résultats", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Notebook pour graphique et texte
        self.notebook = ttk.Notebook(result_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Onglet Graphique
        self.graph_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.graph_tab, text="Visualisation")
        
        # Onglet Texte
        self.text_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.text_tab, text="Résultat Texte")
        
        # Zone de texte pour les résultats
        self.text_box = tk.Text(self.text_tab, wrap=tk.WORD, font=("Courier", 10))
        self.text_scroll = ttk.Scrollbar(self.text_tab, command=self.text_box.yview)
        self.text_box.config(yscrollcommand=self.text_scroll.set)
        
        self.text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_box.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.text_box.config(state="disabled")
        
        # Frame pour le graphique
        self.graph_container = ttk.Frame(self.graph_tab)
        self.graph_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Initialiser avec un graphique vide
        self.display_graph()

    def display_graph(self, new_fig=None):
        # Effacer le contenu précédent
        for widget in self.graph_container.winfo_children():
            widget.destroy()
            
        if new_fig is None:
            fig = Figure(figsize=(10, 8), dpi=100)
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, "Exécutez l'algorithme pour voir la visualisation", 
                    ha='center', va='center', fontsize=14)
            ax.axis('off')
            canvas = FigureCanvasTkAgg(fig, master=self.graph_container)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            canvas = FigureCanvasTkAgg(new_fig, master=self.graph_container)
            toolbar = NavigationToolbar2Tk(canvas, self.graph_container)
            toolbar.update()
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def display_text(self, text):
        self.text_box.config(state="normal")
        self.text_box.delete("1.0", tk.END)
        self.text_box.insert("1.0", text)
        self.text_box.config(state="disabled")
        self.notebook.select(1)  # Basculer vers l'onglet texte

    def run_algorithm(self, algo_key):
        try:
            self.current_algo_data = {}
            fig = None
            result_text = ""
            
            if algo_key == "welsh":
                nb = int(self.input_vars["Nombre de sommets"].get())
    
                # Récupère le graphe et la coloration
                graph, graph_couleur = algos.welsh.welsh(nb)
                result_text = str(graph_couleur)
    
                # Créer la visualisation
                fig = Figure(figsize=(10, 6), dpi=100)
                ax = fig.add_subplot(111)
    
                G = nx.Graph()
    
    # Ajouter les nœuds
                for node in graph:
                    G.add_node(node)
    
    # Ajouter les arêtes
                for node, voisins in graph.items():
                    for voisin, _ in voisins:
                        if not G.has_edge(node, voisin):
                            G.add_edge(node, voisin)
    
    # Mise en page et coloriage
                pos = nx.spring_layout(G, seed=42)
                node_colors = [graph_couleur[node] for node in G.nodes()]
    
                nx.draw(G, pos, with_labels=True, node_color=node_colors, ax=ax, node_size=600, font_size=10)
                ax.set_title("Coloration du graphe (Welsh-Powell)")
    
                self.display_graph(fig)
                self.display_text(result_text)
                
            elif algo_key == "kruskal":
                nb = int(self.input_vars["Nombre de sommets"].get())
                total_weight, mst, G = algos.kruskal.kruskal(nb)
                result_text = f"Poids total de l'arbre couvrant minimal : {total_weight}"
                
                # Créer la visualisation
                fig = Figure(figsize=(8, 6), dpi=100)
                ax = fig.add_subplot(111)
                
                pos = nx.spring_layout(G, seed=42)
                nx.draw(G, pos, with_labels=True, node_color="lightblue", edge_color="gray", 
                       width=1, node_size=500, ax=ax)
                nx.draw_networkx_edges(G, pos, edgelist=mst.edges(), edge_color="red", width=2, ax=ax)
                
                edge_labels = nx.get_edge_attributes(G, 'weight')
                nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax)
                
                red_line = Line2D([], [], color='red', linewidth=2, label="Arbre couvrant minimal")
                ax.legend(handles=[red_line], loc="upper right")
                ax.set_title("Arbre couvrant minimal - Kruskal")
                
                self.display_graph(fig)
                self.display_text(result_text)
                
            elif algo_key == "dijkstra":
                nb = int(self.input_vars["Nombre de sommets"].get())
                src = self.input_vars["Noeud source"].get().upper()
                dist, chemins, G = algos.dijkstra.dijkstra(nb, src)
                
                # Construire le résultat textuel
                result_text = "🗺️ Cas d'utilisation : Recherche du chemin le plus court\n\n"
                if isinstance(dist, str):
                    result_text += dist
                else:
                    result_text += f"Distances depuis {src} :\n"
                    for k, v in dist.items():
                        result_text += f"{k} : {v}\n"
                
                # Créer la visualisation
                fig = Figure(figsize=(10, 8), dpi=100)
                ax = fig.add_subplot(111)
                
                pos = nx.spring_layout(G, seed=42)
                nx.draw(G, pos, with_labels=False, node_color="lightblue", node_size=700, 
                       edge_color='gray', ax=ax)
                
                # Afficher les distances dans les nœuds
                new_labels = {node: f"{node}\n({dist[node] if dist[node] != float('inf') else '∞'})" 
                             for node in G.nodes()}
                nx.draw_networkx_labels(G, pos, labels=new_labels, font_size=10, ax=ax)
                
                # Afficher les poids des arêtes
                edge_labels = nx.get_edge_attributes(G, 'weight')
                nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax)
                
                # Afficher les chemins
                colors = plt.cm.tab10.colors
                legend_handles = []
                for i, (target, edges) in enumerate(chemins.items()):
                    color = colors[i % len(colors)]
                    nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color=[color], 
                                          width=3, ax=ax)
                    distance = dist[target]
                    legend_handles.append(Line2D([], [], color=color, 
                                               label=f"{src} → {target} = {distance}"))
                
                ax.legend(handles=legend_handles, loc="upper left", title="Chemins les plus courts")
                ax.set_title(f"Dijkstra depuis {src}")
                ax.axis('off')
                
                self.display_graph(fig)
                self.display_text(result_text)
                
            elif algo_key == "bellman":
                nb = int(self.input_vars["Nombre de sommets"].get())
                src = self.input_vars["Noeud source"].get().upper()
                result_text, distances, G = algos.bellmanford.bellman_ford_graph(nb, src)
                
                # Créer la visualisation
                fig = Figure(figsize=(10, 8), dpi=100)
                ax = fig.add_subplot(111)
                
                pos = nx.spring_layout(G, seed=42)
                
                # Gérer les distances si elles sont disponibles
                if distances:
                    min_dist = min(distances.values())
                    max_dist = max(distances.values())
                    colors = []
                    for node in G.nodes():
                        d = distances.get(node, float('inf'))
                        if d == float('inf'):
                            colors.append("#cccccc")
                        else:
                            norm = (d - min_dist) / (max_dist - min_dist + 1e-5)
                            r = int(255 * norm)
                            b = 255 - r
                            colors.append(f"#{r:02x}00{b:02x}")
                else:
                    colors = ["lightblue"] * len(G.nodes)
                
                nx.draw(G, pos, with_labels=True, node_color=colors, edge_color='gray',
                       node_size=800, arrows=True, ax=ax)
                
                # Mettre en évidence la source
                if src in G.nodes:
                    nx.draw_networkx_nodes(G, pos, nodelist=[src], node_color='green', 
                                          node_size=800, ax=ax)
                
                edge_labels = nx.get_edge_attributes(G, 'weight')
                if edge_labels:
                    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax)
                
                ax.set_title("Algorithme de Bellman-Ford")
                
                self.display_graph(fig)
                self.display_text(result_text)
                
            elif algo_key == "ford":
                nb = int(self.input_vars["Nombre de sommets"].get())
                source = self.input_vars["Noeud source"].get().upper()
                sink = self.input_vars["Noeud puits"].get().upper()
                max_flow, cut_edges, G = algos.ford.ford_fulkerson(nb, source, sink)
                
                # Construire le résultat textuel
                result = f"📶 Cas d'utilisation : Calcul du débit maximal\n\n"
                result += f"Flux maximal trouvé : {max_flow}\n"
                result += f"Arêtes dans la coupe minimale : {len(cut_edges)}"
                
                # Créer la visualisation
                fig = Figure(figsize=(10, 8), dpi=100)
                ax = fig.add_subplot(111)
                
                pos = nx.spring_layout(G, seed=42)
                node_colors = []
                for n in G.nodes():
                    if n == source:
                        node_colors.append('lightgreen')
                    elif n == sink:
                        node_colors.append('tomato')
                    else:
                        node_colors.append('skyblue')
                
                nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=700, ax=ax)
                nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold', ax=ax)
                
                normal_edges = [e for e in G.edges() if e not in cut_edges]
                nx.draw_networkx_edges(
                    G, pos, edgelist=normal_edges, 
                    edge_color='gray', arrowsize=20, arrowstyle='-|>', ax=ax,
                    connectionstyle='arc3,rad=0.1'
                )
                
                nx.draw_networkx_edges(
                    G, pos, edgelist=list(cut_edges), 
                    edge_color='red', style='dashed', width=2,
                    arrowsize=20, arrowstyle='-|>', ax=ax,
                    connectionstyle='arc3,rad=0.1'
                )
                
                edge_labels = {(u, v): f"{d['capacity']}" for u, v, d in G.edges(data=True)}
                nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='black', font_size=10, ax=ax)
                
                legend_elements = [
                    Line2D([0], [0], marker='o', color='w', label='Source', markerfacecolor='lightgreen', markersize=15),
                    Line2D([0], [0], marker='o', color='w', label='Puits', markerfacecolor='tomato', markersize=15),
                    Line2D([0], [0], marker='o', color='w', label='Autres noeuds', markerfacecolor='skyblue', markersize=15),
                    Line2D([0], [0], color='gray', lw=2, label='Arcs normaux'),
                    Line2D([0], [0], color='red', lw=2, linestyle='dashed', label='Coupe minimale'),
                ]
                ax.legend(handles=legend_elements, loc='best')
                ax.set_title(f"Ford-Fulkerson - Flux max = {max_flow}")
                ax.axis('off')
                
                self.display_graph(fig)
                self.display_text(result)
                
            elif algo_key == "metra":
                nb = int(self.input_vars["Nombre de tâches"].get())
                
                # Ouvrir fenêtre pour les détails des tâches
                task_win = tk.Toplevel(self.input_win)
                task_win.title("Détails des tâches")
                task_win.geometry("600x500")
                task_win.configure(bg=BG_COLOR)
                task_win.grab_set()
                
                task_entries = []
                
                for i in range(nb):
                    frame = ttk.LabelFrame(task_win, text=f"Tâche {chr(65+i)}", padding=10)
                    frame.pack(fill=tk.X, padx=10, pady=5)
                    
                    # Durée
                    ttk.Label(frame, text="Durée:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
                    duree_entry = ttk.Entry(frame, width=5)
                    duree_entry.grid(row=0, column=1, padx=5, pady=5)
                    
                    # Prédécesseurs
                    ttk.Label(frame, text="Prédécesseurs:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
                    pred_entry = ttk.Entry(frame, width=20)
                    pred_entry.grid(row=0, column=3, padx=5, pady=5)
                    pred_entry.insert(0, "Ex: A,C")
                    
                    def on_focus_in(e, entry=pred_entry):
                        if entry.get() == "Ex: A,C":
                            entry.delete(0, tk.END)
                            
                    def on_focus_out(e, entry=pred_entry):
                        if not entry.get():
                            entry.insert(0, "Ex: A,C")
                            
                    pred_entry.bind("<FocusIn>", on_focus_in)
                    pred_entry.bind("<FocusOut>", on_focus_out)
                    
                    task_entries.append((duree_entry, pred_entry))
                
                def submit_tasks():
                    try:
                        taches_input = {}
                        for i in range(nb):
                            nom = chr(65 + i)
                            try:
                                duree = int(task_entries[i][0].get())
                            except ValueError:
                                self.display_text(f"Durée invalide pour la tâche {nom}")
                                return
                            
                            preds_raw = task_entries[i][1].get().strip().upper()
                            if preds_raw == "EX: A,C":
                                pred_list = []
                            else:
                                preds = preds_raw.replace(" ", "")
                                pred_list = [p for p in preds.split(",") if p]
                            
                            taches_input[nom] = {
                                'duree': duree,
                                'pred': pred_list
                            }
                        
                        # Exécuter l'algorithme et stocker les résultats
                        taches, fig = algos.mpm.algo_potentiel_metra(taches_input)
                        
                        # Construire le résultat textuel
                        text_result = "📅 Cas d'utilisation : Planification de projets\n\n"
                        text_result += "Tâche | DébutTôt | FinTôt | DébutTard | FinTard | Marge | Critique\n"
                        text_result += "-" * 60 + "\n"
                        
                        for t in sorted(taches):
                            data = taches[t]
                            crit = "Oui" if data['marge'] == 0 else "Non"
                            text_result += f"{t:6} | {data['tot']:9} | {data['tft']:7} | {data['tard']:10} | {data['tftard']:8} | {data['marge']:5} | {crit}\n"
                        
                        # Afficher la visualisation
                        self.display_graph(fig)
                        self.display_text(text_result)
                        task_win.destroy()
                        
                    except Exception as e:
                        self.display_text(f"Erreur : {str(e)}")
                
                btn_frame = ttk.Frame(task_win)
                btn_frame.pack(fill=tk.X, padx=10, pady=10)
                
                ttk.Button(btn_frame, text="Valider", command=submit_tasks).pack(side=tk.LEFT, padx=5)
                ttk.Button(btn_frame, text="Annuler", command=task_win.destroy).pack(side=tk.RIGHT, padx=5)
                
            elif algo_key == "nordouest":
                n_usines = int(self.input_vars["Nombre d'usines"].get())
                n_magasins = int(self.input_vars["Nombre de magasins"].get())
                
                # Ouvrir fenêtre pour saisir les données
                data_win = tk.Toplevel(self.input_win)
                data_win.title("Données du problème de transport")
                data_win.geometry("800x600")
                data_win.configure(bg=BG_COLOR)
                data_win.grab_set()
                
                # Créer un tableau pour les coûts
                cout_frame = ttk.LabelFrame(data_win, text="Coûts de transport", padding=10)
                cout_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
                
                # Entrées pour les coûts (matrice n_usines x n_magasins)
                cout_entries = []
                for i in range(n_usines):
                    row_entries = []
                    row_frame = ttk.Frame(cout_frame)
                    row_frame.pack(fill=tk.X, pady=2)
                    ttk.Label(row_frame, text=f"Usine {i+1}").pack(side=tk.LEFT)
                    for j in range(n_magasins):
                        entry = ttk.Entry(row_frame, width=5)
                        entry.pack(side=tk.LEFT, padx=2)
                        entry.insert(0, "0")
                        row_entries.append(entry)
                    cout_entries.append(row_entries)
                
                # Entrées pour les offres
                offre_frame = ttk.LabelFrame(data_win, text="Offres (production)", padding=10)
                offre_frame.pack(fill=tk.X, padx=10, pady=5)
                offre_entries = []
                for i in range(n_usines):
                    frame = ttk.Frame(offre_frame)
                    frame.pack(fill=tk.X, pady=2)
                    ttk.Label(frame, text=f"Usine {i+1}").pack(side=tk.LEFT)
                    entry = ttk.Entry(frame, width=10)
                    entry.pack(side=tk.LEFT, padx=5)
                    entry.insert(0, "0")
                    offre_entries.append(entry)
                
                # Entrées pour les demandes
                demande_frame = ttk.LabelFrame(data_win, text="Demandes (clients)", padding=10)
                demande_frame.pack(fill=tk.X, padx=10, pady=5)
                demande_entries = []
                for j in range(n_magasins):
                    frame = ttk.Frame(demande_frame)
                    frame.pack(fill=tk.X, pady=2)
                    ttk.Label(frame, text=f"Magasin {j+1}").pack(side=tk.LEFT)
                    entry = ttk.Entry(frame, width=10)
                    entry.pack(side=tk.LEFT, padx=5)
                    entry.insert(0, "0")
                    demande_entries.append(entry)
                
                def submit_data():
                    try:
                        # Récupérer les coûts
                        couts = []
                        for i in range(n_usines):
                            row = []
                            for j in range(n_magasins):
                                val = int(cout_entries[i][j].get())
                                row.append(val)
                            couts.append(row)
                        
                        # Récupérer les offres
                        offres = [int(entry.get()) for entry in offre_entries]
                        
                        # Récupérer les demandes
                        demandes = [int(entry.get()) for entry in demande_entries]
                        
                        # Vérifier que la somme des offres = somme des demandes
                        if sum(offres) != sum(demandes):
                            messagebox.showerror("Erreur", "La somme des offres doit égaler la somme des demandes.")
                            return
                        
                        # Copie des offres et demandes car l'algorithme va les modifier
                        offres_copie = offres.copy()
                        demandes_copie = demandes.copy()
                        
                        # Appeler l'algorithme
                        solution, cout_total = algos.NordO.nord_ouest(offres_copie, demandes_copie, couts)
                        
                        # Construire le résultat textuel
                        result_text = "Méthode du coin Nord-Ouest\n\n"
                        result_text += "Solution (quantités transportées) :\n"
                        for i in range(n_usines):
                            for j in range(n_magasins):
                                result_text += f"{solution[i][j]}\t"
                            result_text += "\n"
                        result_text += f"\nCoût total: {cout_total}"
                        
                        # Afficher le résultat
                        self.display_text(result_text)
                        
                        # Créer une visualisation sous forme de tableau
                        fig = Figure(figsize=(10, 6), dpi=100)
                        ax = fig.add_subplot(111)
                        ax.axis('off')
                        
                        # Préparer les données pour le tableau
                        table_data = []
                        
                        # En-têtes des colonnes
                        header = [""] + [f"Magasin {j+1}" for j in range(n_magasins)] + ["Offre"]
                        table_data.append(header)
                        
                        # Lignes des usines
                        for i in range(n_usines):
                            row = [f"Usine {i+1}"]
                            for j in range(n_magasins):
                                # Afficher quantité transportée et coût unitaire
                                cell_text = f"{solution[i][j]} / {couts[i][j]}"
                                row.append(cell_text)
                            row.append(str(offres[i]))
                            table_data.append(row)
                            
                        # Ligne des demandes
                        last_row = ["Demande"] + [str(demandes[j]) for j in range(n_magasins)] + [str(sum(offres))]
                        table_data.append(last_row)
                        
                        # Créer le tableau
                        table = ax.table(
                            cellText=table_data,
                            cellLoc='center',
                            loc='center'
                        )
                        
                        # Mise en forme du tableau
                        table.auto_set_font_size(False)
                        table.set_fontsize(10)
                        
                        # Mettre en valeur les cellules avec des quantités > 0
                        for i in range(1, n_usines + 1):
                            for j in range(1, n_magasins + 1):
                                if solution[i-1][j-1] > 0:
                                    table[(i, j)].set_facecolor('#e6f7ff')  # Couleur de fond pour les cellules utilisées
                        
                        # Titre avec le coût total
                        ax.set_title(f"Solution Nord-Ouest - Coût total: {cout_total}", fontsize=14, pad=20)
                        
                        # Ajuster la taille des cellules
                        table.scale(1, 1.5)
                        
                        self.display_graph(fig)
                        data_win.destroy()
                        
                    except Exception as e:
                        self.display_text(f"Erreur: {str(e)}")
                
                btn_frame = ttk.Frame(data_win)
                btn_frame.pack(fill=tk.X, padx=10, pady=10)
                
                ttk.Button(btn_frame, text="Valider", command=submit_data).pack(side=tk.LEFT, padx=5)
                ttk.Button(btn_frame, text="Annuler", command=data_win.destroy).pack(side=tk.RIGHT, padx=5)
                
            elif algo_key == "cout":  # Moindre coût
                n_usines = int(self.input_vars["Nombre d'usines"].get())
                n_magasins = int(self.input_vars["Nombre de magasins"].get())
                
                # Ouvrir fenêtre pour saisir les données
                data_win = tk.Toplevel(self.input_win)
                data_win.title("Données du problème de transport")
                data_win.geometry("800x600")
                data_win.configure(bg=BG_COLOR)
                data_win.grab_set()
                
                # Créer un tableau pour les coûts
                cout_frame = ttk.LabelFrame(data_win, text="Coûts de transport", padding=10)
                cout_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
                
                # Entrées pour les coûts (matrice n_usines x n_magasins)
                cout_entries = []
                for i in range(n_usines):
                    row_entries = []
                    row_frame = ttk.Frame(cout_frame)
                    row_frame.pack(fill=tk.X, pady=2)
                    ttk.Label(row_frame, text=f"Usine {i+1}").pack(side=tk.LEFT)
                    for j in range(n_magasins):
                        entry = ttk.Entry(row_frame, width=5)
                        entry.pack(side=tk.LEFT, padx=2)
                        entry.insert(0, "0")
                        row_entries.append(entry)
                    cout_entries.append(row_entries)
                
                # Entrées pour les offres
                offre_frame = ttk.LabelFrame(data_win, text="Offres (production)", padding=10)
                offre_frame.pack(fill=tk.X, padx=10, pady=5)
                offre_entries = []
                for i in range(n_usines):
                    frame = ttk.Frame(offre_frame)
                    frame.pack(fill=tk.X, pady=2)
                    ttk.Label(frame, text=f"Usine {i+1}").pack(side=tk.LEFT)
                    entry = ttk.Entry(frame, width=10)
                    entry.pack(side=tk.LEFT, padx=5)
                    entry.insert(0, "0")
                    offre_entries.append(entry)
                
                # Entrées pour les demandes
                demande_frame = ttk.LabelFrame(data_win, text="Demandes (clients)", padding=10)
                demande_frame.pack(fill=tk.X, padx=10, pady=5)
                demande_entries = []
                for j in range(n_magasins):
                    frame = ttk.Frame(demande_frame)
                    frame.pack(fill=tk.X, pady=2)
                    ttk.Label(frame, text=f"Magasin {j+1}").pack(side=tk.LEFT)
                    entry = ttk.Entry(frame, width=10)
                    entry.pack(side=tk.LEFT, padx=5)
                    entry.insert(0, "0")
                    demande_entries.append(entry)
                
                def submit_data():
                    try:
                        # Récupérer les coûts
                        couts = []
                        for i in range(n_usines):
                            row = []
                            for j in range(n_magasins):
                                val = int(cout_entries[i][j].get())
                                row.append(val)
                            couts.append(row)
                        
                        # Récupérer les offres
                        offres = [int(entry.get()) for entry in offre_entries]
                        
                        # Récupérer les demandes
                        demandes = [int(entry.get()) for entry in demande_entries]
                        
                        # Vérifier que la somme des offres = somme des demandes
                        if sum(offres) != sum(demandes):
                            messagebox.showerror("Erreur", "La somme des offres doit égaler la somme des demandes.")
                            return
                        
                        # Appeler l'algorithme du moindre coût
                        solution, cout_total = algos.moindre_cout.moindre_cout(offres, demandes, couts)
                        
                        # Construire le résultat textuel
                        result_text = "Méthode du moindre coût\n\n"
                        result_text += "Solution (quantités transportées) :\n"
                        for i in range(n_usines):
                            for j in range(n_magasins):
                                result_text += f"{solution[i][j]}\t"
                            result_text += "\n"
                        result_text += f"\nCoût total: {cout_total}"
                        
                        # Afficher le résultat
                        self.display_text(result_text)
                        
                        # Créer une visualisation sous forme de tableau
                        fig = Figure(figsize=(10, 6), dpi=100)
                        ax = fig.add_subplot(111)
                        ax.axis('off')
                        
                        # Préparer les données pour le tableau
                        table_data = []
                        
                        # En-têtes des colonnes
                        header = [""] + [f"Magasin {j+1}" for j in range(n_magasins)] + ["Offre"]
                        table_data.append(header)
                        
                        # Lignes des usines
                        for i in range(n_usines):
                            row = [f"Usine {i+1}"]
                            for j in range(n_magasins):
                                # Afficher quantité transportée et coût unitaire
                                cell_text = f"{solution[i][j]} / {couts[i][j]}"
                                row.append(cell_text)
                            row.append(str(offres[i]))
                            table_data.append(row)
                            
                        # Ligne des demandes
                        last_row = ["Demande"] + [str(demandes[j]) for j in range(n_magasins)] + [str(sum(offres))]
                        table_data.append(last_row)
                        
                        # Créer le tableau
                        table = ax.table(
                            cellText=table_data,
                            cellLoc='center',
                            loc='center'
                        )
                        
                        # Mise en forme du tableau
                        table.auto_set_font_size(False)
                        table.set_fontsize(10)
                        
                        # Mettre en valeur les cellules avec des quantités > 0
                        for i in range(1, n_usines + 1):
                            for j in range(1, n_magasins + 1):
                                if solution[i-1][j-1] > 0:
                                    table[(i, j)].set_facecolor('#e6f7ff')  # Couleur de fond pour les cellules utilisées
                        
                        # Titre avec le coût total
                        ax.set_title(f"Solution moindre coût - Coût total: {cout_total}", fontsize=14, pad=20)
                        
                        # Ajuster la taille des cellules
                        table.scale(1, 1.5)
                        
                        self.display_graph(fig)
                        data_win.destroy()
                        
                    except Exception as e:
                        self.display_text(f"Erreur: {str(e)}")
                
                btn_frame = ttk.Frame(data_win)
                btn_frame.pack(fill=tk.X, padx=10, pady=10)
                
                ttk.Button(btn_frame, text="Valider", command=submit_data).pack(side=tk.LEFT, padx=5)
                ttk.Button(btn_frame, text="Annuler", command=data_win.destroy).pack(side=tk.RIGHT, padx=5)
                
            elif algo_key == "steep":  # Stepping-Stone
                n_usines = int(self.input_vars["Nombre d'usines"].get())
                n_magasins = int(self.input_vars["Nombre de magasins"].get())
                
                # Ouvrir fenêtre pour saisir les données
                data_win = tk.Toplevel(self.input_win)
                data_win.title("Données du problème de transport")
                data_win.geometry("800x600")
                data_win.configure(bg=BG_COLOR)
                data_win.grab_set()
                
                # Créer un tableau pour les coûts
                cout_frame = ttk.LabelFrame(data_win, text="Coûts de transport", padding=10)
                cout_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
                
                # Entrées pour les coûts (matrice n_usines x n_magasins)
                cout_entries = []
                for i in range(n_usines):
                    row_entries = []
                    row_frame = ttk.Frame(cout_frame)
                    row_frame.pack(fill=tk.X, pady=2)
                    ttk.Label(row_frame, text=f"Usine {i+1}").pack(side=tk.LEFT)
                    for j in range(n_magasins):
                        entry = ttk.Entry(row_frame, width=5)
                        entry.pack(side=tk.LEFT, padx=2)
                        entry.insert(0, "0")
                        row_entries.append(entry)
                    cout_entries.append(row_entries)
                
                # Entrées pour les offres
                offre_frame = ttk.LabelFrame(data_win, text="Offres (production)", padding=10)
                offre_frame.pack(fill=tk.X, padx=10, pady=5)
                offre_entries = []
                for i in range(n_usines):
                    frame = ttk.Frame(offre_frame)
                    frame.pack(fill=tk.X, pady=2)
                    ttk.Label(frame, text=f"Usine {i+1}").pack(side=tk.LEFT)
                    entry = ttk.Entry(frame, width=10)
                    entry.pack(side=tk.LEFT, padx=5)
                    entry.insert(0, "0")
                    offre_entries.append(entry)
                
                # Entrées pour les demandes
                demande_frame = ttk.LabelFrame(data_win, text="Demandes (clients)", padding=10)
                demande_frame.pack(fill=tk.X, padx=10, pady=5)
                demande_entries = []
                for j in range(n_magasins):
                    frame = ttk.Frame(demande_frame)
                    frame.pack(fill=tk.X, pady=2)
                    ttk.Label(frame, text=f"Magasin {j+1}").pack(side=tk.LEFT)
                    entry = ttk.Entry(frame, width=10)
                    entry.pack(side=tk.LEFT, padx=5)
                    entry.insert(0, "0")
                    demande_entries.append(entry)
                
                def submit_data():
                    try:
                        # Récupérer les coûts
                        couts = []
                        for i in range(n_usines):
                            row = []
                            for j in range(n_magasins):
                                val = int(cout_entries[i][j].get())
                                row.append(val)
                            couts.append(row)
                        
                        # Récupérer les offres
                        offres = [int(entry.get()) for entry in offre_entries]
                        
                        # Récupérer les demandes
                        demandes = [int(entry.get()) for entry in demande_entries]
                        
                        # Vérifier que la somme des offres = somme des demandes
                        if sum(offres) != sum(demandes):
                            messagebox.showerror("Erreur", "La somme des offres doit égaler la somme des demandes.")
                            return
                        
                        # Appeler l'algorithme Stepping-Stone
                        solution, cout_total, iterations, methode, solution_init, cout_init, derniere_solution = algos.stepping_stone.stepping_stone(offres, demandes, couts)

                        
                        # Construire le résultat textuel
                        result_text = "🪨 Méthode Stepping-Stone (optimisation)\n\n"
                        result_text += f"Méthode initiale utilisée : {methode}\n"
                        result_text += f"Coût initial : {cout_init}\n"
                        result_text += f"Coût optimisé : {cout_total} (en {iterations} itérations)\n\n"
                        result_text += "Solution optimisée (quantités transportées):\n"
                        for i in range(n_usines):
                            for j in range(n_magasins):
                                result_text += f"{solution[i][j]}\t"
                            result_text += "\n"
                        result_text += f"\nCoût total optimisé: {cout_total}"
                        
                        # Afficher le résultat
                        self.display_text(result_text)
                        
                        # Créer une visualisation sous forme de tableau
                        fig = Figure(figsize=(10, 6), dpi=100)
                        ax = fig.add_subplot(111)
                        ax.axis('off')
                        
                        # Préparer les données pour le tableau
                        table_data = []
                        
                        # En-têtes des colonnes
                        header = [""] + [f"Magasin {j+1}" for j in range(n_magasins)] + ["Offre"]
                        table_data.append(header)
                        
                        # Lignes des usines
                        for i in range(n_usines):
                            row = [f"Usine {i+1}"]
                            for j in range(n_magasins):
                                # Afficher quantité transportée et coût unitaire
                                cell_text = f"{solution[i][j]} / {couts[i][j]}"
                                row.append(cell_text)
                            row.append(str(offres[i]))
                            table_data.append(row)
                            
                        # Ligne des demandes
                        last_row = ["Demande"] + [str(demandes[j]) for j in range(n_magasins)] + [str(sum(offres))]
                        table_data.append(last_row)
                        
                        # Créer le tableau
                        table = ax.table(
                            cellText=table_data,
                            cellLoc='center',
                            loc='center'
                        )
                        
                        # Mise en forme du tableau
                        table.auto_set_font_size(False)
                        table.set_fontsize(10)
                        
                        # Mettre en valeur les cellules avec des quantités > 0
                        for i in range(1, n_usines + 1):
                            for j in range(1, n_magasins + 1):
                                if solution[i-1][j-1] > 0:
                                    table[(i, j)].set_facecolor('#e6f7ff')  # Couleur de fond pour les cellules utilisées
                        
                        # Titre avec le coût total et les itérations
                        ax.set_title(f"Stepping-Stone - Coût optimisé: {cout_total} (en {iterations} itérations)", fontsize=14, pad=20)
                        
                        # Ajuster la taille des cellules
                        table.scale(1, 1.5)
                        
                        self.display_graph(fig)
                        data_win.destroy()
                        
                    except Exception as e:
                        self.display_text(f"Erreur: {str(e)}")
                
                btn_frame = ttk.Frame(data_win)
                btn_frame.pack(fill=tk.X, padx=10, pady=10)
                
                ttk.Button(btn_frame, text="Valider", command=submit_data).pack(side=tk.LEFT, padx=5)
                ttk.Button(btn_frame, text="Annuler", command=data_win.destroy).pack(side=tk.RIGHT, padx=5)
                
            else:
                self.display_text("Algorithme non implémenté encore.")
                
        except Exception as e:
            self.display_text(f"❌ Erreur : {str(e)}")
            # Créer une figure d'erreur
            fig = Figure(figsize=(10, 8), dpi=100)
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, f"Erreur d'exécution:\n{str(e)}", 
                    ha='center', va='center', fontsize=12, color='red')
            ax.axis('off')
            self.display_graph(fig)

    def back_to_algo_selection(self):
        """Retourner à la fenêtre de sélection des algorithmes"""
        if self.input_win and self.input_win.winfo_exists():
            self.input_win.destroy()
        
        if self.algo_win and self.algo_win.winfo_exists():
            self.algo_win.deiconify()
            self.algo_win.lift()
        else:
            self.open_algo_window()

    def close_window(self, window):
        """Fermer une fenêtre proprement"""
        if window and window.winfo_exists():
            window.destroy()
        
        # Si on ferme la fenêtre d'algorithme, réafficher la sélection
        if window == self.input_win:
            self.back_to_algo_selection()

    def on_closing(self):
        """Gérer la fermeture de l'application"""
        if self.input_win and self.input_win.winfo_exists():
            self.input_win.destroy()
        
        if self.algo_win and self.algo_win.winfo_exists():
            self.algo_win.destroy()
            
        self.gui.destroy()

    def run(self):
        self.gui.mainloop()

def init():
    app = Application()
    app.run()