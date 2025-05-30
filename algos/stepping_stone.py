import numpy as np
from algos.NordO import nord_ouest
from algos.moindre_cout import moindre_cout

def stepping_stone(offres, demandes, couts):
    """
    Optimise le problème de transport avec Stepping-Stone à partir de la meilleure
    solution initiale entre Nord-Ouest et Moindre Coût.

    Returns:
        tuple: (
            solution_finale (list),
            cout_final (float),
            iterations (int),
            methode_initiale (str),
            solution_initiale (list),
            cout_initial (float),
            derniere_solution (list)
        )
    """
    if sum(offres) != sum(demandes):
        raise ValueError("La somme des offres doit égaler la somme des demandes.")
    
    sol_nw, cout_nw = nord_ouest(offres.copy(), demandes.copy(), couts)
    sol_mc, cout_mc = moindre_cout(offres.copy(), demandes.copy(), couts)

    if cout_mc < cout_nw:
        solution_init = sol_mc
        cout_total = cout_mc
        methode = "Moindre Coût"
    else:
        solution_init = sol_nw
        cout_total = cout_nw
        methode = "Nord-Ouest"

    n, m = len(offres), len(demandes)
    solution = np.array(solution_init, dtype=int)

    def calculer_cout(sol):
        return sum(sol[i][j] * couts[i][j] for i in range(n) for j in range(m))
    
    iterations = 0
    max_iter = 100
    derniere_solution = solution.copy()

    while iterations < max_iter:
        iterations += 1
        amélioration = False

        u = [None] * n
        v = [None] * m
        u[0] = 0

        changed = True
        while changed:
            changed = False
            for i in range(n):
                for j in range(m):
                    if solution[i][j] > 0:
                        if u[i] is not None and v[j] is None:
                            v[j] = couts[i][j] - u[i]
                            changed = True
                        elif v[j] is not None and u[i] is None:
                            u[i] = couts[i][j] - v[j]
                            changed = True

        for i in range(n):
            for j in range(m):
                if solution[i][j] == 0 and u[i] is not None and v[j] is not None:
                    delta = couts[i][j] - u[i] - v[j]
                    if delta < 0:
                        chemin = trouver_chemin(solution, i, j)
                        if chemin and len(chemin) >= 4:
                            qte = min(solution[x][y] for idx, (x, y) in enumerate(chemin) if idx % 2 == 1)
                            for idx, (x, y) in enumerate(chemin):
                                if idx % 2 == 0:
                                    solution[x][y] += qte
                                else:
                                    solution[x][y] -= qte
                            cout_total = calculer_cout(solution)
                            derniere_solution = solution.copy()
                            amélioration = True
                            break
            if amélioration:
                break

        if not amélioration:
            break

    return (
        solution.tolist(),
        cout_total,
        iterations,
        methode,
        solution_init,
        cout_mc if methode == "Moindre Coût" else cout_nw,
        derniere_solution.tolist()
    )


def trouver_chemin(solution, i_dep, j_dep):
    """
    Cherche un chemin fermé pour l'amélioration dans Stepping-Stone.
    """
    n, m = solution.shape
    for start_dir in [0, 1]:
        queue = [(i_dep, j_dep, [(i_dep, j_dep)], start_dir)]
        visited = set([(i_dep, j_dep)])

        while queue:
            i, j, path, last_dir = queue.pop(0)
            current_dir = 1 - last_dir

            if len(path) >= 4 and (i, j) == (i_dep, j_dep):
                return path

            if current_dir == 0:  # horizontal
                for j2 in range(m):
                    if j2 != j and (solution[i][j2] > 0 or (i, j2) == (i_dep, j_dep)):
                        if (i, j2) in visited and (i, j2) != (i_dep, j_dep):
                            continue
                        queue.append((i, j2, path + [(i, j2)], current_dir))
                        visited.add((i, j2))
            else:  # vertical
                for i2 in range(n):
                    if i2 != i and (solution[i2][j] > 0 or (i2, j) == (i_dep, j_dep)):
                        if (i2, j) in visited and (i2, j) != (i_dep, j_dep):
                            continue
                        queue.append((i2, j, path + [(i2, j)], current_dir))
                        visited.add((i2, j))

    return None
