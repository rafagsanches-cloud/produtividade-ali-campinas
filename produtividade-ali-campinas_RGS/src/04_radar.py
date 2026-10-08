"""Etapa 4 – Radar de Inovação (seções 3 e 4.2 e Apêndice A do artigo).

Compara T0 e TF nas seis dimensões e no Radar médio (teste de Wilcoxon pareado,
correção de Bonferroni) e estima a consistência interna do instrumento.

Entrada : data/processed/base_analitica.csv
Saídas  : results/radar_dimensoes.csv, results/radar_confiabilidade.csv,
          results/tabela_A1_radar_por_empresa.csv
"""
import numpy as np
import pandas as pd
from scipy import stats
from config import BASE_ANALITICA, RESULTADOS, DIMENSOES
from comum import recorte_radar
import estatistica as est


def main():
    b = pd.read_csv(BASE_ANALITICA)
    D = recorte_radar(b)
    rot = [r for _, r, _ in DIMENSOES]
    limiar = 0.05 / len(rot)                                   # Bonferroni: 0,05 / 6

    linhas = []
    for r in rot + ["Radar médio"]:
        x0, x1 = D[f"{r}|T0"], D[f"{r}|TF"]; m = x0.notna() & x1.notna()
        d = (x1 - x0)[m]
        p, metodo = est.wilcoxon_pareado(x1[m], x0[m], metodo="approx")   # empates: aproximação normal
        linhas.append({"dimensao": r, "n": int(m.sum()), "media_t0": x0[m].mean(), "media_tf": x1[m].mean(),
                       "ganho_medio": d.mean(), "melhoraram": int((d > 0).sum()), "iguais": int((d == 0).sum()),
                       "pioraram": int((d < 0).sum()), "p_wilcoxon": p,
                       "significativo_bonferroni": bool(p < limiar) if r != "Radar médio" else None})
    out = pd.DataFrame(linhas)
    out.round(4).to_csv(RESULTADOS / "radar_dimensoes.csv", index=False)
    print(f"Empresas com Radar em T0 e TF: {len(D)}  |  limiar de Bonferroni: {limiar:.4f}")
    print(out.round(3).to_string(index=False))

    conf = []
    for s in ("T0", "TF"):
        X = D[[f"{r}|{s}" for r in rot]].values
        a, n = est.alfa_cronbach(X)
        rho = pd.DataFrame(X).corr(method="spearman").values
        conf.append({"momento": s, "alfa_cronbach": a, "n": n,
                     "rho_medio_entre_dimensoes": np.nanmean(rho[np.triu_indices(len(rot), 1)]),
                     "dimensoes_sem_variacao": int((np.nanstd(X, axis=0) == 0).sum())})
    conf = pd.DataFrame(conf)
    conf.round(3).to_csv(RESULTADOS / "radar_confiabilidade.csv", index=False)
    print("\nConfiabilidade (em T0, dimensões sem variação tornam o alfa pouco informativo):")
    print(conf.round(3).to_string(index=False))

    # Apêndice A – Tabela A1: valores de T0 para TF por empresa
    siglas = {"Controles gerenciais": "CG", "Gestão de operações": "GO", "Marketing": "MK",
              "Práticas sustentáveis": "PS", "Práticas de inovação": "PI", "Transformação digital": "TD"}
    fmt = lambda v: "–*" if pd.isna(v) else (f"{v:.0f}" if float(v).is_integer() else f"{v:.2f}".replace(".", ","))
    a1 = pd.DataFrame({"Empresa": D["codigo"]})
    for r in rot:
        a1[siglas[r]] = [f"{fmt(i)} → {fmt(f)}" for i, f in zip(D[f"{r}|T0"], D[f"{r}|TF"])]
    a1["Média"] = [f"{i:.2f} → {f:.2f}".replace(".", ",") for i, f in zip(D["Radar médio|T0"], D["Radar médio|TF"])]
    a1.to_csv(RESULTADOS / "tabela_A1_radar_por_empresa.csv", index=False)


if __name__ == "__main__":
    main()
