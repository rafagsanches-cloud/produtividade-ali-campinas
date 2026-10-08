# Produtividade e Radar de Inovação nas MPE industriais de Campinas (SP)

Código e metodologia do artigo **"Desafios da Indústria de Transformação: Resultados do Programa ALI Produtividade em Micro e Pequenas Empresas de Campinas (SP)"**, de Rafael Grecco Sanches (2026).

O repositório reproduz todos os números, tabelas e figuras do artigo a partir dos dados do Sistema ALI. Os dados não estão incluídos, por serem confidenciais (ver [data/README.md](data/README.md)), mas há uma base sintética para quem quiser rodar e entender o código.

## O que o estudo faz

O estudo acompanha 29 micro e pequenas empresas industriais atendidas pelo Programa ALI Produtividade no Escritório Regional de Campinas (SP), nos ciclos do 2º semestre de 2025 e do 1º semestre de 2026, e responde a três perguntas:

1. **A produtividade mudou entre o início (T0) e o fim (TF) do ciclo?** Sim. Ela subiu em 20 das 24 empresas com mensuração completa (Wilcoxon, p = 0,001), com mudança típica de cerca de R$ 2.680 por pessoa ocupada.
2. **A maturidade de gestão, medida pelo Radar de Inovação, mudou?** Sim. A média passou de 1,89 para 3,32, numa escala de 1 a 5, nas 18 empresas com Radar nos dois momentos, e as seis dimensões avançaram.
3. **As duas mudanças se relacionam?** Não foi possível detectar relação. Para o Radar médio, ρ = 0,15 (p = 0,56), e com essa amostra só correlações fortes seriam detectáveis.

A descrição completa dos métodos está em [docs/metodologia.md](docs/metodologia.md). O mapa de onde está cada resultado do artigo fica em [docs/mapa_artigo.md](docs/mapa_artigo.md).

## Estrutura

```
.
├── run_all.py                    # executa toda a análise, na ordem
├── src/
│   ├── config.py                 # caminhos, dimensões do Radar, IPCA, sementes
│   ├── estatistica.py            # testes e estimadores (Wilcoxon, Hodges-Lehmann, Spearman com permutação etc.)
│   ├── comum.py                  # recorte das 18 empresas com Radar em T0 e TF
│   ├── 01_extrair_radar.py       # localiza o Radar na base estadual e confere pela Equação 1
│   ├── 02_preparar_base.py       # monta a base analítica (uma linha por empresa)
│   ├── 03_produtividade.py       # produtividade: evolução, testes, sensibilidade, porte, atrito
│   ├── 04_radar.py               # Radar: T0 x TF por dimensão, Bonferroni, confiabilidade, Tabela A1
│   ├── 05_correlacoes.py         # Spearman com permutação, bootstrap, Benjamini-Hochberg e Kendall
│   ├── 06_figuras.py             # figuras do artigo
│   ├── conferir_numeros_artigo.py# confere 50 números do artigo contra os resultados
│   └── gerar_dados_sinteticos.py # base de teste, sem dados reais
├── data/
│   ├── README.md                 # origem, confidencialidade e dicionário de dados
│   ├── raw/                      # dados brutos (não versionados)
│   ├── processed/                # base analítica gerada (não versionada)
│   └── exemplo/                  # base sintética gerada para testes
├── results/                      # tabelas agregadas geradas a partir dos dados reais
├── figures/                      # figuras do artigo
└── docs/
    ├── metodologia.md
    └── mapa_artigo.md
```

## O que não está publicado

- **Dados brutos e base analítica:** pertencem ao Sebrae e são confidenciais (ver [data/README.md](data/README.md)).
- **Tabelas 3, 4 e A1 do artigo:** trazem valores por empresa. O código as gera em `results/` quando roda com os dados reais, mas elas ficam fora do repositório (estão no `.gitignore`).

## Como rodar

Requer Python 3.10 ou superior.

```bash
git clone https://github.com/<usuario>/produtividade-ali-campinas.git
cd produtividade-ali-campinas
python -m venv .venv && source .venv/bin/activate    # no Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Com os dados reais.** Coloque os arquivos descritos em [data/README.md](data/README.md) em `data/raw/` e rode:

```bash
python run_all.py
```

O último passo confere 50 números do artigo e deve terminar com `50 de 50 números conferem com o artigo`.

**Sem os dados (base sintética).** Para testar o código:

```bash
python run_all.py --sintetico
```

As saídas vão para `results/exemplo_sintetico/` e `figures/exemplo_sintetico/`. Os valores são aleatórios e não correspondem aos do artigo.

Cada etapa também pode ser rodada sozinha, de dentro de `src/` (por exemplo, `python 03_produtividade.py`).

## Principais resultados esperados

| Resultado | Valor |
|---|---|
| Produtividade mediana, T0 → TF (24 empresas) | R$ 4.873,48 → R$ 5.863,00 (+20,3%) |
| Variação mediana por empresa (n = 23) | 31,0% |
| Empresas com ganho | 20 de 24 |
| Wilcoxon pareado / efeito r | p = 0,001 / 0,73 |
| Mudança típica (Hodges-Lehmann, IC 95%) | R$ 2.680 (R$ 1.119 a R$ 4.459) |
| Variação mediana deflacionada pelo IPCA | 26,7% (Wilcoxon, p = 0,002) |
| Radar médio, T0 → TF (18 empresas) | 1,89 → 3,32 |
| Alfa de Cronbach do Radar em TF | 0,61 |
| Spearman, ganho no Radar médio × variação da produtividade | ρ = 0,15 (IC 95%: −0,37 a 0,62; p = 0,56) |

## Reprodutibilidade

- **Sementes fixas** (em `src/config.py`): permutação e bootstrap reproduzem exatamente os valores do artigo.
- **Ordem das operações aleatórias:** a ordem em `05_correlacoes.py` também é fixa. Alterar a ordem dos testes muda a sequência aleatória e, com ela, a terceira casa decimal de p-valores e intervalos.
- **Fonte do IPCA:** os valores mensais em `config.py` são da série 433 do Sistema Gerenciador de Séries Temporais do Banco Central.
- **Versões testadas:** Python 3.12, pandas 3.0, NumPy 2.4, SciPy 1.17 e Matplotlib 3.10.

## Como citar

Use os metadados de [CITATION.cff](CITATION.cff). Referência do artigo:

> SANCHES, Rafael Grecco. Desafios da Indústria de Transformação: Resultados do Programa ALI Produtividade em Micro e Pequenas Empresas de Campinas (SP). 2026.

## Licença

O código está sob a licença MIT (ver [LICENSE](LICENSE)). Os dados do Sistema ALI pertencem ao Sebrae e não estão cobertos por ela.

## Contato

Rafael Grecco Sanches, Agente Local de Inovação (ALI) N6 – Sebrae São Paulo.
