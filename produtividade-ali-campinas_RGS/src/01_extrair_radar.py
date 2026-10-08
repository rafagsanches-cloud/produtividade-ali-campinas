"""Etapa 1 – Extrai o Radar de Inovação das empresas da amostra a partir da base estadual.

A base estadual ("Base para N6 – Relatório Estadual e Radar") traz dois blocos de
colunas cujas linhas não estão alinhadas entre si:
  * bloco A (colunas A a P): identificação da empresa, descrições, custos variáveis
    e a dimensão Controles gerenciais do Radar;
  * bloco B (colunas S a AL): situação no programa, encontros, faturamento, pessoas
    ocupadas, produtividade e as outras cinco dimensões do Radar.
Por isso, cada empresa é localizada separadamente em cada bloco:
  * no bloco A, pela descrição do problema e da solução, custos, CNAE, ciclo e porte;
  * no bloco B, pelo faturamento, pessoas ocupadas, produtividade, encontro e situação.
A consistência do par encontrado é conferida pela Equação 1 do artigo:
  produtividade = (faturamento bruto - custos variáveis) / pessoas ocupadas.

Entrada : data/raw/Pasta2_campinas.xlsx e data/raw/Base_para_N6_Relatorio_Estadual_e_Radar.xlsx
Saída   : data/processed/radar.csv
"""
import numpy as np
import pandas as pd
from config import ARQ_EMPRESAS, ARQ_BASE_N6, DADOS_PROCESSADOS, DIMENSOES


def normalizar(v):
    if pd.isna(v):
        return None
    s = " ".join(str(v).replace("\t", " ").replace("\\n", " ").replace("\n", " ").split())
    try:
        return round(float(s), 2)
    except ValueError:
        return s.lower()


