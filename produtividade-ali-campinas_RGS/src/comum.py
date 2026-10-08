"""Funções de apoio para montar o recorte das 18 empresas com Radar em T0 e TF."""
import numpy as np
import pandas as pd
from config import DIMENSOES


def recorte_radar(b):
    """Devolve o quadro usado nas análises do Radar e das correlações.

    Mantém a ordem original das linhas (importante para reproduzir permutações e
    bootstrap com a mesma semente). O Radar médio usa as dimensões disponíveis.
    """
    D = pd.DataFrame({"codigo": b["codigo"], "p0": b["produtividade_t0"], "p1": b["produtividade_tf"]})
    for cod, rot, _ in DIMENSOES:
        D[f"{rot}|T0"] = b[f"radar_{cod}_t0"]; D[f"{rot}|TF"] = b[f"radar_{cod}_tf"]
        D[f"{rot}|G"] = D[f"{rot}|TF"] - D[f"{rot}|T0"]
    rot = [r for _, r, _ in DIMENSOES]
    for s in ("T0", "TF", "G"):
        D[f"Radar médio|{s}"] = D[[f"{r}|{s}" for r in rot]].mean(axis=1)
    D = D[D["p1"].notna() & D["Radar médio|TF"].notna()].reset_index(drop=True)
    D["varpct"] = np.where(D["p0"] > 0, D["p1"] / D["p0"] - 1, np.nan)
    D["varabs"] = D["p1"] - D["p0"]
    return D
