# Dados

Os dados vêm do Sistema ALI, mantido pelo Sebrae, e incluem informações financeiras de empresas atendidas pelo programa. Por isso, **não fazem parte deste repositório**. Podem ser solicitados ao autor, sujeitos à autorização do Sebrae.

Para testar o código sem os dados, use a base sintética: `python run_all.py --sintetico`.

## Arquivos esperados em `data/raw/`

| Arquivo | Conteúdo | Usado em |
|---|---|---|
| `Pasta2_campinas.xlsx` | As 29 empresas industriais do ER Campinas: ciclo, porte, cadeia produtiva, situação, encontros, problema, solução e o indicador de produtividade em T0 e TF | etapas 1 e 2 |
| `Base_para_N6_Relatorio_Estadual_e_Radar.xlsx` | Base estadual do programa, com o Radar de Inovação | etapa 1 |
| `Campinas_Base_N6_Radar.xlsx` (opcional) | Radar já extraído para as 29 empresas (aba `Campinas_Base_N6`). Substitui a etapa 1 quando a base estadual não está disponível | etapa 2 |

## Base analítica (`data/processed/base_analitica.csv`)

Uma linha por empresa. As descrições livres de problema e de solução ficam de fora, para reduzir o risco de identificação. As empresas aparecem só pelo código.

| Coluna | Descrição |
|---|---|
| `codigo` | Código anônimo da empresa (E####) |
| `ciclo` | Ciclo de atendimento (`2025_2ºsem` = Ciclo 2; `2026_1ºsem` = Ciclo 3) |
| `cnae` | CNAE principal |
| `porte` | MEI, ME ou EPP |
| `cadeia_produtiva`, `subsegmento` | Classificação setorial do Sebrae |
| `desistiu`, `descontinuada` | Situação no programa (verdadeiro/falso) |
| `encontros` | Número de encontros da Jornada ALI realizados |
| `categoria_problema`, `categoria_solucao` | Categorias do problema diagnosticado e da solução proposta |
| `faturamento_t0`, `faturamento_tf` | Faturamento bruto do mês de referência (R$, valores nominais) |
| `custos_t0`, `custos_tf` | Custos variáveis do mês de referência (R$) |
| `pessoas_t0`, `pessoas_tf` | Pessoas ocupadas (colaboradores diretos, sócios e familiares atuantes) |
| `produtividade_t0`, `produtividade_tf` | (faturamento − custos variáveis) ÷ pessoas ocupadas (Equação 1) |
| `radar_XX_t0`, `radar_XX_tf` | Notas do Radar de Inovação (1 a 5). XX: `cg` controles gerenciais, `go` gestão de operações, `mk` marketing, `ps` práticas sustentáveis, `pi` práticas de inovação, `td` transformação digital |
| `concluiu` | Verdadeiro quando há mensuração final (TF) |

Valores ausentes ficam vazios. No Radar, uma nota com registros conflitantes na base estadual também fica vazia (é o caso da E4531 em práticas sustentáveis, T0).
