"""Configurações compartilhadas por todos os scripts."""
from pathlib import Path
import os

RAIZ = Path(__file__).resolve().parents[1]
DADOS_BRUTOS = RAIZ / "data" / "raw"
DADOS_PROCESSADOS = RAIZ / "data" / "processed"
DADOS_EXEMPLO = RAIZ / "data" / "exemplo"
RESULTADOS = RAIZ / "results"
FIGURAS = RAIZ / "figures"

# Arquivos brutos (não versionados; ver data/README.md)
ARQ_EMPRESAS = DADOS_BRUTOS / "Pasta2_campinas.xlsx"                         # 29 empresas, indicador de produtividade
ARQ_BASE_N6 = DADOS_BRUTOS / "Base_para_N6_Relatorio_Estadual_e_Radar.xlsx"   # base estadual com o Radar
ARQ_RADAR_PRONTO = DADOS_BRUTOS / "Campinas_Base_N6_Radar.xlsx"               # alternativa: Radar já extraído

# Base analítica usada pelas análises. Pode ser trocada pela base sintética:
#   ALI_BASE=data/exemplo/base_analitica_sintetica.csv python run_all.py --sintetico
BASE_ANALITICA = Path(os.environ.get("ALI_BASE", DADOS_PROCESSADOS / "base_analitica.csv"))
if not BASE_ANALITICA.is_absolute():
    BASE_ANALITICA = RAIZ / BASE_ANALITICA

# Dimensões do Radar de Inovação: código curto, rótulo e nome da coluna na base estadual
DIMENSOES = [
    ("cg", "Controles gerenciais", "Controles gerenciais"),
    ("go", "Gestão de operações", "Gestão de operações"),
    ("mk", "Marketing", "Marketing"),
    ("ps", "Práticas sustentáveis", "Práticas sustentáveis"),
    ("pi", "Práticas de inovação", "Práticas inovação"),
    ("td", "Transformação digital", "Transformação digital"),
]

# IPCA mensal (%), série 433 do Banco Central (SGS), usado na sensibilidade à variação de preços
IPCA_MENSAL = {
    "2025_2ºsem": [0.26, -0.11, 0.48, 0.09, 0.18, 0.33],   # jul. a dez. de 2025
    "2026_1ºsem": [0.33, 0.70, 0.88, 0.67, 0.58, 0.16],    # jan. a jun. de 2026
}

# Sementes e repetições (fixas para reproduzir os números do artigo)
SEMENTE_HL = 11                  # bootstrap do estimador de Hodges-Lehmann (produtividade)
SEMENTE_CORRELACOES = 20261002   # permutação e bootstrap das correlações de Spearman
N_BOOT_HL = 5000
N_PERMUTACOES = 20000
N_BOOT_CORR = 10000

# Com a base sintética, as saídas vão para subpastas próprias e não sobrescrevem as do artigo
if "sintetica" in BASE_ANALITICA.name:
    RESULTADOS = RESULTADOS / "exemplo_sintetico"
    FIGURAS = FIGURAS / "exemplo_sintetico"

for _p in (DADOS_PROCESSADOS, RESULTADOS, FIGURAS):
    _p.mkdir(parents=True, exist_ok=True)
