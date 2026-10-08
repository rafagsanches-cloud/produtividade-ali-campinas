"""Confere os principais números do artigo contra os resultados gerados.

Só faz sentido com os dados reais. Tolerância: diferença de arredondamento.
"""
import pandas as pd
from config import RESULTADOS

ESPERADO_PROD = {  # indicador em produtividade_numeros.csv: (valor do artigo, casas decimais)
    "mediana_t0": (4873.48, 2), "mediana_tf": (5863.00, 2), "var_mediana_%": (20.3, 1), "var_media_%": (63.5, 1),
    "mediana_variacoes_%": (31.0, 1), "media_variacoes_%": (96.7, 1), "media_aparada_10%": (83.7, 1),
    "media_winsorizada_10%": (90.5, 1), "empresas_com_ganho_R$": (20, 0), "wilcoxon_p": (0.001, 3),
    "efeito_r_rank_bisserial": (0.73, 2), "hodges_lehmann_R$": (2680, 0), "hodges_lehmann_ic95_inf": (1119, 0),
    "hodges_lehmann_ic95_sup": (4459, 0), "regressao_media_rho": (-0.31, 2), "regressao_media_p": (0.16, 2),
    "ipca_2025_2ºsem_%": (1.24, 2), "ipca_2026_1ºsem_%": (3.36, 2), "deflacionada_mediana_variacoes_%": (26.7, 1),
    "deflacionada_empresas_com_ganho": (19, 0), "deflacionada_wilcoxon_p": (0.002, 3),
    "faturamento_agregado_var_%": (48.7, 1), "custos_agregados_var_%": (22.4, 1), "pessoas_var_%": (-3.1, 1),
    "va_por_pessoa_var_%": (75.0, 1), "va_por_pessoa_quadro_fixo_var_%": (69.6, 1), "empresas_sem_mudanca_de_quadro": (18, 0),
    "atrito_mediana_t0_nao_concluintes": (5572, 0), "atrito_mann_whitney_p": (0.74, 2),
}


def linha(nome, artigo, obtido, casas):
    ok = round(float(obtido), casas) == round(float(artigo), casas) or abs(float(obtido) - float(artigo)) <= 10 ** (-casas) / 2 + 1e-9
    return {"indicador": nome, "artigo": artigo, "obtido": round(float(obtido), max(casas, 3)), "confere": "ok" if ok else "DIFERENTE"}


def main():
    res = []
    prod = pd.read_csv(RESULTADOS / "produtividade_numeros.csv").set_index("indicador")["valor"]
    for k, (v, c) in ESPERADO_PROD.items():
        res.append(linha(k, v, prod[k], c))
    porte = pd.read_csv(RESULTADOS / "porte_produtividade.csv").set_index("porte")
    for prt, v in (("EPP", 82.8), ("ME", 54.8), ("MEI", 57.8)):
        res.append(linha(f"var_media_{prt}_%", v, porte.loc[prt, "var_media_%"], 1))
    for prt, v in (("EPP", (160.4, 60.1, 107.2)), ("ME", (26.5, 40.4, 10.3)), ("MEI", (16.4, -26.5, -24.4))):
        for nome, val in zip(("produtividade", "faturamento", "custos"), v):
            res.append(linha(f"mediana_var_{nome}_{prt}_%", val, porte.loc[prt, f"mediana_var_{nome}_%"], 1))
    radar = pd.read_csv(RESULTADOS / "radar_dimensoes.csv").set_index("dimensao")
    res.append(linha("radar_medio_t0", 1.89, radar.loc["Radar médio", "media_t0"], 2))
    res.append(linha("radar_medio_tf", 3.32, radar.loc["Radar médio", "media_tf"], 2))
    res.append(linha("radar_maior_p_dimensoes", 0.0011, radar.drop("Radar médio")["p_wilcoxon"].max(), 4))
    conf = pd.read_csv(RESULTADOS / "radar_confiabilidade.csv").set_index("momento")
    res.append(linha("alfa_cronbach_TF", 0.61, conf.loc["TF", "alfa_cronbach"], 2))
    res.append(linha("rho_medio_dimensoes_TF", 0.18, conf.loc["TF", "rho_medio_entre_dimensoes"], 2))
    cor = pd.read_csv(RESULTADOS / "correlacoes.csv")
    rm = cor[(cor["recorte"] == "A") & (cor["dimensao"] == "Radar médio")].iloc[0]
    for nome, v, campo in (("rho_radar_medio", 0.15, "rho_spearman"), ("ic95_inf", -0.37, "ic95_inf"), ("ic95_sup", 0.62, "ic95_sup"), ("p_permutacao", 0.56, "p_permutacao")):
        res.append(linha(f"correlacao_{nome}", v, rm[campo], 2))
    out = pd.DataFrame(res)
    out.to_csv(RESULTADOS / "conferencia_artigo.csv", index=False)
    print(out.to_string(index=False))
    print(f"\n{int((out['confere'] == 'ok').sum())} de {len(out)} números conferem com o artigo.")


if __name__ == "__main__":
    main()
