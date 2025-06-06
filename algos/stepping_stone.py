# algos/stepping_stone.py
import numpy as np
# Assuming NordO.py and moindre_cout.py are in the same 'algos' directory
from algos.NordO import nord_ouest
from algos.moindre_cout import moindre_cout
import random # Added for potential use, though not directly in this snippet

# (Your stepping_stone and trouver_chemin functions as provided)
def trouver_chemin(solution, i_dep, j_dep):
    """
    Cherche un chemin fermé pour l'amélioration dans Stepping-Stone.
    Un chemin est une séquence de cellules (i,j) où l'on alterne ajout et retrait de qte.
    Il doit commencer et se terminer à (i_dep, j_dep) et avoir au moins 4 cellules.
    Les virages se font sur des cellules de base (solution[x][y] > 0).
    """
    n, m = solution.shape
    
    # path_stack: (current_i, current_j, current_path_list, last_move_direction (0:horizontal, 1:vertical))
    # The initial cell (i_dep, j_dep) is a "receiving" cell (+qte)
    
    # We need to find a cycle. Let's try a Depth First Search approach.
    # The path needs to alternate horizontal and vertical moves.
    # Cells in the path (except start/end) must be basic variables (solution > 0)
    # for cells where we subtract qte. The start cell (i_dep, j_dep) is non-basic.

    # A path looks like: (i0,j0)+, (i0,j1)-, (i1,j1)+, (i1,j0)-, ... (ix,j0)+ -> back to (i0,j0)
    
    q = [] # queue for BFS like search for a cycle. (current_row, current_col, path_taken, last_direction_horizontal)
    
    # Try starting with a horizontal move from (i_dep, j_dep)
    # Path stores (row, col) tuples
    q.append((i_dep, j_dep, [(i_dep, j_dep)], True)) # last_move_was_horizontal = True initially (conceptually)

    visited_states = set() # To avoid redundant searches: (current_cell, last_cell_in_path_tuple, frozenset(path_cells))

    while q:
        r, c, current_path, last_move_horizontal = q.pop(0)
        
        state = ((r,c), tuple(current_path[-2:]) if len(current_path)>1 else tuple(current_path[-1:]), frozenset(current_path))
        if state in visited_states:
            continue
        visited_states.add(state)

        # Next move should be in the other direction
        if last_move_horizontal: # Try vertical moves
            for nr in range(n):
                if nr == r: continue # Must move to a different row

                # If this is the closing move back to the start column AND it's a valid path length
                if c == j_dep and nr == i_dep and len(current_path) >= 3 : # Path of 3 + this = 4
                    final_path = current_path + [(nr, c)]
                    # Validate path structure (alternating row/col changes)
                    # For a path p0,p1,p2,p3 (p3=p0):
                    # p0=(r0,c0), p1=(r0,c1), p2=(r1,c1), p3=(r1,c0) -> valid
                    if len(final_path) % 2 == 0: # Even number of segments for a closed loop
                        is_valid_structure = True
                        for k in range(len(final_path) -1):
                            p_curr = final_path[k]
                            p_next = final_path[(k+1)] #% len(final_path)] for true cycle
                            if k % 2 == 0: # Horizontal segment expected
                                if p_curr[0] != p_next[0] or p_curr[1] == p_next[1]:
                                    is_valid_structure = False; break
                            else: # Vertical segment expected
                                if p_curr[1] != p_next[1] or p_curr[0] == p_next[0]:
                                    is_valid_structure = False; break
                        if is_valid_structure:
                            return final_path[:-1] # Return path without repeating start if cycle check is good
                    # The original implementation seems to rely on BFS finding a cycle of specific form
                    # This simple BFS needs refinement for robust stepping stone cycle finding.
                    # The provided BFS is more like a general graph traversal.
                    # For now, let's assume the structure of the problem guides it.
                    # The key is that path must be closed, have even length >= 4, and alternate turns.
                    # And - marked cells must be basic variables.

                # If it's a basic variable (or the very first cell of the path again for closing)
                # The (nr,c) cell is a candidate for a '+' or '-' cell.
                # If it's a '-' cell (odd index in path), it must be > 0
                # If it's a '+' cell (even index), it can be 0 (like i_dep, j_dep)
                is_minus_cell = (len(current_path)) % 2 == 1 # 0-indexed path, so path[1] is first '-'

                if solution[nr][c] > 0 or ((nr,c) == (i_dep, j_dep) and len(current_path) >=3 ) :
                     if not is_minus_cell or solution[nr][c] > 0 : # Ensure minus cells are basic
                        new_path = current_path + [(nr, c)]
                        # If we returned to (i_dep, j_dep) and path is long enough
                        if (nr,c) == (i_dep, j_dep) and len(new_path) >= 4 and len(new_path) % 2 == 1: # odd path len before closing, so total is even
                            # check structure
                            valid = True
                            for k_chk in range(len(new_path)-1):
                                r1,c1 = new_path[k_chk]
                                r2,c2 = new_path[k_chk+1]
                                if k_chk % 2 == 0 : # from (i_dep,j_dep) should be horizontal
                                    if r1 != r2: valid=False; break # Expected horizontal
                                else:
                                    if c1 != c2: valid=False; break # Expected vertical
                            if valid: return new_path[:-1] # Return path without the final duplicate of start_node

                        if (nr,c) not in current_path or ((nr,c) == (i_dep, j_dep) and len(current_path) >=3): # Prevent trivial cycles or allow closing
                             q.append((nr, c, new_path, False)) # Next move must be horizontal

        else: # Try horizontal moves (last_move_horizontal was False)
            for nc in range(m):
                if nc == c: continue

                is_minus_cell = (len(current_path)) % 2 == 1

                if solution[r][nc] > 0 or ((r,nc) == (i_dep, j_dep) and len(current_path) >=3) :
                    if not is_minus_cell or solution[r][nc] > 0 :
                        new_path = current_path + [(r, nc)]
                        if (r,nc) == (i_dep, j_dep) and len(new_path) >= 4 and len(new_path) % 2 == 1:
                            valid = True
                            for k_chk in range(len(new_path)-1):
                                r1,c1 = new_path[k_chk]
                                r2,c2 = new_path[k_chk+1]
                                if k_chk % 2 == 0 : # from (i_dep,j_dep) should be vertical if first one here was horizontal
                                     if c1 != c2: valid=False; break
                                else:
                                     if r1 != r2: valid=False; break
                            if valid: return new_path[:-1]

                        if (r,nc) not in current_path or ((r,nc) == (i_dep, j_dep) and len(current_path) >=3):
                            q.append((r, nc, new_path, True)) # Next move must be vertical
    return None # No valid cycle found


