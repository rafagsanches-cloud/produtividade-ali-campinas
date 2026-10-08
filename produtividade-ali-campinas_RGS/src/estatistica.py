"""Funções estatísticas usadas no artigo.

Todas são não paramétricas, adequadas a amostras pequenas, a valores extremos
e à escala ordinal do Radar de Inovação.
"""
import numpy as np
from scipy import stats


# ---------------------------------------------------------------------------
# Comparações pareadas (T0 x TF)
# ---------------------------------------------------------------------------
def wilcoxon_pareado(depois, antes, metodo="auto"):
    """Teste de Wilcoxon pareado (pares sem mudança são descartados).

    metodo="auto": exato quando não há empates nem diferenças nulas; caso
    contrário, aproximação normal (é o caso do Radar, cheio de empates).
    """
    depois = np.asarray(depois, float); antes = np.asarray(antes, float)
    d = depois - antes
    if metodo == "auto":
        nz = d[d != 0]
        metodo = "approx" if (np.any(d == 0) or len(np.unique(np.abs(nz))) < len(nz)) else "exact"
    r = stats.wilcoxon(depois, antes, zero_method="wilcox", method=metodo)
    return float(r.pvalue), metodo


def rank_bisserial(d):
    """Tamanho de efeito r rank-bisserial para dados pareados (de -1 a 1)."""
    d = np.asarray(d, float); d = d[d != 0]
    r = stats.rankdata(np.abs(d))
    return float((r[d > 0].sum() - r[d < 0].sum()) / r.sum())


def hodges_lehmann(d):
    """Mediana das médias de Walsh: estimativa robusta da mudança típica."""
    d = np.asarray(d, float)
    w = [(d[i] + d[j]) / 2 for i in range(len(d)) for j in range(i, len(d))]
    return float(np.median(w))


def hodges_lehmann_ic(d, n_boot, semente):
    """IC 95% bootstrap (percentil) do estimador de Hodges-Lehmann."""
    d = np.asarray(d, float)
    rng = np.random.default_rng(semente)
    est = [hodges_lehmann(d[rng.integers(0, len(d), len(d))]) for _ in range(n_boot)]
    return np.percentile(est, [2.5, 97.5])


def teste_do_sinal(d):
    d = np.asarray(d, float)
    sobe, desce = int(np.sum(d > 0)), int(np.sum(d < 0))
    return float(stats.binomtest(sobe, sobe + desce, 0.5).pvalue)


# ---------------------------------------------------------------------------
# Correlação de Spearman com permutação e bootstrap
# ---------------------------------------------------------------------------
def _corr_linhas(a, b):
    a = a - a.mean(axis=1, keepdims=True); b = b - b.mean(axis=1, keepdims=True)
    den = np.sqrt((a * a).sum(1) * (b * b).sum(1))
    with np.errstate(invalid="ignore", divide="ignore"):
        return (a * b).sum(1) / den


def spearman_permutacao(x, y, rng, n=20000):
    """p bilateral por permutação: proporção de |rho| embaralhado >= |rho| observado."""
    rx = stats.rankdata(x); ry = stats.rankdata(y)
    r0 = _corr_linhas(rx[None, :], ry[None, :])[0]
    P = np.array([rng.permutation(ry) for _ in range(n)])
    rp = _corr_linhas(np.repeat(rx[None, :], n, 0), P)
    return float((np.sum(np.abs(rp) >= abs(r0) - 1e-12) + 1) / (n + 1))


def spearman_bootstrap_ic(x, y, rng, n=10000):
    """IC 95% bootstrap (percentil) do rho de Spearman."""
    m = len(x); I = rng.integers(0, m, (n, m))
    rx = stats.rankdata(x[I], axis=1); ry = stats.rankdata(y[I], axis=1)
    rs = _corr_linhas(rx, ry); rs = rs[~np.isnan(rs)]
    return np.percentile(rs, [2.5, 97.5])


def benjamini_hochberg(p):
    """q-valores de Benjamini-Hochberg (controle da taxa de falsas descobertas)."""
    p = np.array(p, float); m = int(np.sum(~np.isnan(p)))
    ordem = np.argsort(np.where(np.isnan(p), np.inf, p))
    q = np.full_like(p, np.nan); anterior = 1.0
    for k in range(m - 1, -1, -1):
        i = ordem[k]; anterior = min(anterior, p[i] * m / (k + 1)); q[i] = anterior
    return q


# ---------------------------------------------------------------------------
# Confiabilidade do Radar e poder estatístico
# ---------------------------------------------------------------------------
def alfa_cronbach(X):
    """Alfa de Cronbach (empresas x dimensões); linhas incompletas são descartadas."""
    X = np.asarray(X, float); X = X[~np.isnan(X).any(axis=1)]
    k = X.shape[1]
    return float(k / (k - 1) * (1 - X.var(axis=0, ddof=1).sum() / X.sum(axis=1).var(ddof=1))), len(X)


def rho_minimo_detectavel(n, alfa=0.05, poder=0.80):
    """|rho| mínimo detectável (aproximação de Fisher, variância 1,06/(n-3))."""
    z = (stats.norm.ppf(1 - alfa / 2) + stats.norm.ppf(poder)) * np.sqrt(1.06 / (n - 3))
    return float(np.tanh(z))
