"""Etapa 5 – Correlação entre o Radar de Inovação e a produtividade (seção 4.2, Tabela 4/5).

Para cada dimensão e para o Radar médio, calcula o rho de Spearman em quatro recortes:
  A  ganho no Radar x variação percentual da produtividade (n = 17; sem base negativa)
  A2 ganho no Radar x variação da produtividade em reais (n = 18; robustez)
  B  Radar em TF x produtividade em TF (níveis finais)
  C  Radar em T0 x produtividade em T0 (níveis iniciais)
O p-valor é obtido por permutação, o IC 95% por bootstrap e o controle de múltiplos
testes por Benjamini-Hochberg dentro de cada recorte. O tau-b de Kendall serve de
confirmação. A ordem das operações aleatórias é fixa para reproduzir o artigo.

Entrada : data/processed/base_analitica.csv
Saída   : results/correlacoes.csv
"""
import numpy as np
import pandas as pd
from scipy import stats
from config import BASE_ANALITICA, RESULTADOS, DIMENSOES, SEMENTE_CORRELACOES, N_PERMUTACOES, N_BOOT_CORR
from comum import recorte_radar
import estatistica as est

RECORTES = {"A": ("G", "varpct", "ganho no Radar x variação % da produtividade"),
            "A2": ("G", "varabs", "ganho no Radar x variação da produtividade (R$)"),
            "B": ("TF", "p1", "Radar em TF x produtividade em TF"),
            "C": ("T0", "p0", "Radar em T0 x produtividade em T0")}


def main():
    D = recorte_radar(pd.read_csv(BASE_ANALITICA))
    rng = np.random.default_rng(SEMENTE_CORRELACOES)
    rotulos = [r for _, r, _ in DIMENSOES] + ["Radar médio"]
    res = []
    for rec, (suf, yv, desc) in RECORTES.items():
        linhas = []
        for r in rotulos:
            x = D[f"{r}|{suf}"].values.astype(float); y = D[yv].values.astype(float)
            m = ~np.isnan(x) & ~np.isnan(y); x, y = x[m], y[m]
            base = {"recorte": rec, "descricao": desc, "dimensao": r, "n": int(m.sum())}
            if len(set(x)) < 2:
                linhas.append({**base, "nota": "sem variação"}); continue
            rho = stats.spearmanr(x, y).statistic; kt = stats.kendalltau(x, y)
            lo, hi = est.spearman_bootstrap_ic(x, y, rng, N_BOOT_CORR)      # (ordem mantida: IC, depois p)
            p = est.spearman_permutacao(x, y, rng, N_PERMUTACOES)
            linhas.append({**base, "rho_spearman": rho, "ic95_inf": lo, "ic95_sup": hi, "p_permutacao": p,
                           "tau_b_kendall": kt.statistic, "p_kendall": kt.pvalue, "nota": ""})
        q = est.benjamini_hochberg([l.get("p_permutacao", np.nan) for l in linhas])
        for l, qq in zip(linhas, q):
            l["q_benjamini_hochberg"] = qq
        res += linhas
    out = pd.DataFrame(res)
    out.round(4).to_csv(RESULTADOS / "correlacoes.csv", index=False)
    n17, n18 = int(D["varpct"].notna().sum()), len(D)
    print(f"|rho| mínimo detectável (80% de poder): n={n17}: {est.rho_minimo_detectavel(n17):.2f}; n={n18}: {est.rho_minimo_detectavel(n18):.2f}")
    with pd.option_context("display.width", 200, "display.max_rows", None):
        print(out[["recorte", "dimensao", "n", "rho_spearman", "ic95_inf", "ic95_sup", "p_permutacao", "q_benjamini_hochberg", "tau_b_kendall"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
