# interface.py
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.lines as mlines
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
        self.gui.title("SMART-APPLICATION - Réseaux & Télécommunications\n")
        self.gui.geometry("1200x800")
        self.gui.configure(bg=BG_COLOR)
        
        self.algo_win = None
        self.input_win = None
        self.current_algo_data = {}
        
        self.setup_styles()
        self.create_main_interface()
        
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
        
        self.style.configure("Connexity.Horizontal.TProgressbar", 
                            thickness=15,
                            background=HIGHLIGHT_COLOR, # Couleur de la barre (partie remplie - jaune/orange)
                            troughcolor=BG_COLOR,      # Couleur du fond/creux (bleu clair de fond actuel, pourrait être PRIMARY_COLOR)
                            # troughcolor=PRIMARY_COLOR, # Si vous voulez le fond de la barre en bleu foncé
                            bordercolor=PRIMARY_COLOR, # Couleur de la bordure
                            lightcolor=HIGHLIGHT_COLOR, # Utilisé par certains thèmes
                            darkcolor=HIGHLIGHT_COLOR)  # Utilisé par certains thèmes
        # Pour le thème "clam", 'background' est la couleur de la barre, 'troughcolor' est le fond.
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

        back_btn = ttk.Button(
            self.algo_win, 
            text="⬅️ Retour",
            command=lambda: self.close_window(self.algo_win)
        )
        back_btn.pack(side=tk.LEFT, padx=20, pady=10)
        
        quit_btn = ttk.Button(
            self.algo_win, 
            text="🚪 Quitter",
            command=self.on_closing
        )
        quit_btn.pack(side=tk.RIGHT, padx=20, pady=10)

    def _open_predecessor_selector(self, current_task_name_widget, current_task_pred_label, all_task_entries_list):
        """Ouvre une popup pour sélectionner les prédécesseurs."""
        
        # Noms des tâches potentiels (exclure la tâche actuelle et les noms vides/placeholders)
        # On prend les noms ACTUELS des champs d'entrée, ce qui est dynamique
        available_task_names = []
        current_task_actual_name_raw = current_task_name_widget.get().strip().upper()

        for task_entry_dict in all_task_entries_list:
            name_entry_widget = task_entry_dict['name_entry']
            potential_name = name_entry_widget.get().strip().upper()
            if potential_name and name_entry_widget != current_task_name_widget : # Ne pas se choisir soi-même ni les vides
                # S'assurer que le nom n'est pas un placeholder si on voulait être plus strict
                available_task_names.append(potential_name)
        
        # Filtrer les doublons potentiels si l'utilisateur a tapé des noms identiques avant validation finale
        available_task_names = sorted(list(set(available_task_names)))

        if not available_task_names:
            messagebox.showinfo("Prédécesseurs", "Aucune autre tâche n'a encore été nommée pour servir de prédécesseur.",
                                parent=self.input_win) # Ou la task_win si elle existe et est parente
            return

        selector_win = tk.Toplevel(self.input_win) # Idealement parent=task_win_metra (la popup des tâches)
        # Pour que selector_win soit modal à task_win_metra, task_win_metra doit être passée en argument
        # à _open_predecessor_selector si cette dernière est une méthode de classe, ou selector_win doit
        # être enfant de task_win_metra (Toplevel(task_win_metra))

        selector_win.title(f"Prédécesseurs pour {current_task_actual_name_raw or 'Tâche'}")
        selector_win.geometry("350x400")
        selector_win.configure(bg=BG_COLOR)
        selector_win.grab_set()

        ttk.Label(selector_win, text="Sélectionnez les prédécesseurs:", background=BG_COLOR).pack(pady=10)

        listbox_frame = ttk.Frame(selector_win)
        listbox_frame.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        
        pred_listbox = tk.Listbox(listbox_frame, selectmode=tk.MULTIPLE, exportselection=False, bg="white", fg=TEXT_COLOR)
        pred_scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=pred_listbox.yview)
        pred_listbox.config(yscrollcommand=pred_scrollbar.set)

        pred_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        pred_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for name in available_task_names:
            pred_listbox.insert(tk.END, name)

        # Pré-sélectionner les prédécesseurs déjà choisis (ceux dans current_task_pred_label)
        current_preds_str = current_task_pred_label.cget("text")
        if current_preds_str and current_preds_str != "Aucun":
            current_selected_preds = [p.strip() for p in current_preds_str.split(',')]
            for i, item_in_listbox in enumerate(pred_listbox.get(0, tk.END)):
                if item_in_listbox in current_selected_preds:
                    pred_listbox.select_set(i)

        selected_predecessors_names = [] # Variable pour stocker la sélection

        def on_confirm_selection():
            selected_indices = pred_listbox.curselection()
            nonlocal selected_predecessors_names # Réfère à la variable dans la portée externe de on_confirm
            selected_predecessors_names.clear() # Vider pour la nouvelle sélection
            for index in selected_indices:
                selected_predecessors_names.append(pred_listbox.get(index))
            
            if selected_predecessors_names:
                current_task_pred_label.config(text=", ".join(selected_predecessors_names))
            else:
                current_task_pred_label.config(text="Aucun")
            
            # Stocker dans une variable "cachée" associée au widget du label ou à l'entrée de tâche
            # pour une récupération facile lors de la soumission finale.
            # Par exemple, en utilisant setattr sur le widget label ou une clé dans entry_dict.
            # Pour cet exemple, on assume que submit_tasks_mpm_action lira le label.
            # Une meilleure approche est d'avoir une var de données par tâche :
            # entry_dict_metra['selected_preds_list'] = selected_predecessors_names
            # Pour cela, _open_predecessor_selector aurait besoin de entry_dict_metra.

            selector_win.destroy()

        def on_cancel_selection():
            selector_win.destroy()

        btn_frame_selector = ttk.Frame(selector_win)
        btn_frame_selector.pack(pady=10)
        ttk.Button(btn_frame_selector, text="Valider", command=on_confirm_selection).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame_selector, text="Annuler", command=on_cancel_selection).pack(side=tk.RIGHT, padx=5)

    def show_input_window(self, algo_key):
        if self.input_win and self.input_win.winfo_exists():
            self.input_win.destroy()
            
        self.input_win = tk.Toplevel()
        self.input_win.title(f"🔧 {algo_key.capitalize()}")
        self.input_win.geometry("1200x900") # Peut nécessiter plus de largeur
        self.input_win.configure(bg=BG_COLOR)
        self.input_win.grab_set()
        self.current_algo_data = {}
        
        self.input_win.protocol("WM_DELETE_WINDOW", lambda: self.close_window(self.input_win))

        header_frame = ttk.Frame(self.input_win)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(header_frame, 
                 text=f"⚙️ {algo_key.capitalize()}", 
                 font=("Arial", 16, "bold"), 
                 foreground=PRIMARY_COLOR,
                 background=BG_COLOR).pack(side=tk.LEFT, padx=10)
        
        action_frame = ttk.Frame(header_frame)
        action_frame.pack(side=tk.RIGHT, padx=10)
        
        back_btn = ttk.Button(
            action_frame, 
            text="⬅️ Retour",
            command=lambda: self.back_to_algo_selection()
        )
        back_btn.grid(row=0, column=0, padx=5)
        
        quit_btn = ttk.Button(
            action_frame, 
            text="🚪 Quitter",
            command=self.on_closing
        )
        quit_btn.grid(row=0, column=1, padx=5)

        main_container = ttk.Frame(self.input_win)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        param_frame = ttk.LabelFrame(main_container, text="Paramètres", padding=10)
        param_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.input_vars = {}
        placeholders = {
            "welsh": [("Nombre de sommets", "e.g. 5")],
            "kruskal": [("Nombre de sommets", "e.g. 6")],
            "dijkstra": [("Nombre de sommets", "e.g. 6"), ("Noeud source", "e.g. A"),("Noeud destination (optionnel)", "e.g. F")],
            "bellman": [("Nombre de sommets", "e.g. 6"), ("Noeud source", "e.g. A"),("Noeud destination (optionnel)", "e.g. F")],
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
            
            ttk.Label(frame, text=label_text, width=25, anchor="w").pack(side=tk.LEFT, padx=5)
            var = tk.StringVar()
            self.input_vars[label_text] = var
            entry = ttk.Entry(frame, textvariable=var, width=20)
            entry.insert(0, placeholder)
            entry.bind("<FocusIn>", lambda e, p=placeholder: e.widget.delete(0, tk.END) if e.widget.get() == p else None)
            entry.bind("<FocusOut>", lambda e, p=placeholder: e.widget.insert(0, p) if not e.widget.get() else None)
            entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
        # Frame pour les boutons et l'affichage du taux de connexité
        btn_and_rate_frame = ttk.Frame(param_frame)
        btn_and_rate_frame.pack(fill=tk.X, pady=(10,5))
        
        run_btn = ttk.Button(
            btn_and_rate_frame, 
            text="▶️ Exécuter l'algorithme", 
            width=20,
            command=lambda: self.run_algorithm(algo_key)
        )
        run_btn.pack(side=tk.LEFT, padx=5)


        self.rate_btn = ttk.Button(
            btn_and_rate_frame, 
            text="📊 Taux Connexité",
            width=18, 
            state="disabled",
            command=self.show_connexity_rate_display # Changé pour gérer l'affichage
        )
        self.rate_btn.pack(side=tk.LEFT, padx=(5,0))

        # Frame pour l'affichage du taux de connexité (directement à droite du bouton)
        # elle est DANS btn_and_rate_frame
        self.connexity_display_frame = ttk.Frame(btn_and_rate_frame) 
        # self.connexity_display_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5,0))

        self.connexity_rate_label = ttk.Label(self.connexity_display_frame, text="N/A", font=("Arial", 10))
        self.connexity_rate_label.pack(side=tk.LEFT, padx=(0,5))
        self.connexity_progress = ttk.Progressbar(
            self.connexity_display_frame, 
            orient="horizontal", 
            length=200,
            mode="determinate",
            style="Connexity.Horizontal.TProgressbar"
        )
        self.connexity_progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.connexity_progress['value'] = 0

        self.connexity_display_frame.pack_forget() 


        result_frame = ttk.LabelFrame(main_container, text="Résultats", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.notebook = ttk.Notebook(result_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.graph_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.graph_tab, text="Visualisation")
        
        self.text_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.text_tab, text="Résultat Texte")
        
        self.text_box = tk.Text(self.text_tab, wrap=tk.WORD, font=("Courier", 10))
        self.text_scroll = ttk.Scrollbar(self.text_tab, command=self.text_box.yview)
        self.text_box.config(yscrollcommand=self.text_scroll.set)
        
        self.text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_box.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.text_box.config(state="disabled")
        
        self.graph_container = ttk.Frame(self.graph_tab)
        self.graph_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.display_graph()

    

    def animate_connexity_rate(self, progress_bar, label, target_value, current=0, step=1):
        if current >= target_value:
            progress_bar['value'] = target_value
            label.config(text=f"{target_value:.2f}%") # Juste le pourcentage pour la concision
            return
        current += step
        if current > target_value:
            current = target_value
        progress_bar['value'] = current
        label.config(text=f"{current:.2f}%")
        if self.input_win and self.input_win.winfo_exists() and progress_bar.winfo_exists():
             self.input_win.after(10, self.animate_connexity_rate, progress_bar, label, target_value, current, step)


    def show_connexity_rate_display(self):
        """Affiche/Cache la frame de connexité et lance l'animation si des données existent."""
        if 'connexity_rate' not in self.current_algo_data:
            # Si pas de données, s'assurer que c'est caché (même si le bouton devrait être désactivé)
            if hasattr(self, 'connexity_display_frame') and self.connexity_display_frame.winfo_ismapped():
                self.connexity_display_frame.pack_forget()
            return
        
        rate = self.current_algo_data['connexity_rate']
        
        if not (hasattr(self, 'connexity_display_frame') and \
                hasattr(self, 'connexity_progress') and \
                hasattr(self, 'connexity_rate_label')):
            messagebox.showerror("Erreur UI", "Composants UI pour connexité manquants.")
            return
        
        # Si la frame est actuellement cachée, l'afficher
        if not self.connexity_display_frame.winfo_ismapped():
            self.connexity_display_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5,0))
        # Si elle est déjà visible, on ne la repack pas, on lance juste l'animation

        self.connexity_progress['value'] = 0
        self.connexity_rate_label.config(text="0.00%")
        
        self.animate_connexity_rate(self.connexity_progress, self.connexity_rate_label, rate)


    def display_graph(self, new_fig=None):
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
        self.notebook.select(1)

    def reset_transport_entries(self, cout_entries, offre_entries, demande_entries):
        for row in cout_entries:
            for entry in row:
                entry.delete(0, tk.END)
                entry.insert(0, "0")
        for entry in offre_entries:
            entry.delete(0, tk.END)
            entry.insert(0, "0")
        for entry in demande_entries:
            entry.delete(0, tk.END)
            entry.insert(0, "0")

    def _validate_positive_integer_revised(self, label_text_key, descriptive_name, min_value=1):
        input_str = self.input_vars[label_text_key].get().strip()
        
        if not input_str:
            message = f"Le champ '{descriptive_name}' est requis."
            messagebox.showerror("Saisie manquante", message, parent=self.input_win if self.input_win and self.input_win.winfo_exists() else None)
            self.display_text(f"Erreur : {message}")
            self.display_graph(None)
            return None
        
        try:
            value = int(input_str)
            if value < min_value:
                message = f"'{descriptive_name}' doit être un entier >= {min_value}."
                messagebox.showerror("Valeur invalide", message, parent=self.input_win if self.input_win and self.input_win.winfo_exists() else None)
                self.display_text(f"Erreur : {message}")
                self.display_graph(None)
                return None
            return value
        except ValueError:
            if any(char.isalpha() for char in input_str) or "." in input_str or input_str.startswith("e.g.") :
                 message = f"Le champ '{descriptive_name}' est requis (ne pas laisser le texte d'exemple '{input_str}')."
            else:
                 message = f"'{descriptive_name}' doit être un nombre entier valide (pas '{input_str}')."
            messagebox.showerror("Format invalide", message, parent=self.input_win if self.input_win and self.input_win.winfo_exists() else None)
            self.display_text(f"Erreur : {message}")
            self.display_graph(None)
            return None
        
    

    def run_algorithm(self, algo_key):
        try:
            self.current_algo_data = {}
            fig = None
            result_text = ""
            
            if hasattr(self, 'rate_btn') and self.rate_btn.winfo_exists():
                self.rate_btn.config(state="disabled")
            if hasattr(self, 'connexity_display_frame') and self.connexity_display_frame.winfo_exists():
                self.connexity_display_frame.pack_forget() # Cacher la frame
            if hasattr(self, 'connexity_progress') and self.connexity_progress.winfo_exists():
                self.connexity_progress['value'] = 0
            if hasattr(self, 'connexity_rate_label') and self.connexity_rate_label.winfo_exists():
                self.connexity_rate_label.config(text="N/A")
            
            if algo_key == "welsh":
                nb = self._validate_positive_integer_revised("Nombre de sommets", "Nombre de sommets")
                if nb is None: return
    
                graph, graph_couleur, densite = algos.welsh.welsh(nb)
                result_text = str(graph_couleur)
    
                fig = Figure(figsize=(10, 6), dpi=100)
                ax = fig.add_subplot(111)
                G = nx.Graph()
                for node in graph: G.add_node(node)
                for node, voisins in graph.items():
                    for voisin, _ in voisins:
                        if not G.has_edge(node, voisin): G.add_edge(node, voisin)
                pos = nx.spring_layout(G, seed=42)
                node_colors = [graph_couleur[node] for node in G.nodes()]
                nx.draw(G, pos, with_labels=True, node_color=node_colors, ax=ax, node_size=600, font_size=10)
                taux_str = f"{round(densite * 100, 2)}%"
                ax.set_title(f"Coloration du graphe (Welsh-Powell)\nTaux de connexité : {taux_str}")
    
                self.display_graph(fig)
                self.display_text(result_text)
                
                self.current_algo_data['connexity_rate'] = densite * 100
                if hasattr(self, 'rate_btn') and self.rate_btn.winfo_exists(): # S'assurer que le bouton existe
                    self.rate_btn.config(state="normal")
                
            elif algo_key == "kruskal":
                nb = self._validate_positive_integer_revised("Nombre de sommets", "Nombre de sommets")
                if nb is None: return

                total_weight, mst, G, densite = algos.kruskal.kruskal(nb)
                result_text = (
                    f"Poids total de l'arbre couvrant minimal : {total_weight}\n"
                    f"Taux de connexité du graphe généré : {densite:.2%}" # densite is already percentage
                )
                fig = Figure(figsize=(8, 6), dpi=100)
                ax = fig.add_subplot(111)
                pos = nx.spring_layout(G, seed=42)
                nx.draw(
                    G, pos, with_labels=True,
                    node_color="lightblue", edge_color="gray",
                    width=1, node_size=500, ax=ax
                )
                nx.draw_networkx_edges(G, pos, edgelist=mst.edges(), edge_color="red", width=2, ax=ax)
                edge_labels = nx.get_edge_attributes(G, 'weight')
                nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax)
                red_line = Line2D([], [], color='red', linewidth=2, label=f"Arbre couvrant minimal : {total_weight}")
                ax.legend(handles=[red_line], loc="upper right")
                ax.set_title(f"Arbre couvrant minimal - Kruskal\nTaux de connexité : {densite:.2%}")
                self.display_graph(fig)
                self.display_text(result_text)
                
                self.current_algo_data['connexity_rate'] = densite * 100
                if hasattr(self, 'rate_btn') and self.rate_btn.winfo_exists(): # S'assurer que le bouton existe
                    self.rate_btn.config(state="normal")
            elif algo_key == "dijkstra":
                nb = self._validate_positive_integer_revised("Nombre de sommets", "Nombre de sommets")
                if nb is None: return

                src_str = self.input_vars["Noeud source"].get().strip()
                # Improved placeholder check for "Noeud source"
                placeholder_src = "e.g. A" # This should be fetched more dynamically if placeholders change
                if not src_str or src_str == placeholder_src:
                    messagebox.showerror("Saisie manquante", "Le 'Noeud source' est requis.", parent=self.input_win)
                    self.display_text("Erreur : Le 'Noeud source' est requis.")
                    self.display_graph(None)
                    return
                src = src_str.upper()

                # Improved placeholder check for "Noeud destination (optionnel)"
                tgt_raw = self.input_vars["Noeud destination (optionnel)"].get().strip().upper()
                placeholder_tgt = "E.G. F" # This should be fetched more dynamically
                if tgt_raw == placeholder_tgt or tgt_raw == "E.G. F": # Add other common variants if necessary
                    tgt_raw = "" 
                tgt = tgt_raw if tgt_raw else None

                dist, chemins, G, densite, chemin_source_target, texte_resultat = algos.dijkstra.dijkstra(nb, src, tgt)
                result_text = "🗺️ Cas d'utilisation : Recherche du chemin le plus court\n\n" + texte_resultat
                fig = Figure(figsize=(12, 8), dpi=100)
                ax = fig.add_subplot(111)
                pos = nx.spring_layout(G, seed=42)
                node_colors = ["orange" if n == src else "lightgreen" if n == tgt else "lightblue" for n in G.nodes()]
                nx.draw(G, pos, with_labels=False, node_color=node_colors, node_size=700, edge_color='gray', ax=ax)
                edge_labels = nx.get_edge_attributes(G, 'weight')
                nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax)
                new_labels = {node: f"{node}\n({dist[node] if dist[node] != float('inf') else '∞'})" for node in G.nodes()}
                nx.draw_networkx_labels(G, pos, labels=new_labels, font_size=10, ax=ax)
                
                legend_handles = []
                if tgt and chemin_source_target: 
                    nx.draw_networkx_edges(G, pos, edgelist=chemin_source_target, edge_color="red", width=3, ax=ax)
                    handle = mlines.Line2D([], [], color="red", label=f"{src} → {tgt} = {dist[tgt]} (ARRIVEE)", linewidth=3)
                    legend_handles.append(handle)
                else: 
                    all_targets_display = sorted(k for k, p in chemins.items() if p and dist[k] != float('inf') and k != src) # Paths that exist, are reachable, and not to source itself
                    colors_multi = plt.cm.tab10(np.linspace(0, 1, len(all_targets_display))) if all_targets_display else []
                    for i, target_node_disp in enumerate(all_targets_display):
                        path_edges = chemins[target_node_disp]
                        # Color should be based on whether it's the specific target (if one was given but maybe not found by chemin_source_target)
                        if colors_multi is not None and colors_multi.size > 0: 
                            color_disp = "red" if (target_node_disp == tgt and tgt is not None) else colors_multi[i % len(colors_multi)]
                        else:
                            color_disp = "blue" # Fallback si colors_multi est vide ou None
                        label = f"{src} → {target_node_disp} = {dist[target_node_disp]}" + (" (ARRIVEE)" if (target_node_disp == tgt and tgt is not None) else "")
                        nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color=[color_disp], width=2.5, ax=ax)
                        handle = mlines.Line2D([], [], color=color_disp, label=label, linewidth=2.5)
                        legend_handles.append(handle)

                if legend_handles:
                    ax.legend(handles=legend_handles, title="Chemins les plus courts", bbox_to_anchor=(0, 1.10), fontsize=9, title_fontsize=10, frameon=True)
                ax.set_title(f"Dijkstra depuis {src}\nTaux de connexité : {densite:.2f}%", fontsize=14, pad=20) # densite is 0-100
                ax.axis('off')
                self.display_graph(fig)
                self.display_text(result_text)
                
                self.current_algo_data['connexity_rate'] = densite
                if hasattr(self, 'rate_btn') and self.rate_btn.winfo_exists(): # S'assurer que le bouton existe
                    self.rate_btn.config(state="normal")

            elif algo_key == "bellman":
                nb = self._validate_positive_integer_revised("Nombre de sommets", "Nombre de sommets")
                if nb is None: return

                src_bellman_str = self.input_vars["Noeud source"].get().strip()
                placeholder_src_b = "e.g. A"
                if not src_bellman_str or src_bellman_str == placeholder_src_b:
                    messagebox.showerror("Saisie manquante", "Le 'Noeud source' pour Bellman-Ford est requis.", parent=self.input_win)
                    self.display_text("Erreur : Le 'Noeud source' pour Bellman-Ford est requis.")
                    self.display_graph(None)
                    return
                src_bellman = src_bellman_str.upper()
                
                dest_bellman_raw = self.input_vars["Noeud destination (optionnel)"].get().strip().upper()
                placeholder_tgt_b = "E.G. F OU VIDE"
                if dest_bellman_raw == placeholder_tgt_b or dest_bellman_raw == "E.G. F": 
                    dest_bellman_raw = ""
                dest_bellman = dest_bellman_raw if dest_bellman_raw else None
                
                result_text_bellman, distances_bellman, G_bellman, path_to_dest_edges, conn_rate_bellman = \
                    algos.bellmanford.bellman_ford_graph(nb, src_bellman, dest_bellman)
                if G_bellman: # conn_rate_bellman is 0-100
                     result_text_bellman += f"\nTaux de connexité généré : {conn_rate_bellman:.2f}%" 

                fig = Figure(figsize=(12, 9), dpi=100)
                ax = fig.add_subplot(111)
                if G_bellman is None or not G_bellman.nodes():
                    ax.text(0.5, 0.5, "Impossible de générer le graphe ou graphe vide.\n" + result_text_bellman.split('\n')[0], 
                            ha='center', va='center', color='red', fontsize=12)
                    ax.axis('off')
                else:
                    k_layout = 0.9 / np.sqrt(G_bellman.number_of_nodes()) if G_bellman.number_of_nodes() > 0 else 0.9
                    pos_bellman = nx.spring_layout(G_bellman, seed=30, k=k_layout, iterations=35)
                    node_colors_list_bellman = []
                    for node_item_bf in G_bellman.nodes():
                        if node_item_bf == src_bellman: node_colors_list_bellman.append('orange')
                        elif node_item_bf == dest_bellman: node_colors_list_bellman.append('lightgreen')
                        else: node_colors_list_bellman.append('skyblue')
                    nx.draw_networkx_nodes(G_bellman, pos_bellman, node_color=node_colors_list_bellman, node_size=750, ax=ax, edgecolors='dimgray', linewidths=0.5)
                    labels_for_nodes_bf = {node_label_bf: f"{node_label_bf}\n({distances_bellman.get(node_label_bf, '∞')})" for node_label_bf in G_bellman.nodes()}
                    nx.draw_networkx_labels(G_bellman, pos_bellman, labels=labels_for_nodes_bf, font_size=9, font_weight='bold', ax=ax)
                    nx.draw_networkx_edges(G_bellman, pos_bellman, edge_color='gray', width=1.0, alpha=0.6, arrows=True, arrowstyle='-|>', arrowsize=25, connectionstyle='arc3,rad=0.1', ax=ax)
                    edge_weights_labels_bf = nx.get_edge_attributes(G_bellman, 'weight')
                    nx.draw_networkx_edge_labels(G_bellman, pos_bellman, edge_labels=edge_weights_labels_bf, font_size=8, font_color='black', ax=ax, bbox=dict(facecolor='white', alpha=0.4, edgecolor='none', pad=0))
                    legend_handles_bf = []
                    if dest_bellman and path_to_dest_edges:
                        nx.draw_networkx_edges(G_bellman, pos_bellman, edgelist=path_to_dest_edges, edge_color='red', width=2.5, arrows=True, arrowstyle='-|>', arrowsize=20, connectionstyle='arc3,rad=0.1', ax=ax, label=f"Chemin {src_bellman} → {dest_bellman}")
                        dist_to_dest_val = distances_bellman.get(dest_bellman, '∞')
                        path_legend_label = f"{src_bellman} → {dest_bellman} (Coût: {dist_to_dest_val})"
                        handle = mlines.Line2D([], [], color='red', label=path_legend_label, linewidth=2.5)
                        legend_handles_bf.append(handle)
                    if legend_handles_bf:
                        ax.legend(handles=legend_handles_bf, title="Chemin vers Destination", loc='upper left', bbox_to_anchor=(0, 1.10), fontsize=9, title_fontsize=10, frameon=True, facecolor='whitesmoke', edgecolor='lightgray')
                    title_str_bf = f"Bellman-Ford depuis {src_bellman}"
                    if dest_bellman: title_str_bf += f" vers {dest_bellman}"
                    title_str_bf += f"\nTaux de connexité : {conn_rate_bellman:.2f}%" # Already percent
                    ax.set_title(title_str_bf, fontsize=14, pad=20)
                    if "cycle négatif" in result_text_bellman.lower():
                        ax.text(0.5, -0.05, "Attention : Cycle négatif détecté !", color="red", ha="center", va="top", transform=ax.transAxes, fontsize=12, fontweight='bold', bbox=dict(facecolor='white', alpha=0.8, edgecolor='red', boxstyle='round,pad=0.3'))
                ax.axis('off')
                plt.tight_layout(rect=[0, 0.03, 1, 0.95])
                self.display_graph(fig)
                self.display_text(result_text_bellman)
                
                self.current_algo_data['connexity_rate'] = conn_rate_bellman
                if hasattr(self, 'rate_btn') and self.rate_btn.winfo_exists(): # S'assurer que le bouton existe
                    self.rate_btn.config(state="normal")
                
            elif algo_key == "ford":
                nb_ff = self._validate_positive_integer_revised("Nombre de sommets", "Nombre de sommets", min_value=2)
                if nb_ff is None: return

                source_ff_name_str = self.input_vars["Noeud source"].get().strip()
                placeholder_src_ff = "e.g. A"
                if not source_ff_name_str or source_ff_name_str == placeholder_src_ff:
                    messagebox.showerror("Saisie manquante", "Le 'Noeud source' pour Ford-Fulkerson est requis.", parent=self.input_win)
                    self.display_text("Erreur : Le 'Noeud source' pour Ford-Fulkerson est requis.")
                    self.display_graph(None)
                    return
                source_ff_name = source_ff_name_str.upper()

                sink_ff_name_str = self.input_vars["Noeud puits"].get().strip()
                placeholder_sink_ff = "e.g. F"
                if not sink_ff_name_str or sink_ff_name_str == placeholder_sink_ff:
                    messagebox.showerror("Saisie manquante", "Le 'Noeud puits' pour Ford-Fulkerson est requis.", parent=self.input_win)
                    self.display_text("Erreur : Le 'Noeud puits' pour Ford-Fulkerson est requis.")
                    self.display_graph(None)
                    return
                sink_ff_name = sink_ff_name_str.upper()

                if source_ff_name == sink_ff_name:
                    messagebox.showerror("Valeur invalide", "Le Noeud source et le Noeud puits ne peuvent pas être identiques.", parent=self.input_win)
                    self.display_text("Erreur : Noeud source et Noeud puits sont identiques.")
                    self.display_graph(None)
                    return
                
                try:
                    max_flow_val, min_cut_edges_set, G_ff_graph, conn_rate_ff = \
                        algos.ford.ford_fulkerson(nb_ff, source_ff_name, sink_ff_name)
                except ValueError as ve: 
                    messagebox.showerror("Erreur de configuration", str(ve), parent=self.input_win)
                    self.display_text(f"Erreur de configuration : {str(ve)}")
                    self.display_graph(None)
                    return
                except RuntimeError as re_ff: 
                    messagebox.showerror("Erreur d'exécution", str(re_ff), parent=self.input_win)
                    self.display_text(f"Erreur d'exécution Ford-Fulkerson : {str(re_ff)}")
                    self.display_graph(None)
                    return

                result_text_ff_str = f"📶 Cas d'utilisation : Calcul du débit maximal (Ford-Fulkerson)\n\n"
                result_text_ff_str += f"Flux maximal de {source_ff_name} à {sink_ff_name} : {max_flow_val}\n"
                result_text_ff_str += f"Arêtes dans la coupe minimale ({len(min_cut_edges_set)}) : {min_cut_edges_set if min_cut_edges_set else 'N/A (ou flux nul)'}\n"
                result_text_ff_str += f"Taux de connexité généré : {conn_rate_ff:.2f}%" # conn_rate_ff is 0-100
                
                fig = Figure(figsize=(11, 8), dpi=100)
                ax = fig.add_subplot(111)
                if G_ff_graph is None or not G_ff_graph.nodes():
                     ax.text(0.5, 0.5, "Impossible de générer le graphe.", ha='center', va='center', color='red')
                else:
                    k_layout_ff = 0.9 / np.sqrt(G_ff_graph.number_of_nodes()) if G_ff_graph.number_of_nodes() > 0 else 0.9
                    pos_ff_layout = nx.spring_layout(G_ff_graph, seed=42, k=k_layout_ff, iterations=30)
                    node_colors_ff_list = []
                    for n_ff_node in G_ff_graph.nodes():
                        if n_ff_node == source_ff_name: node_colors_ff_list.append('lightgreen')
                        elif n_ff_node == sink_ff_name: node_colors_ff_list.append('tomato')
                        else: node_colors_ff_list.append('skyblue')
                    nx.draw_networkx_nodes(G_ff_graph, pos_ff_layout, node_color=node_colors_ff_list, node_size=700, ax=ax, edgecolors='dimgray')
                    nx.draw_networkx_labels(G_ff_graph, pos_ff_layout, font_size=10, font_weight='bold', ax=ax)
                    all_edges_ff = list(G_ff_graph.edges())
                    nx.draw_networkx_edges(G_ff_graph, pos_ff_layout, edgelist=all_edges_ff, edge_color='gray', width=1.2, alpha=0.7, arrowsize=18, arrowstyle='-|>', connectionstyle='arc3,rad=0.1', ax=ax)
                    if min_cut_edges_set:
                         nx.draw_networkx_edges(G_ff_graph, pos_ff_layout, edgelist=list(min_cut_edges_set), edge_color='red', style='dashed', width=2.2, arrowsize=18, arrowstyle='-|>', connectionstyle='arc3,rad=0.1', ax=ax)
                    edge_labels_ff_dict = {(u, v): f"{d.get('capacity', '?')}" for u, v, d in G_ff_graph.edges(data=True)}
                    nx.draw_networkx_edge_labels(G_ff_graph, pos_ff_layout, edge_labels=edge_labels_ff_dict, font_color='black', font_size=9, ax=ax, bbox=dict(facecolor='white', alpha=0.5, edgecolor='none', pad=0.05))
                    legend_elements_ff = [ Line2D([0], [0], marker='o', color='w', label='Source', markerfacecolor='lightgreen', markersize=10), Line2D([0], [0], marker='o', color='w', label='Puits', markerfacecolor='tomato', markersize=10), Line2D([0], [0], color='gray', lw=1.5, label='Arc (Capacité)'), Line2D([0], [0], color='red', lw=2, linestyle='dashed', label='Coupe Minimale')]
                    ax.legend(handles=legend_elements_ff, loc='upper right', fontsize=9, title="Légende", facecolor='whitesmoke')
                    ax.set_title(f"Ford-Fulkerson: Flux Max = {max_flow_val} ({source_ff_name} → {sink_ff_name})\n" f"Taux de connexité : {conn_rate_ff:.2f}%", fontsize=13, pad=15) # Already percent
                ax.axis('off')
                plt.tight_layout(rect=[0, 0, 1, 0.95])
                self.display_graph(fig)
                self.display_text(result_text_ff_str)
                
                self.current_algo_data['connexity_rate'] = conn_rate_ff
                if hasattr(self, 'rate_btn') and self.rate_btn.winfo_exists(): # S'assurer que le bouton existe
                    self.rate_btn.config(state="normal")

            elif algo_key == "metra":
                nb_tasks_metra = self._validate_positive_integer_revised("Nombre de tâches", "Nombre de tâches")
                if nb_tasks_metra is None: return

                task_win_metra = tk.Toplevel(self.input_win) # Fenêtre popup principale des tâches
                task_win_metra.title("Détails des tâches MPM/PERT")
                task_win_metra.geometry("800x600") 
                task_win_metra.configure(bg=BG_COLOR)
                task_win_metra.grab_set()
                
                canvas_frame_mpm_popup = ttk.Frame(task_win_metra) # ...
                # ... (Configuration du canvas et scrollbar comme avant) ...
                canvas_frame_mpm_popup.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
                task_canvas_mpm_popup = tk.Canvas(canvas_frame_mpm_popup, bg=BG_COLOR, highlightthickness=0)
                task_scrollbar_mpm_popup = ttk.Scrollbar(canvas_frame_mpm_popup, orient="vertical", command=task_canvas_mpm_popup.yview)
                scrollable_frame_mpm_popup = ttk.Frame(task_canvas_mpm_popup)
                scrollable_frame_mpm_popup.bind("<Configure>", lambda e: task_canvas_mpm_popup.configure(scrollregion=task_canvas_mpm_popup.bbox("all")))
                task_canvas_mpm_popup.create_window((0, 0), window=scrollable_frame_mpm_popup, anchor="nw")
                task_canvas_mpm_popup.configure(yscrollcommand=task_scrollbar_mpm_popup.set)
                task_canvas_mpm_popup.pack(side="left", fill="both", expand=True)
                task_scrollbar_mpm_popup.pack(side="right", fill="y")
                
                task_entries_metra_list = [] 
                ttk.Label(scrollable_frame_mpm_popup, text="Définissez chaque tâche :", 
                          font=("Arial", 11, "bold"), background=BG_COLOR).pack(pady=(10,5), anchor="w", padx=10)

                for i_metra_task in range(nb_tasks_metra):
                    default_task_name = chr(65 + i_metra_task)
                    frame_metra_entry = ttk.LabelFrame(scrollable_frame_mpm_popup, text=f"Tâche {i_metra_task+1}", padding=10)
                    frame_metra_entry.pack(fill=tk.X, padx=10, pady=(0,5), anchor="w")
                    
                    ttk.Label(frame_metra_entry, text="Nom Tâche:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
                    name_entry_metra_widget = ttk.Entry(frame_metra_entry, width=15) # Renommé pour clarté
                    name_entry_metra_widget.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
                    name_entry_metra_widget.insert(0, default_task_name)

                    ttk.Label(frame_metra_entry, text="Durée:").grid(row=0, column=2, padx=(10,5), pady=2, sticky="w")
                    duree_entry_metra_widget = ttk.Entry(frame_metra_entry, width=8) # Renommé
                    duree_entry_metra_widget.grid(row=0, column=3, padx=5, pady=2)
                    duree_entry_metra_widget.insert(0, "1") 
                    
                    ttk.Label(frame_metra_entry, text="Prédécesseurs:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
                    # Label pour afficher les prédécesseurs sélectionnés
                    pred_display_label = ttk.Label(frame_metra_entry, text="Aucun", width=30, anchor="w", relief="sunken", padding=2)
                    pred_display_label.grid(row=1, column=1, columnspan=2, padx=5, pady=2, sticky="ew")
                    
                    # Bouton pour ouvrir le sélecteur de prédécesseurs
                    # Le lambda a besoin de capturer les widgets spécifiques à CETTE ligne de tâche
                    select_pred_btn = ttk.Button(frame_metra_entry, text="Choisir...", width=10,
                        command=lambda current_name_w=name_entry_metra_widget, current_pred_l=pred_display_label: \
                                self._open_predecessor_selector(current_name_w, current_pred_l, task_entries_metra_list)
                    )
                    select_pred_btn.grid(row=1, column=3, padx=5, pady=2)
                    
                    entry_data = {
                        'id': i_metra_task,
                        'name_entry': name_entry_metra_widget, 
                        'duree_entry': duree_entry_metra_widget, 
                        'pred_display_label': pred_display_label, # Pour lire les prédécesseurs
                        'selected_preds_list': [] # Nouvelle clé pour stocker les noms des prédécesseurs sélectionnés
                    }
                    # Modifier la commande du bouton pour mettre à jour 'selected_preds_list' dans entry_data
                    select_pred_btn.config(
                         command=lambda current_name_w=name_entry_metra_widget, 
                                        current_pred_l=pred_display_label, 
                                        current_entry_data=entry_data: \
                                self._open_predecessor_selector_v2(current_name_w, current_pred_l, task_entries_metra_list, current_entry_data, task_win_metra)
                    )
                    task_entries_metra_list.append(entry_data)
                
                def submit_tasks_mpm_action():
                    try:
                        taches_input_for_algo = {} 
                        defined_task_names = [] 

                        # Première passe : valider noms et durées
                        for entry_dict in task_entries_metra_list: # Correction ici: task_entries_metra_list
                            task_name_widget = entry_dict['name_entry']
                            duree_widget = entry_dict['duree_entry']

                            task_name = task_name_widget.get().strip().upper()
                            duree_str = duree_widget.get().strip()

                            if not task_name:
                                messagebox.showerror("Erreur MPM", f"Le nom de la tâche {entry_dict['id']+1} est vide.", parent=task_win_metra); task_name_widget.focus_set(); return
                            if not re.match(r"^[A-Z0-9_.-]+$", task_name):
                                messagebox.showerror("Erreur MPM", f"Nom tâche '{task_name}' invalide (lettres A-Z, chiffres 0-9, _, ., -).", parent=task_win_metra); task_name_widget.focus_set(); return
                            if task_name in ["DÉBUT", "DEBUT", "FIN"]:
                                messagebox.showerror("Erreur MPM", f"Nom tâche '{task_name}' est réservé.", parent=task_win_metra); task_name_widget.focus_set(); return
                            if task_name in defined_task_names:
                                messagebox.showerror("Erreur MPM", f"Nom tâche '{task_name}' dupliqué.", parent=task_win_metra); task_name_widget.focus_set(); return
                            
                            defined_task_names.append(task_name)

                            if not duree_str:
                                messagebox.showerror("Erreur MPM", f"Tâche '{task_name}': Durée manquante.", parent=task_win_metra); duree_widget.focus_set(); return
                            try:
                                duree = int(duree_str)
                                if duree <= 0:
                                    messagebox.showerror("Erreur MPM", f"Tâche '{task_name}': Durée doit être > 0.", parent=task_win_metra); duree_widget.focus_set(); return
                            except ValueError:
                                messagebox.showerror("Erreur MPM", f"Tâche '{task_name}': Durée '{duree_str}' invalide.", parent=task_win_metra); duree_widget.focus_set(); return
                            
                            taches_input_for_algo[task_name] = {'duree': duree, 'pred': []}

                        # Deuxième passe : traiter les prédécesseurs sélectionnés
                        for entry_dict in task_entries_metra_list: # Correction ici: task_entries_metra_list
                            current_task_name = entry_dict['name_entry'].get().strip().upper()
                            selected_preds_for_task = entry_dict['selected_preds_list'] 

                            for pred_name in selected_preds_for_task:
                                if pred_name not in defined_task_names:
                                    messagebox.showerror("Erreur MPM", f"Tâche '{current_task_name}': Prédécesseur '{pred_name}' (sélectionné) non valide.", parent=task_win_metra); return
                                if pred_name == current_task_name: # Déjà validé mais double check
                                    messagebox.showerror("Erreur MPM", f"Tâche '{current_task_name}': Auto-prédécesseur.", parent=task_win_metra); return
                                taches_input_for_algo[current_task_name]['pred'].append(pred_name)
                        
                        if not taches_input_for_algo:
                            messagebox.showinfo("Info MPM", "Aucune tâche valide à traiter.", parent=task_win_metra)
                            if task_win_metra and task_win_metra.winfo_exists(): task_win_metra.destroy()
                            return

                        taches_data_mpm_result, fig_mpm_generated = algos.mpm.algo_potentiel_metra(taches_input_for_algo, afficher_console=False) # afficher_console=False est déjà là

                        # --- SECTION CRITIQUE POUR LE RÉSULTAT TEXTUEL ---
                        text_result_mpm_display = "📅 Planification de projets (MPM)\n\n" # Titre plus général
                        
                        # Déterminer la largeur maximale nécessaire pour les noms de tâches
                        max_name_len = 0
                        if taches_data_mpm_result: # S'assurer que le dictionnaire n'est pas vide
                            max_name_len = max(len(name) for name in taches_data_mpm_result.keys())
                        max_name_len = max(max_name_len, len("Tâche")) # S'assurer que le header "Tâche" rentre
                        max_name_len = min(max_name_len, 25) # Limiter la largeur pour éviter des tableaux trop larges

                        header_format = "{:<{width}} | {:<12} | {:<10} | {:<13} | {:<11} | {:<5} | {:<8}\n"
                        row_format =    "{:<{width}} | {:<12} | {:<10} | {:<13.1f} | {:<11.1f} | {:<5.1f} | {:<8}\n" # .1f pour les floats
                        inf_row_format = "{:<{width}} | {:<12} | {:<10} | {:<13} | {:<11} | {:<5} | {:<8}\n" # Pour les '∞'

                        text_result_mpm_display += header_format.format(
                            "Tâche", "TOT", "TFT", "TARD", "TFTARD", "Marge", "Critique", width=max_name_len)
                        
                        # Calculer la longueur de la ligne de séparation dynamiquement
                        # Somme des largeurs + nombre de séparateurs * 3 (pour " | ")
                        separator_len = max_name_len + 12 + 10 + 13 + 11 + 5 + 8 + (6 * 3) 
                        text_result_mpm_display += "-" * separator_len + "\n"
                        
                        user_task_keys_sorted = sorted([k for k in taches_data_mpm_result if k not in ['Début', 'Fin']])
                        
                        display_order_keys = []
                        # S'assurer que 'Début' et 'Fin' existent dans le résultat avant de les ajouter
                        if 'Début' in taches_data_mpm_result: display_order_keys.append('Début')
                        display_order_keys.extend(user_task_keys_sorted)
                        if 'Fin' in taches_data_mpm_result: display_order_keys.append('Fin')
                        
                        for t_key_disp in display_order_keys:
                            data_disp = taches_data_mpm_result.get(t_key_disp)
                            if not data_disp: continue # Au cas où une clé est manquante

                            crit_disp = "Oui" if data_disp.get('marge', float('inf')) == 0 else "Non"
                            
                            # Gestion des valeurs potentiellement infinies pour l'affichage
                            tot_str = f"{data_disp.get('tot', 0):.1f}"
                            tft_str = f"{data_disp.get('tft', 0):.1f}"
                            tard_val = data_disp.get('tard', float('inf'))
                            tftard_val = data_disp.get('tftard', float('inf'))
                            marge_val = data_disp.get('marge', float('inf'))

                            tard_str = f"{tard_val:.1f}" if tard_val != float('inf') else '∞'
                            tftard_str = f"{tftard_val:.1f}" if tftard_val != float('inf') else '∞'
                            marge_str = f"{marge_val:.1f}" if marge_val != float('inf') else '∞'
                            
                            # Utiliser un format de ligne différent si des infinis sont présents pour éviter erreur de formatage avec .1f
                            current_row_format = row_format
                            if '∞' in [tard_str, tftard_str, marge_str]:
                                current_row_format = inf_row_format
                                # Remplacer les valeurs float par les chaines avec infini pour inf_row_format
                                # Cela suppose que inf_row_format attend des chaines pour ces champs
                                tot_disp_final = tot_str 
                                tft_disp_final = tft_str
                                tard_disp_final = tard_str
                                tftard_disp_final = tftard_str
                                marge_disp_final = marge_str
                                text_result_mpm_display += current_row_format.format(
                                    t_key_disp, 
                                    tot_disp_final, tft_disp_final, 
                                    tard_disp_final, tftard_disp_final, 
                                    marge_disp_final, crit_disp, width=max_name_len)
                            else:
                                # Les valeurs sont des nombres, on peut les formatter avec .1f
                                text_result_mpm_display += current_row_format.format(
                                    t_key_disp, 
                                    data_disp.get('tot',0), data_disp.get('tft',0), 
                                    tard_val, tftard_val, 
                                    marge_val, crit_disp, width=max_name_len)

                        dur_proj_val = taches_data_mpm_result.get('Fin', {}).get('tft', None)
                        if dur_proj_val is not None: 
                            text_result_mpm_display += f"\nDurée totale projet : {dur_proj_val:.1f}\n"
                        
                        # --- Logique pour afficher le(s) chemin(s) critique(s) ---
                        # (Cette partie dépend de la structure exacte de temp_g_check ou cp_graph_viz_mpm dans la version précédente)
                        # Pour l'instant, je vais simplifier en affichant juste les tâches critiques.
                        critical_tasks_list_str = [name for name, data in taches_data_mpm_result.items() 
                                                   if data.get('marge', float('inf')) == 0 and name not in ['Début', 'Fin']]
                        if critical_tasks_list_str:
                             text_result_mpm_display += f"\nTâches sur le chemin critique (hors Début/Fin) : {', '.join(critical_tasks_list_str)}\n"
                        elif dur_proj_val is not None and dur_proj_val > 0 and taches_data_mpm_result.get('Début',{}).get('marge',1)==0:
                             text_result_mpm_display += "\nLe projet est critique, mais aucune tâche intermédiaire spécifique n'est sur un chemin critique simple, ou la durée est nulle.\n"

                        # --- Fin de la section critique pour le résultat textuel ---

                        self.display_graph(fig_mpm_generated)
                        self.display_text(text_result_mpm_display)
                        if task_win_metra and task_win_metra.winfo_exists(): task_win_metra.destroy()
                    except Exception as e_submit_metra:
                        # ... (Gestion d'exception)
                        pass # (déjà dans votre code)
                
                # Boutons Valider/Annuler pour la fenêtre task_win_metra
                btn_container_submit_all_mpm = ttk.Frame(task_win_metra) 
                btn_container_submit_all_mpm.pack(fill=tk.X,padx=10,pady=10,side=tk.BOTTOM)
                ttk.Button(btn_container_submit_all_mpm, text="✅ Valider Toutes les Tâches", command=submit_tasks_mpm_action).pack(side=tk.LEFT, padx=5)
                ttk.Button(btn_container_submit_all_mpm, text="❌ Annuler Saisie MPM", command=task_win_metra.destroy).pack(side=tk.RIGHT, padx=5)
            
            elif algo_key == "nordouest" or algo_key == "cout":
                n_usines = self._validate_positive_integer_revised("Nombre d'usines", "Nombre d'usines")
                if n_usines is None: return
                n_magasins = self._validate_positive_integer_revised("Nombre de magasins", "Nombre de magasins")
                if n_magasins is None: return
                
                data_win = tk.Toplevel(self.input_win)
                data_win.title("Données du problème de transport")
                data_win.geometry("850x650")
                data_win.configure(bg=BG_COLOR)
                data_win.grab_set()
                
                action_frame_tp = ttk.Frame(data_win); action_frame_tp.pack(fill=tk.X, padx=10, pady=10)
                ttk.Label(action_frame_tp, text="Modifiez les valeurs ou générez aléatoirement. \nOffres totales = demandes totales.", font=("Arial", 9, "italic"), foreground=PRIMARY_COLOR).pack(side=tk.LEFT, padx=5)
                
                cout_entries, offre_entries, demande_entries = [], [], [] 

                reset_btn_tp = ttk.Button(action_frame_tp, text="🔄 Réinitialiser", command=lambda: self.reset_transport_entries(cout_entries, offre_entries, demande_entries))
                reset_btn_tp.pack(side=tk.LEFT, padx=5)
                random_btn_tp = ttk.Button(action_frame_tp, text="🎲 Générer Aléatoire", command=lambda: generate_random_data_tp())
                random_btn_tp.pack(side=tk.RIGHT, padx=5)
                
                cout_frame_tp = ttk.LabelFrame(data_win, text="Coûts de transport", padding=10); cout_frame_tp.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
                for i_tp in range(n_usines):
                    row_entries_tp = []; row_frame_tp = ttk.Frame(cout_frame_tp); row_frame_tp.pack(fill=tk.X, pady=2)
                    ttk.Label(row_frame_tp, text=f"Usine {i_tp+1}").pack(side=tk.LEFT, padx=(0,10),ipadx=5)
                    for j_tp in range(n_magasins):
                        entry_tp = ttk.Entry(row_frame_tp, width=5, justify='center'); entry_tp.pack(side=tk.LEFT, padx=2); entry_tp.insert(0, "0"); row_entries_tp.append(entry_tp)
                    cout_entries.append(row_entries_tp)
                
                offre_demande_frame_tp = ttk.Frame(data_win); offre_demande_frame_tp.pack(fill=tk.X, padx=10, pady=5)
                offre_frame_tp = ttk.LabelFrame(offre_demande_frame_tp, text="Offres", padding=10); offre_frame_tp.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
                for i_tp in range(n_usines):
                    frame_tp_o = ttk.Frame(offre_frame_tp); frame_tp_o.pack(fill=tk.X, pady=2)
                    ttk.Label(frame_tp_o, text=f"Usine {i_tp+1}:", width=12).pack(side=tk.LEFT)
                    entry_tp_o = ttk.Entry(frame_tp_o, width=10, justify='right'); entry_tp_o.pack(side=tk.LEFT, padx=5); entry_tp_o.insert(0, "0"); offre_entries.append(entry_tp_o)
                
                demande_frame_tp = ttk.LabelFrame(offre_demande_frame_tp, text="Demandes", padding=10); demande_frame_tp.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5,0))
                for j_tp in range(n_magasins):
                    frame_tp_d = ttk.Frame(demande_frame_tp); frame_tp_d.pack(fill=tk.X, pady=2)
                    ttk.Label(frame_tp_d, text=f"Magasin {j_tp+1}:", width=12).pack(side=tk.LEFT)
                    entry_tp_d = ttk.Entry(frame_tp_d, width=10, justify='right'); entry_tp_d.pack(side=tk.LEFT, padx=5); entry_tp_d.insert(0, "0"); demande_entries.append(entry_tp_d)
                
                def generate_random_data_tp():
                    total_s = random.randint(max(n_usines, n_magasins) * 20, max(n_usines, n_magasins) * 70)
                    
                    offres_g_tp = [0] * n_usines; cs_o_tp = 0
                    for io_tp in range(n_usines - 1):
                        mv_o_tp = total_s - cs_o_tp - (n_usines - 1 - io_tp) # Ensure enough for remaining
                        val_o_tp = random.randint(1, max(1, mv_o_tp)) if mv_o_tp > 0 else (1 if (n_usines-1-io_tp == 0) else 0) # Give at least 1 to last one if forced
                        offres_g_tp[io_tp] = val_o_tp; cs_o_tp += val_o_tp
                    offres_g_tp[n_usines - 1] = max(0, total_s - cs_o_tp)
                    if sum(offres_g_tp) != total_s: # Adjust if sum is not perfect
                        diff_tp = total_s - sum(offres_g_tp)
                        if n_usines > 0: offres_g_tp[random.randrange(n_usines)] += diff_tp
                    random.shuffle(offres_g_tp)

                    demandes_g_tp = [0] * n_magasins; cs_d_tp = 0
                    for id_tp in range(n_magasins - 1):
                        mv_d_tp = total_s - cs_d_tp - (n_magasins - 1 - id_tp)
                        val_d_tp = random.randint(1, max(1, mv_d_tp)) if mv_d_tp > 0 else (1 if (n_magasins-1-id_tp == 0) else 0)
                        demandes_g_tp[id_tp] = val_d_tp; cs_d_tp += val_d_tp
                    demandes_g_tp[n_magasins - 1] = max(0, total_s - cs_d_tp)
                    if sum(demandes_g_tp) != total_s:
                        diff_d_tp = total_s - sum(demandes_g_tp)
                        if n_magasins > 0: demandes_g_tp[random.randrange(n_magasins)] += diff_d_tp
                    random.shuffle(demandes_g_tp)

                    # Final balance check
                    s_o = sum(offres_g_tp); s_d = sum(demandes_g_tp)
                    if s_o != s_d:
                        if s_o > s_d and n_magasins > 0: demandes_g_tp[0] += (s_o - s_d)
                        elif s_d > s_o and n_usines > 0: offres_g_tp[0] += (s_d - s_o)
                        # if one list is empty
                        elif n_magasins == 0 and n_usines > 0: offres_g_tp = [0]*n_usines # Reset to 0 if unbalanced and no sinks
                        elif n_usines == 0 and n_magasins > 0: demandes_g_tp = [0]*n_magasins

                    for i in range(n_usines): offre_entries[i].delete(0, tk.END); offre_entries[i].insert(0, str(offres_g_tp[i]))
                    for j in range(n_magasins): demande_entries[j].delete(0, tk.END); demande_entries[j].insert(0, str(demandes_g_tp[j]))
                    for i in range(n_usines):
                        for j in range(n_magasins): cout_entries[i][j].delete(0, tk.END); cout_entries[i][j].insert(0, str(random.randint(1, 20)))
                
                def submit_data_tp():
                    try:
                        couts, offres, demandes = [], [], []
                        # ... (validation for costs, offers, demands as before)
                        for i in range(n_usines): 
                            row = []
                            for j in range(n_magasins):
                                val_str = cout_entries[i][j].get().strip()
                                if not val_str: messagebox.showerror("Saisie manquante", f"Coût Usine {i+1}-M{j+1} requis.", parent=data_win); return
                                try: val = int(val_str); row.append(val)
                                except ValueError: messagebox.showerror("Format invalide", f"Coût U{i+1}-M{j+1} ('{val_str}') non entier.", parent=data_win); return
                            couts.append(row)
                        for i in range(n_usines):
                            val_str = offre_entries[i].get().strip()
                            if not val_str: messagebox.showerror("Saisie manquante", f"Offre Usine {i+1} requise.", parent=data_win); return
                            try: val = int(val_str); offres.append(val)
                            except ValueError: messagebox.showerror("Format invalide", f"Offre U{i+1} ('{val_str}') non entière.", parent=data_win); return
                        for j in range(n_magasins):
                            val_str = demande_entries[j].get().strip()
                            if not val_str: messagebox.showerror("Saisie manquante", f"Demande Magasin {j+1} requise.", parent=data_win); return
                            try: val = int(val_str); demandes.append(val)
                            except ValueError: messagebox.showerror("Format invalide", f"Demande M{j+1} ('{val_str}') non entière.", parent=data_win); return


                        if sum(offres) != sum(demandes):
                            messagebox.showerror("Erreur", f"Total offres ({sum(offres)}) ≠ Total demandes ({sum(demandes)}). Équilibrez le problème.", parent=data_win)
                            return
                        if any(o < 0 for o in offres) or any(d < 0 for d in demandes) or any(c < 0 for row in couts for c in row):
                            messagebox.showerror("Erreur", "Offres, demandes, coûts doivent être >= 0.", parent=data_win)
                            return
                        
                        offres_c = offres.copy(); demandes_c = demandes.copy()
                        solution, cout_total = None, None 
                        algo_name_disp = ""

                        if algo_key == "nordouest":
                            solution, cout_total = algos.NordO.nord_ouest(offres_c, demandes_c, couts)
                            algo_name_disp = "Nord-Ouest"
                        elif algo_key == "cout":
                            solution, cout_total = algos.moindre_cout.moindre_cout(offres_c, demandes_c, couts)
                            algo_name_disp = "Moindre Coût"
                        
                        result_text = f"🚚 Méthode de Transport : {algo_name_disp}\n\nSolution Initiale (quantités / coût unitaire) :\n"
                        header = ["U\\M"] + [f"M{j+1}" for j in range(n_magasins)] + ["Offre"]
                        result_text += "{:<5}".format(header[0]) + "\t" + "\t".join(["{:<10}".format(h) for h in header[1:-1]]) + "\t" + "{:<8}".format(header[-1]) + "\n"

                        for i_r in range(n_usines):
                            row_items = [f"U{i_r+1}"] + [f"{solution[i_r][j_c]}/{couts[i_r][j_c]}" for j_c in range(n_magasins)] + [f"({offres[i_r]})"]
                            result_text += "{:<5}".format(row_items[0]) + "\t" + "\t".join(["{:<10}".format(item) for item in row_items[1:-1]]) + "\t" + "{:<8}".format(row_items[-1]) + "\n"
                        
                        demande_items_txt = ["Dem"] + [f"({d})" for d in demandes] + [f"Tot:{sum(offres)}"]
                        result_text += "{:<5}".format(demande_items_txt[0]) + "\t" + "\t".join(["{:<10}".format(item) for item in demande_items_txt[1:-1]]) + "\t" + "{:<8}".format(demande_items_txt[-1]) + "\n"
                        result_text += f"\nCoût total pour cette solution : {cout_total}"
                        self.display_text(result_text)
                        
                        fig_tp_w = max(10, n_magasins * 1.8 + 3); fig_tp_h = max(7, n_usines * 1.0 + 3)
                        fig_tp = Figure(figsize=(fig_tp_w, fig_tp_h), dpi=100); ax_tp = fig_tp.add_subplot(111); ax_tp.axis('off')
                        
                        table_data_viz_tp = []
                        col_labels_viz_tp = ["Usine \\ Magasin"] + [f"M{j+1}" for j in range(n_magasins)] + ["Offre Initiale"]
                        for i_row_v_tp in range(n_usines):
                            row_viz_data_tp = [f"U{i_row_v_tp+1}"] + \
                                         [f"{solution[i_row_v_tp][j_col_v_tp]}\n(coût: {couts[i_row_v_tp][j_col_v_tp]})" for j_col_v_tp in range(n_magasins)] + \
                                         [str(offres[i_row_v_tp])]
                            table_data_viz_tp.append(row_viz_data_tp)
                        table_data_viz_tp.append(["Demande Initiale"] + [str(d) for d in demandes] + [f"Total: {sum(offres)}"])
                        
                        num_mid_cols_tp = n_magasins
                        first_cw_tp = 0.18; last_cw_tp = 0.15; mid_cws_total_tp = 1.0 - first_cw_tp - last_cw_tp
                        mid_cw_tp = mid_cws_total_tp / num_mid_cols_tp if num_mid_cols_tp > 0 else 0.1
                        col_widths_tp = [first_cw_tp] + [mid_cw_tp]*num_mid_cols_tp + [last_cw_tp]
                        col_widths_tp = [max(0.05, w) for w in col_widths_tp]; sum_w_tp = sum(col_widths_tp); col_widths_tp = [w/sum_w_tp for w in col_widths_tp]

                        table_viz_tp = ax_tp.table(cellText=table_data_viz_tp, colLabels=col_labels_viz_tp, cellLoc='center', loc='center', colWidths=col_widths_tp)
                        table_viz_tp.auto_set_font_size(False); table_viz_tp.set_fontsize(9); table_viz_tp.scale(1, 2.0)
                        for r_viz_tp in range(n_usines): 
                            for c_viz_tp in range(n_magasins):
                                cell_viz_tp = table_viz_tp.get_celld().get((r_viz_tp + 1, c_viz_tp + 1))
                                if cell_viz_tp and solution[r_viz_tp][c_viz_tp] > 0 : 
                                    cell_viz_tp.set_facecolor('#e6f7ff'); cell_viz_tp.set_text_props(weight='bold', color='darkblue')
                                elif cell_viz_tp:
                                    cell_viz_tp.set_text_props(color='gray')
                        ax_tp.set_title(f"Solution {algo_name_disp} - Coût total: {cout_total}", fontsize=14, pad=25)
                        plt.tight_layout(rect=[0,0.02,1,0.95])
                        self.display_graph(fig_tp)
                        data_win.destroy()

                    except Exception as e_tp_sub:
                        tb_tp_sub = traceback.format_exc()
                        print(f"Erreur Submit TP: {type(e_tp_sub).__name__} - {str(e_tp_sub)}\n{tb_tp_sub}")
                        messagebox.showerror("Erreur d'exécution Transport", f"{type(e_tp_sub).__name__}: {str(e_tp_sub)}", parent=data_win)
                        self.display_text(f"Erreur Transport: {type(e_tp_sub).__name__}: {str(e_tp_sub)}")
                
                btn_frame_tp = ttk.Frame(data_win); btn_frame_tp.pack(fill=tk.X, padx=10, pady=(10,5), side=tk.BOTTOM) # pady on bottom
                ttk.Button(btn_frame_tp, text="✅ Valider", command=submit_data_tp).pack(side=tk.LEFT, padx=5)
                ttk.Button(btn_frame_tp, text="❌ Annuler", command=data_win.destroy).pack(side=tk.RIGHT, padx=5)
                generate_random_data_tp()
                
            elif algo_key == "steep":
                n_usines = self._validate_positive_integer_revised("Nombre d'usines", "Nombre d'usines")
                if n_usines is None: return
                n_magasins = self._validate_positive_integer_revised("Nombre de magasins", "Nombre de magasins")
                if n_magasins is None: return

                data_win = tk.Toplevel(self.input_win)
                data_win.title("Données du Problème de Transport (Stepping Stone)")
                win_width = max(800, n_magasins * 110 + 220); win_height = max(650, n_usines * 85 + 380) # Increased estimates
                data_win.geometry(f"{win_width}x{win_height}"); data_win.configure(bg=BG_COLOR); data_win.grab_set()
                content_main_frame = ttk.Frame(data_win, padding=10); content_main_frame.pack(fill=tk.BOTH, expand=True)
                info_label = ttk.Label(content_main_frame, text="Entrez les données ou générez-les. Offres totales = demandes totales.", justify=tk.LEFT, wraplength=win_width - 40, font=("Arial", 10), background=BG_COLOR)
                info_label.pack(pady=(5,10), fill=tk.X)
                input_tables_frame = ttk.Frame(content_main_frame); input_tables_frame.pack(fill=tk.BOTH, expand=True)
                
                # Costs Frame
                cout_frame_ss = ttk.LabelFrame(input_tables_frame, text="Coûts", padding=10); cout_frame_ss.pack(fill=tk.X, padx=5, pady=5)
                cout_entries = []
                header_cost_frame_ss = ttk.Frame(cout_frame_ss); header_cost_frame_ss.pack(fill=tk.X)
                ttk.Label(header_cost_frame_ss, text="", width=10).pack(side=tk.LEFT, padx=(0,5)) # Label for Usine column
                for j_header_ss in range(n_magasins): ttk.Label(header_cost_frame_ss, text=f"M{j_header_ss+1}", width=7, anchor='center').pack(side=tk.LEFT, padx=1, expand=True, fill=tk.X)
                for i_ss in range(n_usines):
                    row_entries_c_ss = []; row_frame_c_ss = ttk.Frame(cout_frame_ss); row_frame_c_ss.pack(fill=tk.X, pady=2)
                    ttk.Label(row_frame_c_ss, text=f"U{i_ss+1}:", width=10, anchor='w').pack(side=tk.LEFT, padx=(0,5))
                    for j_ss in range(n_magasins):
                        entry_c_ss = ttk.Entry(row_frame_c_ss, width=7, justify='center'); entry_c_ss.pack(side=tk.LEFT, padx=1, expand=True, fill=tk.X); entry_c_ss.insert(0, "0"); row_entries_c_ss.append(entry_c_ss)
                    cout_entries.append(row_entries_c_ss)
                
                # Offers and Demands side-by-side
                offre_demande_container_ss = ttk.Frame(input_tables_frame); offre_demande_container_ss.pack(fill=tk.X, pady=5)
                
                offre_frame_ss = ttk.LabelFrame(offre_demande_container_ss, text="Offres", padding=10); offre_frame_ss.pack(side=tk.LEFT, fill=tk.Y, padx=(0,5), expand=True)
                offre_entries = []
                for i_ss in range(n_usines):
                    frame_o_ss = ttk.Frame(offre_frame_ss); frame_o_ss.pack(fill=tk.X, pady=2)
                    ttk.Label(frame_o_ss, text=f"U{i_ss+1}:", width=12, anchor='w').pack(side=tk.LEFT) # Adjusted width
                    entry_o_ss = ttk.Entry(frame_o_ss, width=10, justify='right'); entry_o_ss.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True); entry_o_ss.insert(0, "0"); offre_entries.append(entry_o_ss)
                
                demande_frame_ss = ttk.LabelFrame(offre_demande_container_ss, text="Demandes", padding=10); demande_frame_ss.pack(side=tk.LEFT, fill=tk.Y, padx=(5,0), expand=True)
                demande_entries = []
                for j_ss in range(n_magasins):
                    frame_d_ss = ttk.Frame(demande_frame_ss); frame_d_ss.pack(fill=tk.X, pady=2)
                    ttk.Label(frame_d_ss, text=f"M{j_ss+1}:", width=12, anchor='w').pack(side=tk.LEFT) # Adjusted width
                    entry_d_ss = ttk.Entry(frame_d_ss, width=10, justify='right'); entry_d_ss.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True); entry_d_ss.insert(0, "0"); demande_entries.append(entry_d_ss)
                
                def generate_random_data_action_ss(): # Uses the same logic as for nordouest/cout
                    total_s = random.randint(max(n_usines, n_magasins) * 20, max(n_usines, n_magasins) * 70)
                    offres_g_tp = [0] * n_usines; cs_o_tp = 0
                    for io_tp in range(n_usines - 1):
                        mv_o_tp = total_s - cs_o_tp - (n_usines - 1 - io_tp)
                        val_o_tp = random.randint(1, max(1, mv_o_tp)) if mv_o_tp > 0 else (1 if (n_usines-1-io_tp == 0) else 0)
                        offres_g_tp[io_tp] = val_o_tp; cs_o_tp += val_o_tp
                    offres_g_tp[n_usines - 1] = max(0, total_s - cs_o_tp)
                    if sum(offres_g_tp) != total_s: 
                        diff_tp = total_s - sum(offres_g_tp)
                        if n_usines > 0: offres_g_tp[random.randrange(n_usines)] += diff_tp
                    random.shuffle(offres_g_tp)

                    demandes_g_tp = [0] * n_magasins; cs_d_tp = 0
                    for id_tp in range(n_magasins - 1):
                        mv_d_tp = total_s - cs_d_tp - (n_magasins - 1 - id_tp)
                        val_d_tp = random.randint(1, max(1, mv_d_tp)) if mv_d_tp > 0 else (1 if (n_magasins-1-id_tp == 0) else 0)
                        demandes_g_tp[id_tp] = val_d_tp; cs_d_tp += val_d_tp
                    demandes_g_tp[n_magasins - 1] = max(0, total_s - cs_d_tp)
                    if sum(demandes_g_tp) != total_s:
                        diff_d_tp = total_s - sum(demandes_g_tp)
                        if n_magasins > 0: demandes_g_tp[random.randrange(n_magasins)] += diff_d_tp
                    random.shuffle(demandes_g_tp)
                    
                    s_o, s_d = sum(offres_g_tp), sum(demandes_g_tp)
                    if s_o != s_d:
                        if s_o > s_d and n_magasins > 0: demandes_g_tp[0] += (s_o - s_d)
                        elif s_d > s_o and n_usines > 0: offres_g_tp[0] += (s_d - s_o)
                        elif n_magasins == 0 and n_usines > 0: offres_g_tp = [0]*n_usines 
                        elif n_usines == 0 and n_magasins > 0: demandes_g_tp = [0]*n_magasins


                    for i in range(n_usines): offre_entries[i].delete(0, tk.END); offre_entries[i].insert(0, str(offres_g_tp[i]))
                    for j in range(n_magasins): demande_entries[j].delete(0, tk.END); demande_entries[j].insert(0, str(demandes_g_tp[j]))
                    for i in range(n_usines):
                        for j in range(n_magasins): cout_entries[i][j].delete(0, tk.END); cout_entries[i][j].insert(0, str(random.randint(1, 30)))
                
                def submit_data_action_ss(): 
                    try:
                        couts_list, offres_list, demandes_list = [], [], []
                        # Validation for costs, offers, demands (same as before)
                        for i_c in range(n_usines): 
                            row_c = []
                            for j_c in range(n_magasins):
                                val_str = cout_entries[i_c][j_c].get().strip()
                                if not val_str: messagebox.showerror("Saisie manquante", f"Coût Usine {i_c+1}-M{j_c+1} requis.", parent=data_win); return
                                try: val = int(val_str); row_c.append(val)
                                except ValueError: messagebox.showerror("Format invalide", f"Coût U{i_c+1}-M{j_c+1} ('{val_str}') non entier.", parent=data_win); return
                            couts_list.append(row_c)
                        for i_o in range(n_usines): 
                            val_str = offre_entries[i_o].get().strip()
                            if not val_str: messagebox.showerror("Saisie manquante", f"Offre Usine {i_o+1} requise.", parent=data_win); return
                            try: val = int(val_str); offres_list.append(val)
                            except ValueError: messagebox.showerror("Format invalide", f"Offre U{i_o+1} ('{val_str}') non entière.", parent=data_win); return
                        for j_d in range(n_magasins):
                            val_str = demande_entries[j_d].get().strip()
                            if not val_str: messagebox.showerror("Saisie manquante", f"Demande Magasin {j_d+1} requise.", parent=data_win); return
                            try: val = int(val_str); demandes_list.append(val)
                            except ValueError: messagebox.showerror("Format invalide", f"Demande M{j_d+1} ('{val_str}') non entière.", parent=data_win); return

                        if sum(offres_list) != sum(demandes_list):
                            messagebox.showerror("Erreur de Données", f"Total offres ({sum(offres_list)}) ≠ Total demandes ({sum(demandes_list)}). Équilibrez.", parent=data_win)
                            return
                        if any(o < 0 for o in offres_list) or any(d < 0 for d in demandes_list) or any(c < 0 for row in couts_list for c in row):
                            messagebox.showerror("Erreur de Données", "Offres, demandes et coûts doivent être >= 0.", parent=data_win)
                            return

                        solution_ss, cout_total_ss, iterations_ss, methode_init_ss, solution_initiale_liste_ss, cout_initial_val_ss_num, _ = \
    algos.stepping_stone.stepping_stone(offres_list, demandes_list, couts_list)
                        
                        result_text_ss = f"🪨 Stepping-Stone\n"
                        result_text_ss += f"Méthode d'initialisation: {methode_init_ss}\n"
                        result_text_ss += f"Coût initial ({methode_init_ss}): {cout_initial_val_ss_num:.2f}\n" # UTILISER LA VARIABLE CORRIGÉE
                        result_text_ss += f"Coût optimisé (Stepping Stone): {cout_total_ss:.2f} (après {iterations_ss} itérations)\n\n"
                        
                        header_txt_ss = ["U\\M"] + [f"M{j+1}" for j in range(n_magasins)] + ["Offre"]
                        result_text_ss += "{:<5}".format(header_txt_ss[0]) + "\t" + "\t".join(["{:<10}".format(h) for h in header_txt_ss[1:-1]]) + "\t" + "{:<8}".format(header_txt_ss[-1]) + "\n"

                        for i_r_ss in range(n_usines):
                            row_items_ss = [f"U{i_r_ss+1}"] + [f"{solution_ss[i_r_ss][j_c_ss]}/{couts_list[i_r_ss][j_c_ss]}" for j_c_ss in range(n_magasins)] + [f"({offres_list[i_r_ss]})"]
                            result_text_ss += "{:<5}".format(row_items_ss[0]) + "\t" + "\t".join(["{:<10}".format(item) for item in row_items_ss[1:-1]]) + "\t" + "{:<8}".format(row_items_ss[-1]) + "\n"
                        
                        demande_items_ss = ["Dem"] + [f"({d})" for d in demandes_list] + [f"Tot:{sum(offres_list)}"]
                        result_text_ss += "{:<5}".format(demande_items_ss[0]) + "\t" + "\t".join(["{:<10}".format(item) for item in demande_items_ss[1:-1]]) + "\t" + "{:<8}".format(demande_items_ss[-1]) + "\n"

                        self.display_text(result_text_ss)
                        
                        fig_width_ss = max(10, n_magasins * 1.8 + 3); fig_height_ss = max(7, n_usines * 1.0 + 3)
                        fig_ss = Figure(figsize=(fig_width_ss, fig_height_ss), dpi=100); ax_ss = fig_ss.add_subplot(111); ax_ss.axis('off')
                        
                        table_data_viz_ss = []
                        col_labels_viz_ss = ["Usine \\ Magasin"] + [f"M{j+1}" for j in range(n_magasins)] + ["Offre O(i)"]
                        for i_row_viz_ss in range(n_usines):
                            row_viz_data_ss = [f"U{i_row_viz_ss+1}"] + \
                                          [f"{solution_ss[i_row_viz_ss][j_col_viz_ss]}\n(coût: {couts_list[i_row_viz_ss][j_col_viz_ss]})" for j_col_viz_ss in range(n_magasins)] + \
                                          [str(offres_list[i_row_viz_ss])]
                            table_data_viz_ss.append(row_viz_data_ss)
                        table_data_viz_ss.append(["Demande D(j)"] + [str(d) for d in demandes_list] + [f"Total: {sum(offres_list)}"])
                        
                        num_mid_cols_ss = n_magasins
                        first_cw_ss = 0.18; last_cw_ss = 0.15; mid_cws_total_ss = 1.0 - first_cw_ss - last_cw_ss
                        mid_cw_ss = mid_cws_total_ss / num_mid_cols_ss if num_mid_cols_ss > 0 else 0.1
                        col_widths_list_ss = [first_cw_ss] + [mid_cw_ss]*num_mid_cols_ss + [last_cw_ss]
                        col_widths_list_ss = [max(0.05, w) for w in col_widths_list_ss]; sum_w_ss = sum(col_widths_list_ss); col_widths_list_ss = [w/sum_w_ss for w in col_widths_list_ss]

                        table_viz_ss = ax_ss.table(cellText=table_data_viz_ss, colLabels=col_labels_viz_ss, cellLoc='center', loc='center', colWidths=col_widths_list_ss)
                        table_viz_ss.auto_set_font_size(False); table_viz_ss.set_fontsize(9); table_viz_ss.scale(1, 2.0) # Scale height more
                        for r_h_ss in range(n_usines): 
                            for c_h_ss in range(n_magasins):
                                cell_ss = table_viz_ss.get_celld().get((r_h_ss + 1, c_h_ss + 1)) 
                                if cell_ss:
                                    if solution_ss[r_h_ss][c_h_ss] > 0 : 
                                        cell_ss.set_facecolor('#cceeff'); cell_ss.set_text_props(weight='bold', color='darkblue')
                                    else: 
                                        cell_ss.set_text_props(color='gray')
                        
                        title_ss = f"Stepping-Stone: Coût Initial ({methode_init_ss}) = {cout_initial_val_ss_num:.2f}\n" # UTILISER LA VARIABLE CORRIGÉE
                        title_ss += f"Coût Optimisé = {cout_total_ss:.2f} (après {iterations_ss} itérations)"
                        ax_ss.set_title(title_ss, fontsize=13, pad=25)
                        
                        plt.tight_layout(rect=[0,0.02,1,0.93]) # Adjusted rect for multiline title
                        self.display_graph(fig_ss)
                        if data_win and data_win.winfo_exists(): data_win.destroy()

                    except ValueError as ve_ss: 
                        messagebox.showerror("Erreur de Saisie Stepping Stone", str(ve_ss), parent=data_win)
                    except Exception as e_ss_main:
                        import traceback
                        tb_ss = traceback.format_exc()
                        print(f"Erreur Exécution Stepping Stone: {type(e_ss_main).__name__} - {str(e_ss_main)}\n{tb_ss}")
                        messagebox.showerror("Erreur d'Exécution Stepping Stone", f"{type(e_ss_main).__name__}: {str(e_ss_main)}. Consultez la console.", parent=data_win)
                        self.display_text(f"Erreur Stepping Stone: {type(e_ss_main).__name__} - {str(e_ss_main)}")
                
                action_buttons_frame_ss = ttk.Frame(content_main_frame); action_buttons_frame_ss.pack(fill=tk.X, pady=(15,5), side=tk.BOTTOM)
                ttk.Button(action_buttons_frame_ss, text="♻️ Générer Données", command=generate_random_data_action_ss).pack(side=tk.LEFT, padx=10)
                ttk.Button(action_buttons_frame_ss, text="✅ Valider et Exécuter", command=submit_data_action_ss).pack(side=tk.LEFT, padx=5)
                ttk.Button(action_buttons_frame_ss, text="❌ Annuler", command=data_win.destroy).pack(side=tk.RIGHT, padx=5)
                generate_random_data_action_ss()

            else:
                self.display_text("Algorithme non implémenté encore.")
                self.display_graph(None)
                
        except Exception as e:
            err_msg = f"❌ Erreur d'exécution de l'algorithme : {type(e).__name__} - {str(e)}"
            import traceback
            tb_str = traceback.format_exc()
            print(f"{err_msg}\n{tb_str}")
            self.display_text(f"{err_msg}\nConsultez la console pour la trace.")
            messagebox.showerror("Erreur d'Exécution", f"{err_msg}\nConsultez la console pour la trace.")
            
            fig_err = Figure(figsize=(10, 8), dpi=100)
            ax_err = fig_err.add_subplot(111)
            ax_err.text(0.5, 0.5, f"Erreur d'exécution:\n{type(e).__name__}\n{str(e)}", 
                    ha='center', va='center', fontsize=12, color='red', wrap=True)
            ax_err.axis('off')
            self.display_graph(fig_err)


    def back_to_algo_selection(self):
        if self.input_win and self.input_win.winfo_exists():
            self.input_win.destroy()
        
        if self.algo_win and self.algo_win.winfo_exists():
            self.algo_win.deiconify()
            self.algo_win.lift()
        else:
            self.open_algo_window()

    def close_window(self, window):
        if window and window.winfo_exists():
            window.destroy()
        
        if window == self.input_win:
            self.input_win = None 
            if self.algo_win and self.algo_win.winfo_exists():
                 self.algo_win.deiconify()
                 self.algo_win.lift()
            else:
                 self.algo_win = None 
                 self.open_algo_window()
        elif window == self.algo_win:
            self.algo_win = None
            # Si la fenêtre principale existe toujours, elle prend le focus.
            if self.gui and self.gui.winfo_exists():
                self.gui.lift() # Make sure main GUI is visible/active


    def on_closing(self):
        if messagebox.askokcancel("Quitter", "Êtes-vous sûr de vouloir quitter SMART-APPLICATION ?"):
            if self.input_win and self.input_win.winfo_exists():
                self.input_win.destroy()
            self.input_win = None
            
            if self.algo_win and self.algo_win.winfo_exists():
                self.algo_win.destroy()
            self.algo_win = None

            plt.close('all') 

            if self.gui and self.gui.winfo_exists():
                self.gui.destroy()
            self.gui = None

    def run(self):
        self.gui.mainloop()

    def _open_predecessor_selector_v2(self, current_task_name_widget, current_task_pred_label, all_task_entries_list, target_entry_data_dict, parent_window_for_popup):
        """
        Ouvre une popup pour sélectionner les prédécesseurs.
        Met à jour target_entry_data_dict['selected_preds_list'].
        parent_window_for_popup est la fenêtre task_win_metra.
        """
        available_task_names = []
        current_task_actual_name_raw = current_task_name_widget.get().strip().upper()

        for task_entry_dict_iter in all_task_entries_list:
            name_entry_widget_iter = task_entry_dict_iter['name_entry']
            potential_name_iter = name_entry_widget_iter.get().strip().upper()
            # Exclure la tâche actuelle elle-même et les noms vides
            if potential_name_iter and name_entry_widget_iter != current_task_name_widget :
                available_task_names.append(potential_name_iter)
        
        available_task_names = sorted(list(set(available_task_names)))

        if not available_task_names:
            messagebox.showinfo("Prédécesseurs", "Aucune autre tâche nommée à sélectionner.", parent=parent_window_for_popup)
            return

        selector_win = tk.Toplevel(parent_window_for_popup) # Enfant de la popup principale des tâches
        selector_win.title(f"Prédécesseurs pour {current_task_actual_name_raw or 'Tâche non nommée'}")
        selector_win.geometry("350x400"); selector_win.configure(bg=BG_COLOR); selector_win.grab_set()

        ttk.Label(selector_win, text="Sélectionnez les prédécesseurs:", background=BG_COLOR).pack(pady=10)
        listbox_frame_sel = ttk.Frame(selector_win); listbox_frame_sel.pack(pady=5,padx=10,fill=tk.BOTH,expand=True)
        
        pred_listbox_sel = tk.Listbox(listbox_frame_sel, selectmode=tk.MULTIPLE, exportselection=False, bg="white", fg=TEXT_COLOR)
        pred_scrollbar_sel = ttk.Scrollbar(listbox_frame_sel, orient=tk.VERTICAL, command=pred_listbox_sel.yview)
        pred_listbox_sel.config(yscrollcommand=pred_scrollbar_sel.set)
        pred_scrollbar_sel.pack(side=tk.RIGHT, fill=tk.Y); pred_listbox_sel.pack(side=tk.LEFT,fill=tk.BOTH,expand=True)

        for name_item in available_task_names: pred_listbox_sel.insert(tk.END, name_item)

        # Pré-sélectionner basé sur target_entry_data_dict['selected_preds_list']
        already_selected_preds = target_entry_data_dict.get('selected_preds_list', [])
        for i, item_in_lb in enumerate(pred_listbox_sel.get(0, tk.END)):
            if item_in_lb in already_selected_preds:
                pred_listbox_sel.select_set(i)

        def on_confirm_selection_v2():
            selected_indices_new = pred_listbox_sel.curselection()
            newly_selected_names = [pred_listbox_sel.get(index) for index in selected_indices_new]
            
            target_entry_data_dict['selected_preds_list'] = newly_selected_names # Mettre à jour la liste de données
            
            current_task_pred_label.config(text=", ".join(newly_selected_names) if newly_selected_names else "Aucun")
            selector_win.destroy()

        btn_frame_sel_confirm = ttk.Frame(selector_win); btn_frame_sel_confirm.pack(pady=10)
        ttk.Button(btn_frame_sel_confirm, text="Valider", command=on_confirm_selection_v2).pack(side=tk.LEFT,padx=5)
        ttk.Button(btn_frame_sel_confirm, text="Annuler", command=selector_win.destroy).pack(side=tk.RIGHT,padx=5)

def init():
    # Global error handler for Tkinter (optional but can be useful)
    # def tk_error_handler(exc, val, tb):
    #     import traceback
    #     error_message = "".join(traceback.format_exception(exc, val, tb))
    #     print(f"Unhandled Tkinter Exception:\n{error_message}")
    #     messagebox.showerror("Erreur Critique Tkinter", f"Une erreur inattendue est survenue dans l'interface.\n{val}\nConsultez la console.")
        # Potentially try to save work or exit gracefully
    # tk.Tk.report_callback_exception = tk_error_handler # Set for the root Tk instance
    
    app = Application()
    app.run()

# if __name__ == "__main__":
#     init()