# Metodologia

Este documento descreve, passo a passo, o que o código faz e por quê. A ordem segue a do artigo.

## 1. Dados e recorte da amostra

Os dados são do Sistema ALI, preenchidos pelos Agentes Locais de Inovação no diagnóstico (T0) e na mensuração final (TF) de cada ciclo da Jornada ALI Produtividade. O recorte é o Escritório Regional de Campinas (SP), nos Ciclos 2 (2º semestre de 2025) e 3 (1º semestre de 2026).

A amostra passa por dois recortes:

1. **29 empresas industriais atendidas.** Cinco não têm mensuração final: duas com o ciclo em andamento, duas desistentes e uma descontinuada.
2. **24 empresas com produtividade em T0 e TF.** É a amostra das análises de produtividade.
3. **18 empresas com Radar de Inovação em T0 e TF.** As outras seis não constam da base estadual do Radar. É a amostra das análises do Radar e das correlações.

As 24 concluintes fizeram os nove encontros da jornada. As que saíram pararam entre o segundo e o sétimo.

## 2. Indicador de produtividade

**Equação 1 – produtividade (valor adicionado por pessoa ocupada):**

    produtividade = (faturamento bruto − custos variáveis) / pessoas ocupadas

**Equação 2 – variação percentual entre T0 e TF:**

    variação (%) = [(produtividade_TF / produtividade_T0) − 1] × 100

A Equação 2 é usada de duas formas, e o artigo distingue as duas:

- **sobre o grupo**: variação da mediana (+20,3%) e da média (+63,5%) das 24 empresas;
- **empresa a empresa**: mediana (31,0%) e média (96,7%) das variações individuais.

Na forma individual, a E4664 fica de fora porque sua produtividade inicial é negativa, o que torna a variação percentual indefinida. Os valores são nominais e se referem a um mês em T0 e outro em TF, dentro do mesmo ciclo semestral.

## 3. Consolidação da base estadual (etapa 1)

A base estadual organiza as informações em dois blocos de colunas, e as linhas de um bloco não correspondem às do outro. Por isso, cada empresa é localizada separadamente:

- **bloco A** (colunas A a P): pela descrição do problema e da solução, custos, CNAE, ciclo e porte. Daqui sai a dimensão *controles gerenciais* do Radar;
- **bloco B** (colunas S a AL): pelo faturamento, pessoas ocupadas, produtividade, encontro e situação. Daqui saem as outras cinco dimensões.

O par encontrado é conferido pela Equação 1: a produtividade registrada no bloco B precisa ser igual a (faturamento do bloco B − custos do bloco A) / pessoas do bloco B. As 18 empresas com Radar completo passam nessa conferência.

## 4. Evolução da produtividade (etapa 3)

| Procedimento | Por quê |
|---|---|
| **Teste de Wilcoxon pareado** (exato) | Compara T0 e TF dentro de cada empresa sem supor distribuição normal. As diferenças não são normais (Shapiro-Wilk, p = 0,0002) e há casos extremos. |
| **Teste do sinal** | Confirmação simples: conta só quantas empresas subiram e quantas caíram. |
| **Estimador de Hodges-Lehmann** | Mudança típica em reais, pouco sensível a valores extremos. IC 95% por bootstrap (5.000 reamostragens, semente 11). |
| **r rank-bisserial** | Tamanho de efeito, de −1 a 1. |
| **Média aparada e winsorizada a 10%** | Mostram que o sentido do resultado não depende dos casos extremos. |

**Verificações de sensibilidade:**

- **sem as empresas atípicas** (E4664, de base negativa, e E4367, de faturamento final nulo);
- **regressão à média**: correlação de Spearman entre a produtividade inicial e a variação;
- **variação de preços**: a produtividade de TF é deflacionada pelo IPCA acumulado no semestre de cada ciclo (série 433 do Banco Central): 1,24% no Ciclo 2 e 3,36% no Ciclo 3. Como T0 e TF ficam dentro do mesmo semestre, a correção é conservadora;
- **pessoal ocupado**: o valor adicionado total por pessoa é recalculado mantendo o quadro de T0, para separar o efeito da redução de pessoal.

**Atrito:** a produtividade inicial das empresas sem TF é comparada à das concluintes pelo teste de Mann-Whitney.

**Porte:** médias e medianas das variações de produtividade, faturamento e custos. A E4664 fica fora das três medidas dos MEI pelo mesmo motivo da seção 2.

## 5. Radar de Inovação (etapa 4)

O Radar pontua seis dimensões de 1 a 5: controles gerenciais, gestão de operações, marketing, práticas sustentáveis, práticas de inovação e transformação digital. O Radar médio é a média das dimensões disponíveis de cada empresa.

- **Mudança entre T0 e TF:** teste de Wilcoxon pareado com aproximação normal (há muitos empates), com correção de Bonferroni para as seis dimensões (limiar 0,05/6 = 0,0083).
- **Confiabilidade:** alfa de Cronbach e correlação média de Spearman entre as dimensões. Em TF, alfa = 0,61. Em T0, duas dimensões não variam (todas as empresas na nota 2), o que torna o alfa pouco informativo. A concordância entre avaliadores não pode ser estimada, porque cada empresa foi pontuada por um único agente.

## 6. Correlação entre Radar e produtividade (etapa 5)

| Procedimento | Por quê |
|---|---|
| **Spearman (ρ)** | Trabalha com a ordem dos valores; não é distorcido pela escala ordinal do Radar nem pelos extremos de produtividade, como seria Pearson. |
| **p por permutação** | 20.000 reordenações aleatórias; não depende de aproximações, o que importa com 17 ou 18 empresas. |
| **IC 95% por bootstrap** | 10.000 reamostragens (percentil). |
| **Benjamini-Hochberg** | Controla os falsos positivos dentro de cada bloco de sete testes. |
| **τ-b de Kendall** | Confirmação, mais robusta a empates. |

São quatro recortes: ganho no Radar × variação percentual (A, n = 17), ganho × variação em reais (A2, n = 18), níveis em TF (B) e níveis em T0 (C). A semente (20261002) e a ordem das operações são fixas para reproduzir os valores do artigo.

**Poder:** com 17 ou 18 empresas, só correlações de módulo próximo de 0,63 ou mais seriam detectadas com 80% de probabilidade. A ausência de significância não prova ausência de relação.

## 7. Limitações

- Não há grupo de controle. As mudanças observadas não podem ser atribuídas só ao programa.
- Os valores são nominais e se referem a um único mês em cada momento, o que os sujeita à sazonalidade.
- O indicador usa pessoas ocupadas, e não horas trabalhadas.
- O Radar é aplicado pelo mesmo agente que conduz o atendimento, sem validação externa.
- Alguns grupos, como os portes MEI e EPP, têm poucas empresas.