def main():
    base = pd.read_excel(ARQ_BASE_N6)
    emp = pd.read_excel(ARQ_EMPRESAS).dropna(how="all").reset_index(drop=True)

    # Delimitação dos blocos pelo número de linhas preenchidas
    fim_a = base.columns.get_loc("Custos variáveis - Inicial")
    ini_b = base.columns.get_loc("Empresa desistiu?")
    A = base.iloc[: int(base["Ciclo"].notna().sum()), : fim_a + 1]
    B = base.iloc[: int(base["Encontro"].last_valid_index()) + 1, ini_b:]
    NA, NB, NE = A.map(normalizar), B.map(normalizar), emp.map(normalizar)

    campos_a = {  # coluna na planilha das empresas -> (coluna na base, peso)
        "Descrição do Problema": ("Descrição do Problema", 5), "Descrição da Solução": ("Descrição da Solução", 5),
        "Custos variáveis - Inicial": ("Custos variáveis - Inicial", 3), "Custos variáveis - Final": ("Custos variáveis - Final", 3),
        "CNAE": ("CNAE", 2), "Ciclo": ("Ciclo", 1), "Porte": ("Porte", 1), "município": ("Município", 1),
        "Categoria do Problema": ("Categoria do Problema", 1), "Categoria da Solução": ("Categoria da Solução", 1),
        "Subsegmento": ("Subsegmento", 1), "Escritório Regional": ("Escritório Regional", 1), "Setor": ("Setor", 1)}
    campos_b = {
        "Faturamento bruto - Inicial": ("Faturamento bruto - Inicial", 3), "Faturamento bruto - Final": ("Faturamento bruto - Final", 3),
        "Pessoas ocupadas - Inicial": ("Pessoas ocupadas - Inicial", 1), "Pessoas ocupadas - Final": ("Pessoas ocupadas - Final", 1),
        "Produtividade - Inicial": ("Produtividade - Inicial", 3), "Produtividade - Final": ("Produtividade - Final", 3),
        "Encontro": ("Encontro", 1), "Empresa desistiu?": ("Empresa desistiu?", 1), "Empresa descontinuada?": ("Empresa Descontinuada", 1)}

    def melhores(N, campos, linha):
        pontos = np.zeros(len(N))
        for col_emp, (col_base, peso) in campos.items():
            pontos += (N[col_base] == linha[col_emp]).values * peso
        maximo = sum(p for _, p in campos.values())
        return np.where(pontos == maximo)[0]

    radar_b = {"go": "Gestão de operações", "mk": "Marketing", "ps": "Práticas sustentáveis",
               "pi": "Práticas inovação", "td": None}
    linhas = []
    for i, linha in NE.iterrows():
        cod = emp.at[i, "Nome Empresa"]
        reg = {"codigo": cod}
        ia, ib = melhores(NA, campos_a, linha), melhores(NB, campos_b, linha)
        obs = []
        if len(ia) == 1:
            reg["linha_bloco_a"] = int(ia[0]) + 2          # número da linha no Excel
            reg["radar_cg_t0"] = base.at[ia[0], "Controles gerenciais inicial"]
            reg["radar_cg_tf"] = base.at[ia[0], "Controles gerenciais final"]
        else:
            obs.append("não localizada no bloco A" if len(ia) == 0 else "bloco A ambíguo")
        tem_financeiro = pd.notna(emp.at[i, "Produtividade - Final"]) and str(emp.at[i, "Produtividade - Final"]).strip() != "-"
        if len(ib) >= 1 and tem_financeiro:
            reg["linha_bloco_b"] = "/".join(str(int(j) + 2) for j in ib)
            for cod_d, rot, nome in DIMENSOES:
                if cod_d == "cg":
                    continue
                c0 = "Transformacão digital inicial" if cod_d == "td" else f"{nome} inicial"
                c1 = "Transformação digital final" if cod_d == "td" else f"{nome} final"
                for sufixo, col in (("t0", c0), ("tf", c1)):
                    valores = {str(base.at[j, col]).strip() for j in ib}
                    reg[f"radar_{cod_d}_{sufixo}"] = valores.pop() if len(valores) == 1 else np.nan
                    if len(valores) >= 1:
                        obs.append(f"{rot} {sufixo.upper()}: registros duplicados com valores diferentes")
            # Conferência pela Equação 1, cruzando os dois blocos
            if "linha_bloco_a" in reg:
                j = ib[0]; a = ia[0]
                fat, cus = pd.to_numeric(base.at[j, "Faturamento bruto - Final"], errors="coerce"), pd.to_numeric(base.at[a, "Custos variáveis - Final"], errors="coerce")
                pes, pro = pd.to_numeric(base.at[j, "Pessoas ocupadas - Final"], errors="coerce"), pd.to_numeric(base.at[j, "Produtividade - Final"], errors="coerce")
                reg["confere_equacao_1"] = bool(np.isclose((fat - cus) / pes, pro, atol=0.01)) if pes else None
        elif not tem_financeiro:
            obs.append("sem mensuração final (fora das análises do Radar)")
        else:
            obs.append("não localizada no bloco B")
        reg["observacao"] = "; ".join(obs)
        linhas.append(reg)

    out = pd.DataFrame(linhas)
    cols_radar = [f"radar_{c}_{s}" for c, _, _ in DIMENSOES for s in ("t0", "tf")]
    out = out.reindex(columns=["codigo"] + cols_radar + ["linha_bloco_a", "linha_bloco_b", "confere_equacao_1", "observacao"])
    for cod_d, _, _ in DIMENSOES:
        for s in ("t0", "tf"):
            col = f"radar_{cod_d}_{s}"
            if col in out:
                out[col] = pd.to_numeric(out[col], errors="coerce")
    out.to_csv(DADOS_PROCESSADOS / "radar.csv", index=False)
    ok = out["radar_cg_tf"].notna() & out["radar_go_tf"].notna()
    print(f"Radar extraído: {len(out)} empresas; com Radar em T0 e TF: {int(ok.sum())}")
    print(f"Conferência pela Equação 1: {int(out.get('confere_equacao_1', pd.Series(dtype=bool)).fillna(False).sum())} pares consistentes")


if __name__ == "__main__":
    main()
