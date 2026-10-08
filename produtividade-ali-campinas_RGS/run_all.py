"""Executa toda a análise do artigo, na ordem.

Uso:
  python run_all.py              # dados reais em data/raw/ (ver data/README.md)
  python run_all.py --sintetico  # base sintética, para testar o código sem os dados
"""
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
SRC = RAIZ / "src"


def rodar(script, env):
    print(f"\n=== {script} " + "=" * (60 - len(script)))
    subprocess.run([sys.executable, str(SRC / script)], cwd=SRC, env=env, check=True)


def main():
    env = dict(os.environ)
    if "--sintetico" in sys.argv:
        rodar("gerar_dados_sinteticos.py", env)
        env["ALI_BASE"] = str(RAIZ / "data" / "exemplo" / "base_analitica_sintetica.csv")
        etapas = ["03_produtividade.py", "04_radar.py", "05_correlacoes.py", "06_figuras.py"]
    else:
        brutos = RAIZ / "data" / "raw"
        if not (brutos / "Pasta2_campinas.xlsx").exists():
            sys.exit("Faltam os dados brutos em data/raw/ (ver data/README.md). Para testar o código, use --sintetico.")
        etapas = []
        if (brutos / "Base_para_N6_Relatorio_Estadual_e_Radar.xlsx").exists():
            etapas.append("01_extrair_radar.py")
        else:
            print("Base estadual ausente: o Radar será lido de Campinas_Base_N6_Radar.xlsx.")
        etapas += ["02_preparar_base.py", "03_produtividade.py", "04_radar.py", "05_correlacoes.py",
                   "06_figuras.py", "conferir_numeros_artigo.py"]
    for e in etapas:
        rodar(e, env)
    print("\nConcluído. Tabelas em results/ e figuras em figures/.")


if __name__ == "__main__":
    main()
