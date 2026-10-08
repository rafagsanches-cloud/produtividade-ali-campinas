# Onde está cada resultado do artigo

| Elemento do artigo | Script | Saída |
|---|---|---|
| Recortes da amostra (29 → 24 → 18), seção 3 | `02_preparar_base.py`, `03_produtividade.py` | `results/tabela_1_situacao.csv` |
| Intervenção: encontros e soluções, seção 3 | `03_produtividade.py` | `results/produtividade_numeros.csv` (`encontros_*`), `results/solucoes_24_empresas.csv` |
| Consolidação da base estadual e conferência pela Equação 1 | `01_extrair_radar.py` | `data/processed/radar.csv` |
| Tabela 1 – situação das 29 empresas | `03_produtividade.py` | `results/tabela_1_situacao.csv` |
| Tabela 2 – cadeia produtiva | `03_produtividade.py` | `results/tabela_2_cadeia_produtiva.csv` |
| Porte das 29 empresas | `03_produtividade.py` | `results/porte_29_empresas.csv` |
| Figura 1 – categorias do problema | `06_figuras.py` | `figures/fig01_categorias_problema.png` |
| Medianas, médias, Wilcoxon, Hodges-Lehmann, efeito | `03_produtividade.py` | `results/produtividade_numeros.csv` |
| Médias robustas, regressão à média, deflação pelo IPCA | `03_produtividade.py` | `results/produtividade_numeros.csv` |
| Figura 2 – boxplot | `06_figuras.py` | `figures/fig02_boxplot_produtividade.png` |
| Seção 4.1 e Figura 3 – porte | `03_produtividade.py`, `06_figuras.py` | `results/porte_produtividade.csv`, `figures/fig03_produtividade_porte.png` |
| Alimentos e bebidas (16,8%) | `03_produtividade.py` | `results/cadeia_produtividade.csv` |
| Tabela 3 – maiores ganhos | `03_produtividade.py` | `results/tabela_3_maiores_ganhos.csv` (gerada localmente; não publicada) |
| Tabela 4 – quedas | `03_produtividade.py` | `results/tabela_4_quedas.csv` (gerada localmente; não publicada) |
| Figuras 4a e 4b | `06_figuras.py` | `figures/fig04a_ranking_variacao.png`, `figures/fig04b_produtividade_log.png` |
| Faturamento, custos e pessoal; quadro fixo | `03_produtividade.py` | `results/produtividade_numeros.csv` |
| Figura 5 – faturamento | `06_figuras.py` | `figures/fig05_faturamento_porte.png` |
| Atrito (Mann-Whitney) | `03_produtividade.py` | `results/produtividade_numeros.csv`, `results/atrito_por_cadeia.csv` |
| Seção 4.2 – Radar por dimensão, Bonferroni | `04_radar.py` | `results/radar_dimensoes.csv` |
| Confiabilidade do Radar (alfa de Cronbach) | `04_radar.py` | `results/radar_confiabilidade.csv` |
| Figura 6 – Radar médio | `06_figuras.py` | `figures/fig06_radar_medio.png` |
| Tabela de correlações de Spearman | `05_correlacoes.py` | `results/correlacoes.csv` (recortes A e B) |
| Apêndice A – Tabela A1 e Figura A1 | `04_radar.py`, `06_figuras.py` | `results/tabela_A1_radar_por_empresa.csv` (gerada localmente; não publicada), `figures/figA1_radares_empresas.png` |
| Conferência de 50 números do artigo | `conferir_numeros_artigo.py` | `results/conferencia_artigo.csv` |
