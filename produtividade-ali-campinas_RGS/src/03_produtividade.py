"""Etapa 3 – Análises de produtividade (seções 3 e 4 do artigo).

Calcula a caracterização da amostra, a evolução da produtividade entre T0 e TF,
os testes e as verificações de sensibilidade. Gera tabelas em results/.

Entrada : data/processed/base_analitica.csv
Saídas  : results/produtividade_numeros.csv e results/tabela_*.csv
"""
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats.mstats import winsorize
from config import BASE_ANALITICA, RESULTADOS, IPCA_MENSAL, SEMENTE_HL, N_BOOT_HL
import estatistica as est

NUMEROS = []


def reg(indicador, valor, descricao=""):
    NUMEROS.append({"indicador": indicador, "valor": valor, "descricao": descricao})


def variacao(a, b):
    return (b / a - 1) * 100


def main():
    b = pd.read_csv(BASE_ANALITICA)
    c = b[b["concluiu"]].copy()                      # empresas com T0 e TF
    p0, p1 = c["produtividade_t0"], c["produtividade_tf"]
    base_pos = p0 > 0                                # variação % só existe com base positiva

    # --- Caracterização (Tabela 1, Tabela 2 e Figura 1) -----------------------
    situ = np.select([b["concluiu"], b["desistiu"], b["descontinuada"]], ["Concluído", "Desistiu", "Descontinuada"], "Em andamento")
    t1 = pd.Series(situ).value_counts().rename_axis("situacao").reset_index(name="empresas")
    t1["percentual"] = (t1["empresas"] / len(b) * 100).round(1)
    t1.to_csv(RESULTADOS / "tabela_1_situacao.csv", index=False)
    t2 = b["cadeia_produtiva"].value_counts().rename_axis("cadeia_produtiva").reset_index(name="empresas")
    t2["percentual"] = (t2["empresas"] / len(b) * 100).round(1)
    t2.to_csv(RESULTADOS / "tabela_2_cadeia_produtiva.csv", index=False)
    porte = b["porte"].value_counts().rename_axis("porte").reset_index(name="empresas")
    porte["percentual"] = (porte["empresas"] / len(b) * 100).round(1)
    porte.to_csv(RESULTADOS / "porte_29_empresas.csv", index=False)
    prob = b["categoria_problema"].fillna("Não classificado / ciclo em andamento").value_counts()
    prob.rename_axis("categoria_problema").reset_index(name="empresas").to_csv(RESULTADOS / "figura_1_categorias_problema.csv", index=False)

    # --- Intervenção: encontros e soluções -----------------------------------
    reg("encontros_concluintes", ",".join(map(str, sorted(c["encontros"].unique()))), "número de encontros das empresas concluintes")
    reg("encontros_nao_concluintes", ",".join(map(str, sorted(b.loc[~b["concluiu"], "encontros"].dropna().astype(int)))), "encontro em que as demais pararam")
    c["categoria_solucao"].value_counts().rename_axis("categoria_solucao").reset_index(name="empresas").to_csv(RESULTADOS / "solucoes_24_empresas.csv", index=False)

    # --- Evolução do grupo ------------------------------------------------------
    reg("n_concluintes", len(c))
    reg("mediana_t0", p0.median()); reg("mediana_tf", p1.median()); reg("var_mediana_%", variacao(p0.median(), p1.median()))
    reg("media_t0", p0.mean()); reg("media_tf", p1.mean()); reg("var_media_%", variacao(p0.mean(), p1.mean()))
    v = variacao(p0[base_pos], p1[base_pos])
    reg("n_variacao_individual", len(v), "empresas com produtividade inicial positiva")
    reg("mediana_variacoes_%", v.median()); reg("media_variacoes_%", v.mean())
    reg("media_aparada_10%", stats.trim_mean(v, 0.10))
    reg("media_winsorizada_10%", float(np.mean(winsorize(v.values, limits=(0.10, 0.10)))))
    d = (p1 - p0).values
    reg("empresas_com_ganho_R$", int((d > 0).sum())); reg("empresas_com_queda_R$", int((d < 0).sum()))
    p, metodo = est.wilcoxon_pareado(p1, p0)
    reg("wilcoxon_p", p, f"Wilcoxon pareado ({metodo})")
    reg("teste_do_sinal_p", est.teste_do_sinal(d))
    reg("efeito_r_rank_bisserial", est.rank_bisserial(d))
    hl = est.hodges_lehmann(d); lo, hi = est.hodges_lehmann_ic(d, N_BOOT_HL, SEMENTE_HL)
    reg("hodges_lehmann_R$", hl); reg("hodges_lehmann_ic95_inf", lo); reg("hodges_lehmann_ic95_sup", hi)
    reg("shapiro_wilk_p_diferencas", stats.shapiro(d).pvalue, "normalidade das diferenças (justifica teste não paramétrico)")

    # --- Sensibilidade -----------------------------------------------------------
    atip = c[(p0 <= 0) | (p1 <= 0)]["codigo"].tolist()
    s = c[~c["codigo"].isin(atip)]
    reg("sensibilidade_sem_atipicas_p", est.wilcoxon_pareado(s["produtividade_tf"], s["produtividade_t0"])[0], "sem " + ", ".join(atip))
    reg("sensibilidade_sem_atipicas_n", len(s))
    rho = stats.spearmanr(p0[base_pos], v)
    reg("regressao_media_rho", rho.statistic, "Spearman entre produtividade inicial e variação %")
    reg("regressao_media_p", rho.pvalue)
    ipca = {k: (np.prod([1 + m / 100 for m in ms]) - 1) * 100 for k, ms in IPCA_MENSAL.items()}
    for k, val in ipca.items():
        reg(f"ipca_{k}_%", val)
    p1r = p1 / c["ciclo"].map(lambda k: 1 + ipca[k] / 100)
    vr = variacao(p0[base_pos], p1r[base_pos])
    reg("deflacionada_mediana_variacoes_%", vr.median())
    reg("deflacionada_empresas_com_ganho", int((p1r > p0).sum()))
    reg("deflacionada_wilcoxon_p", est.wilcoxon_pareado(p1r, p0)[0])

    # --- Pessoal ocupado e agregados ------------------------------------------------
    F0, F1, C0, C1 = c["faturamento_t0"].sum(), c["faturamento_tf"].sum(), c["custos_t0"].sum(), c["custos_tf"].sum()
    N0, N1 = c["pessoas_t0"].sum(), c["pessoas_tf"].sum()
    reg("faturamento_agregado_var_%", variacao(F0, F1)); reg("custos_agregados_var_%", variacao(C0, C1))
    reg("pessoas_t0", N0); reg("pessoas_tf", N1); reg("pessoas_var_%", variacao(N0, N1))
    reg("va_por_pessoa_var_%", variacao((F0 - C0) / N0, (F1 - C1) / N1), "valor adicionado total por pessoa")
    reg("va_por_pessoa_quadro_fixo_var_%", variacao((F0 - C0) / N0, (F1 - C1) / N0), "mantido o quadro de T0")
    reg("empresas_sem_mudanca_de_quadro", int((c["pessoas_tf"] == c["pessoas_t0"]).sum()))

    # --- Atrito --------------------------------------------------------------------------
    nc = b[~b["concluiu"] & b["produtividade_t0"].notna()]
    reg("atrito_mediana_t0_nao_concluintes", nc["produtividade_t0"].median(), f"n = {len(nc)}")
    reg("atrito_mediana_t0_concluintes", p0.median())
    reg("atrito_mann_whitney_p", stats.mannwhitneyu(p0, nc["produtividade_t0"]).pvalue)
    b.loc[~b["concluiu"], "cadeia_produtiva"].value_counts().rename_axis("cadeia").reset_index(name="nao_concluintes").to_csv(RESULTADOS / "atrito_por_cadeia.csv", index=False)

    # --- Porte (Figura 3 e seção 4.1) e cadeia produtiva --------------------------------
    linhas = []
    for prt, g in c.groupby("porte"):
        g = g[g["produtividade_t0"] > 0]           # a empresa de base negativa sai das três medidas
        linhas.append({"porte": prt, "n": len(g),
                       "media_t0": g["produtividade_t0"].mean(), "media_tf": g["produtividade_tf"].mean(),
                       "var_media_%": variacao(g["produtividade_t0"].mean(), g["produtividade_tf"].mean()),
                       "mediana_var_produtividade_%": variacao(g["produtividade_t0"], g["produtividade_tf"]).median(),
                       "mediana_var_faturamento_%": variacao(g["faturamento_t0"], g["faturamento_tf"]).median(),
                       "mediana_var_custos_%": variacao(g["custos_t0"], g["custos_tf"]).median()})
    pd.DataFrame(linhas).round(2).to_csv(RESULTADOS / "porte_produtividade.csv", index=False)
    cad = c.groupby("cadeia_produtiva").apply(lambda g: pd.Series({"n": len(g), "var_media_%": variacao(g["produtividade_t0"].mean(), g["produtividade_tf"].mean())}), include_groups=False)
    cad.round(1).to_csv(RESULTADOS / "cadeia_produtividade.csv")

    # --- Tabelas 3 e 4 -------------------------------------------------------------------
    t = c.assign(variacao_pct=np.where(base_pos, variacao(p0, p1), np.nan))
    cols = ["codigo", "cadeia_produtiva", "porte", "produtividade_t0", "produtividade_tf", "variacao_pct"]
    t.sort_values("variacao_pct", ascending=False).head(5)[cols].round(2).to_csv(RESULTADOS / "tabela_3_maiores_ganhos.csv", index=False)
    t[t["produtividade_tf"] < t["produtividade_t0"]].sort_values("variacao_pct")[cols].round(2).to_csv(RESULTADOS / "tabela_4_quedas.csv", index=False)

    out = pd.DataFrame(NUMEROS)
    out.to_csv(RESULTADOS / "produtividade_numeros.csv", index=False)
    with pd.option_context("display.max_rows", None, "display.width", 160, "display.float_format", "{:,.4f}".format):
        print(out.to_string(index=False))


if __name__ == "__main__":
    main()
