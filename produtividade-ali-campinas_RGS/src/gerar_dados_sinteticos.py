"""Gera uma base analítica SINTÉTICA, com a mesma estrutura da base real.

Serve para testar o código sem acesso aos dados do Sistema ALI. Os valores são
aleatórios: os resultados obtidos com ela NÃO correspondem aos do artigo.

Saída : data/exemplo/base_analitica_sintetica.csv
"""
import numpy as np
import pandas as pd
from config import DADOS_EXEMPLO, DIMENSOES


def main(semente=2026):
    rng = np.random.default_rng(semente)
    n = 29
    df = pd.DataFrame({"codigo": [f"S{i:03d}" for i in range(1, n + 1)]})
    df["ciclo"] = ["2025_2ºsem"] * 6 + ["2026_1ºsem"] * 23
    df["cnae"] = rng.choice([1091101, 1412601, 2063100, 2539001, 3212400], n)
    df["porte"] = rng.permutation(["ME"] * 19 + ["EPP"] * 6 + ["MEI"] * 4)
    df["cadeia_produtiva"] = rng.permutation(["Alimentos e bebidas"] * 12 + ["Moda"] * 7 + ["Indústria - Outros"] * 6 + ["Beleza"] * 3 + ["Atividades de interesse público"])
    df["subsegmento"] = df["cadeia_produtiva"]
    situ = rng.permutation(["concluiu"] * 24 + ["andamento"] * 2 + ["desistiu"] * 2 + ["descontinuada"])
    df["desistiu"] = situ == "desistiu"; df["descontinuada"] = situ == "descontinuada"
    df["encontros"] = np.where(situ == "concluiu", 9, rng.choice([2, 3, 6, 7], n))
    cats = ["Marketing / divulgação", "Processos internos", "Faturamento / Quantidade de clientes", "Custos", "Gestão de pessoas"]
    df["categoria_problema"] = rng.choice(cats, n)
    df["categoria_solucao"] = rng.choice(["Marketing e divulgação", "Contratação de pessoal", "Processos internos", "Gestão financeira", "Capacitação da equipe"], n)
    df["pessoas_t0"] = rng.integers(1, 20, n).astype(float)
    df["faturamento_t0"] = np.round(rng.lognormal(10.5, 1.0, n), 2)
    df["custos_t0"] = np.round(df["faturamento_t0"] * rng.uniform(0.2, 0.8, n), 2)
    df["produtividade_t0"] = (df["faturamento_t0"] - df["custos_t0"]) / df["pessoas_t0"]
    conc = situ == "concluiu"
    df["pessoas_tf"] = np.where(conc, np.maximum(1, df["pessoas_t0"] + rng.integers(-1, 2, n)), np.nan)
    df["faturamento_tf"] = np.where(conc, np.round(df["faturamento_t0"] * rng.lognormal(0.3, 0.5, n), 2), np.nan)
    df["custos_tf"] = np.where(conc, np.round(df["custos_t0"] * rng.lognormal(0.15, 0.4, n), 2), np.nan)
    df["produtividade_tf"] = (df["faturamento_tf"] - df["custos_tf"]) / df["pessoas_tf"]
    com_radar = np.zeros(n, bool); com_radar[rng.choice(np.where(conc)[0], 18, replace=False)] = True
    for cod, _, _ in DIMENSOES:
        t0 = rng.choice([1, 2, 2, 2, 2], n).astype(float)
        tf = np.clip(t0 + rng.choice([0, 1, 1, 2, 2, 3], n), 1, 5)
        df[f"radar_{cod}_t0"] = np.where(com_radar | (situ != "concluiu"), t0, np.nan)
        df[f"radar_{cod}_tf"] = np.where(com_radar, tf, np.nan)
    df["concluiu"] = conc
    DADOS_EXEMPLO.mkdir(parents=True, exist_ok=True)
    df.to_csv(DADOS_EXEMPLO / "base_analitica_sintetica.csv", index=False)
    print("Base sintética gravada em", DADOS_EXEMPLO / "base_analitica_sintetica.csv")


if __name__ == "__main__":
    main()