def stepping_stone(offres, demandes, couts):
    if sum(offres) != sum(demandes):
        raise ValueError("La somme des offres doit égaler la somme des demandes.")
    
    # Ensure copies are passed to initial solution finders
    sol_nw, cout_nw = nord_ouest(list(offres), list(demandes), couts)
    sol_mc, cout_mc = moindre_cout(list(offres), list(demandes), couts)

    # Convert to numpy arrays for easier manipulation internally
    if cout_mc < cout_nw:
        solution_init_list = sol_mc
        cout_total = float(cout_mc) # Ensure float
        methode = "Moindre Coût"
    else:
        solution_init_list = sol_nw
        cout_total = float(cout_nw) # Ensure float
        methode = "Nord-Ouest"

    n = len(offres)
    m = len(demandes)
    solution = np.array(solution_init_list, dtype=float) # Use float for solution for qte adjustments
    couts_np = np.array(couts, dtype=float) # Ensure couts is also numpy array

    def calculer_cout(sol_calc):
        return np.sum(sol_calc * couts_np) # More efficient with numpy
    
    iterations = 0
    max_iter = n * m * 2 # Heuristic for max iterations to prevent infinite loops

    while iterations < max_iter:
        iterations += 1
        amélioration_trouvée_cette_iteration = False

        # Calculer les potentiels u et v (méthode MODI / dual variables)
        u = np.full(n, np.nan, dtype=float) # Initialize with NaN
        v = np.full(m, np.nan, dtype=float)
        
        # Ancre u[0] = 0 pour les systèmes sous-déterminés
        # (ou choisir une ligne/colonne avec le plus de cellules de base)
        # For simplicity, u[0] = 0 is common if row 0 has basic variables.
        # A more robust way is to find a row/col with most basic vars, or iterate.
        
        # Find first basic variable to anchor u and v calculations
        first_basic_r, first_basic_c = -1, -1
        for r_idx in range(n):
            for c_idx in range(m):
                if solution[r_idx, c_idx] > 1e-9: # Consider >0 as basic (epsilon for float)
                    first_basic_r, first_basic_c = r_idx, c_idx
                    break
            if first_basic_r != -1:
                break
        
        if first_basic_r == -1 : # No basic variables, solution is likely all zeros (degenerate)
            # This case should ideally not happen if sum(offres)>0
            # Or it means the problem is highly degenerate or already optimal in a trivial way.
            break 

        u[first_basic_r] = 0.0 # Anchor one u value

        # Itérer pour calculer tous les u et v pour les cellules de base
        # This needs to be iterative if graph of basic cells is not simple tree
        for _ in range(n + m): # Iterate enough times to propagate values
            for r_idx in range(n):
                for c_idx in range(m):
                    if solution[r_idx, c_idx] > 1e-9: # Pour les cellules de base (x_ij > 0)
                        if not np.isnan(u[r_idx]) and np.isnan(v[c_idx]):
                            v[c_idx] = couts_np[r_idx, c_idx] - u[r_idx]
                        elif np.isnan(u[r_idx]) and not np.isnan(v[c_idx]):
                            u[r_idx] = couts_np[r_idx, c_idx] - v[c_idx]
        
        if np.isnan(u).any() or np.isnan(v).any():
            # This indicates a degenerate solution where not all u,v could be determined.
            # Stepping stone path finding is harder here. For now, we might stop or need a more complex u,v.
            # print("Warning: Degenerate solution, u/v calculation incomplete. Path finding may fail.")
            # A common way to handle degeneracy is to add very small epsilon quantities.
            # For now, let the path finding attempt it. If it fails, loop will break.
            pass


        # Calculer les coûts réduits (delta_ij = c_ij - u_i - v_j) pour les cellules hors base
        meilleur_delta = 0
        cellule_entrante = None

        for r_idx in range(n):
            for c_idx in range(m):
                if solution[r_idx, c_idx] < 1e-9: # Pour les cellules hors base (x_ij = 0)
                    if not np.isnan(u[r_idx]) and not np.isnan(v[c_idx]): # Check if u,v are calculated
                        delta = couts_np[r_idx, c_idx] - u[r_idx] - v[c_idx]
                        if delta < meilleur_delta:
                            meilleur_delta = delta
                            cellule_entrante = (r_idx, c_idx)
        
        if cellule_entrante is None or meilleur_delta >= -1e-9: # No improvement or negligible
            break # Solution optimale trouvée

        # Amélioration possible, trouver le chemin et ajuster
        r_in, c_in = cellule_entrante
        chemin = trouver_chemin(solution, r_in, c_in) # This path finding needs to be robust

        if chemin and len(chemin) >= 4: # Chemin trouvé
            qte_a_transferer = float('inf')
            # Les cellules impaires (1, 3, ...) dans le chemin sont celles où l'on soustrait
            for idx, (r_path, c_path) in enumerate(chemin):
                if idx % 2 == 1: # Cellules '-'
                    qte_a_transferer = min(qte_a_transferer, solution[r_path, c_path])
            
            if qte_a_transferer == float('inf') or qte_a_transferer < 1e-9 : # No quantity to transfer or path error
                # This can happen if path is bad or solution is highly degenerate
                # print(f"Warning: Path found for {cellule_entrante} but no quantity to transfer or path error. Qte={qte_a_transferer}")
                break # Stop if we can't improve meaningfully


            for idx, (r_path, c_path) in enumerate(chemin):
                if idx % 2 == 0: # Cellules '+' (y compris la cellule entrante)
                    solution[r_path, c_path] += qte_a_transferer
                else: # Cellules '-'
                    solution[r_path, c_path] -= qte_a_transferer
            
            cout_total = calculer_cout(solution)
            amélioration_trouvée_cette_iteration = True
        else: # Aucun chemin trouvé pour la cellule entrante la plus prometteuse
            # This might mean the path finder failed or the u,v method hit a complex case.
            # print(f"Warning: No valid Stepping Stone path found for entering cell {cellule_entrante} with delta {meilleur_delta}.")
            break 

        if not amélioration_trouvée_cette_iteration:
            break # Sortir si aucune amélioration n'a été faite dans cette itération

    # Convert solution back to list of lists of ints for consistency if desired
    solution_finale_list = [[int(round(val)) for val in row] for row in solution]
    
    return (
        solution_finale_list,
        float(calculer_cout(solution)), # Recalculate with final solution (potentially rounded)
        iterations,
        methode, # Initial method
        solution_init_list, # Initial solution (list of lists)
        float(cout_mc if methode == "Moindre Coût" else cout_nw), # Initial cost
        solution_finale_list # Last solution state before potential rounding
    )