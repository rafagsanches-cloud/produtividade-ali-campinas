"""Etapa 2 – Monta a base analítica (uma linha por empresa) usada em todas as análises.

Junta o indicador de produtividade das 29 empresas (planilha do Escritório Regional)
com o Radar de Inovação extraído na etapa 1. As descrições livres de problema e de
solução não entram na base analítica, para reduzir o risco de identificação.

Entradas : data/raw/Pasta2_campinas.xlsx e data/processed/radar.csv
           (ou, na falta deste, data/raw/Campinas_Base_N6_Radar.xlsx)
Saída    : data/processed/base_analitica.csv
"""
import numpy as np
import pandas as pd
from config import ARQ_EMPRESAS, ARQ_RADAR_PRONTO, DADOS_PROCESSADOS, DIMENSOES

COLUNAS = {
    "Nome Empresa": "codigo", "Ciclo": "ciclo", "CNAE": "cnae", "Porte": "porte",
    "Cadeia Produtiva": "cadeia_produtiva", "Subsegmento": "subsegmento",
    "Empresa desistiu?": "desistiu", "Empresa descontinuada?": "descontinuada", "Encontro": "encontros",
    "Categoria do Problema": "categoria_problema", "Categoria da Solução": "categoria_solucao",
    "Custos variáveis - Inicial": "custos_t0", "Faturamento bruto - Inicial": "faturamento_t0",
    "Pessoas ocupadas - Inicial": "pessoas_t0", "Produtividade - Inicial": "produtividade_t0",
    "Custos variáveis - Final": "custos_tf", "Faturamento bruto - Final": "faturamento_tf",
    "Pessoas ocupadas - Final": "pessoas_tf", "Produtividade - Final": "produtividade_tf",
}
NUMERICAS = [c for c in COLUNAS.values() if c.endswith(("_t0", "_tf"))] + ["encontros", "cnae"]


def radar_da_planilha_pronta():
    """Alternativa à etapa 1: lê o Radar já extraído (aba Campinas_Base_N6)."""
    r = pd.read_excel(ARQ_RADAR_PRONTO, sheet_name="Campinas_Base_N6")
    out = pd.DataFrame({"codigo": r["Nome Empresa"]})
    for cod, _, nome in DIMENSOES:
        out[f"radar_{cod}_t0"] = pd.to_numeric(r[f"{nome} inicial"], errors="coerce")
        out[f"radar_{cod}_tf"] = pd.to_numeric(r[f"{nome} final"], errors="coerce")
    return out


def main():
    emp = pd.read_excel(ARQ_EMPRESAS).dropna(how="all")
    base = emp[list(COLUNAS)].rename(columns=COLUNAS)
    for c in NUMERICAS:
        base[c] = pd.to_numeric(base[c], errors="coerce")
    for c in ("desistiu", "descontinuada"):
        base[c] = base[c].astype(str).str.strip().str.lower().eq("sim")
    base["categoria_problema"] = base["categoria_problema"].replace("-", np.nan)
    base["porte"] = base["porte"].astype(str).str.strip()

    arq_radar = DADOS_PROCESSADOS / "radar.csv"
    if arq_radar.exists():
        radar = pd.read_csv(arq_radar)
        origem = "radar.csv (etapa 1)"
    elif ARQ_RADAR_PRONTO.exists():
        radar = radar_da_planilha_pronta()
        origem = ARQ_RADAR_PRONTO.name
    else:
        raise FileNotFoundError("Rode a etapa 1 ou coloque Campinas_Base_N6_Radar.xlsx em data/raw/.")
    cols = ["codigo"] + [f"radar_{c}_{s}" for c, _, _ in DIMENSOES for s in ("t0", "tf")]
    base = base.merge(radar[cols], on="codigo", how="left")

    base["concluiu"] = base["produtividade_tf"].notna()
    base.to_csv(DADOS_PROCESSADOS / "base_analitica.csv", index=False)
    print(f"Base analítica: {len(base)} empresas, {int(base['concluiu'].sum())} com mensuração final; Radar de {origem}")


if __name__ == "__main__":
    main()
