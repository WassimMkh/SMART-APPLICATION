import numpy as np

def moindre_cout(offres, demandes, couts):
    """
    Résout le problème de transport par la méthode du moindre coût.

    Args:
        offres (list): Liste des offres pour chaque source.
        demandes (list): Liste des demandes pour chaque destination.
        couts (list): Matrice des coûts (sources x destinations).

    Returns:
        tuple: (solution, cout_total)
            solution (list): Matrice de la solution (quantités transportées).
            cout_total (float): Coût total de la solution.
    """
    if sum(offres) != sum(demandes):
        raise ValueError("La somme des offres doit égaler la somme des demandes.")
    
    n, m = len(offres), len(demandes)
    solution = np.zeros((n, m), dtype=int)

    # Copie des données pour ne pas modifier les originales
    offres_restantes = offres.copy()
    demandes_restantes = demandes.copy()
    cout_total = 0

    # Liste des cellules traitables (non saturées)
    while sum(offres_restantes) > 0 and sum(demandes_restantes) > 0:
        min_cout = float('inf')
        i_min = j_min = -1

        # Trouver la cellule à coût minimum
        for i in range(n):
            for j in range(m):
                if offres_restantes[i] > 0 and demandes_restantes[j] > 0:
                    if couts[i][j] < min_cout:
                        min_cout = couts[i][j]
                        i_min, j_min = i, j

        if i_min == -1 or j_min == -1:
            break  # aucune cellule valide trouvée
        
        quantite = min(offres_restantes[i_min], demandes_restantes[j_min])
        solution[i_min][j_min] = quantite
        cout_total += quantite * couts[i_min][j_min]
        offres_restantes[i_min] -= quantite
        demandes_restantes[j_min] -= quantite

    return solution.tolist(), cout_total
