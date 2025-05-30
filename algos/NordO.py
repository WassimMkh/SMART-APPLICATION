import numpy as np

def nord_ouest(offres, demandes, couts):
    """
    Résout le problème de transport par la méthode du coin Nord-Ouest.
    
    Args:
        offres (list): Liste des offres.
        demandes (list): Liste des demandes.
        couts (list): Matrice des coûts.
    
    Returns:
        tuple: (solution, cout_total)
    """
    if sum(offres) != sum(demandes):
        raise ValueError("La somme des offres doit égaler la somme des demandes.")
    
    # Copier les listes pour éviter les modifications en place
    offres = offres.copy()
    demandes = demandes.copy()
    
    n, m = len(offres), len(demandes)
    solution = np.zeros((n, m), dtype=int)
    i = j = 0
    cout_total = 0

    while i < n and j < m:
        qte = min(offres[i], demandes[j])
        solution[i][j] = qte
        cout_total += qte * couts[i][j]
        offres[i] -= qte
        demandes[j] -= qte

        if offres[i] == 0:
            i += 1
        if demandes[j] == 0:
            j += 1
    
    return solution.tolist(), cout_total
