"""Etapa 6 – Figuras do artigo (seção 4 e Apêndice A).

  fig01_categorias_problema.png   Figura 1  – categoria do problema diagnosticado (n = 29)
  fig02_boxplot_produtividade.png Figura 2  – boxplot da produtividade em T0 e TF (n = 24)
  fig03_produtividade_porte.png   Figura 3  – produtividade média por porte (MEI sem base negativa)
  fig04a_ranking_variacao.png     Figura 4a – ranking da variação percentual por empresa
  fig04b_produtividade_log.png    Figura 4b – produtividade inicial e final por empresa (escala log)
  fig05_faturamento_porte.png     Figura 5  – faturamento bruto inicial e final por empresa
  fig06_radar_medio.png           Figura 6  – Radar de Inovação médio em T0 e TF (n = 18)
  figA1_radares_empresas.png      Figura A1 – Radar de cada empresa em T0 e TF

Entrada : data/processed/base_analitica.csv      Saída : figures/
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
from config import BASE_ANALITICA, FIGURAS, DIMENSOES
from comum import recorte_radar

AZUL, VERDE, CINZA, VERMELHO = "#1B2A4A", "#2A9D8F", "#8D99AE", "#E63946"
AMARELO, LARANJA = "#E9C46A", "#F4A261"
reais = FuncFormatter(lambda v, p: "R$ " + f"{v:,.0f}".replace(",", "."))
virg = lambda v, d=2: f"{v:.{d}f}".replace(".", ",")


def salvar(fig, nome):
    fig.savefig(FIGURAS / nome, dpi=300, bbox_inches="tight", facecolor="white"); plt.close(fig)


def fig01(b):
    cat = b["categoria_problema"].fillna("Não classificado / ciclo em andamento").value_counts()
    cores = [AZUL, VERDE, AMARELO, LARANJA, VERMELHO, CINZA, "#6D6875", "#B5838D", "#1D3557", "#2A9D8F", "#E9C46A"]
    fig, ax = plt.subplots(figsize=(10, 6))
    w, _, aut = ax.pie(cat.values, colors=cores[: len(cat)], startangle=90, counterclock=False,
                       wedgeprops=dict(width=0.42, edgecolor="white"), autopct="%1.1f%%", pctdistance=0.79)
    for a in aut:
        a.set_color("white"); a.set_fontsize(9); a.set_fontweight("bold"); a.set_text(a.get_text().replace(".", ","))
    ax.legend(w, [f"{k} (n={v})" for k, v in cat.items()], title="Categoria do problema", loc="center left", bbox_to_anchor=(1, 0.5), fontsize=9)
    ax.set_title(f"Gargalos diagnosticados — categoria do problema (n={len(b)})", fontweight="bold", color=AZUL)
    salvar(fig, "fig01_categorias_problema.png")


def fig02(c):
    fig, ax = plt.subplots(figsize=(6.5, 4.6))
    bp = ax.boxplot([c["produtividade_t0"], c["produtividade_tf"]], widths=0.55, patch_artist=True,
                    medianprops=dict(color=AZUL, lw=2), flierprops=dict(marker="o", markerfacecolor=VERMELHO, markeredgecolor=VERMELHO, alpha=0.8))
    for patch, cor in zip(bp["boxes"], [CINZA, VERDE]):
        patch.set_facecolor(cor); patch.set_alpha(0.75)
    ax.set_xticks([1, 2]); ax.set_xticklabels(["Produtividade\ninicial", "Produtividade\nfinal"])
    ax.yaxis.set_major_formatter(reais); ax.set_ylabel("R$ / pessoa ocupada")
    ax.grid(axis="y", ls="--", color="#E4E4E4"); ax.set_axisbelow(True)
    ax.set_title(f"Distribuição da produtividade — inicial e final (n={len(c)})", fontweight="bold", color=AZUL)
    salvar(fig, "fig02_boxplot_produtividade.png")


def fig03(c):
    g = c[c["produtividade_t0"] > 0].groupby("porte").agg(n=("codigo", "size"), t0=("produtividade_t0", "mean"), tf=("produtividade_tf", "mean"))
    g = g.reindex([p for p in ("MEI", "ME", "EPP") if p in g.index])
    excl = c.loc[c["produtividade_t0"] <= 0, "porte"].tolist()
    fig, ax = plt.subplots(figsize=(6.5, 4.6)); x = np.arange(len(g)); w = 0.35
    ax.bar(x - w / 2, g["t0"], w, color=CINZA, label="Inicial"); ax.bar(x + w / 2, g["tf"], w, color=VERDE, label="Final")
    for i, (a, f) in enumerate(zip(g["t0"], g["tf"])):
        ax.text(i + w / 2, f + 350, f"+{(f / a - 1) * 100:.0f}%", ha="center", va="bottom", fontweight="bold", color=AZUL)
    ax.set_xticks(x); ax.set_xticklabels([f"{p}\n(n={n})" + ("*" if p in excl else "") for p, n in zip(g.index, g["n"])])
    ax.set_ylim(0, max(g["tf"]) * 1.17); ax.yaxis.set_major_formatter(reais); ax.set_ylabel("Produtividade média (R$/pessoa)")
    ax.grid(axis="y", ls="--", color="#E4E4E4"); ax.set_axisbelow(True); ax.legend(loc="upper left")
    ax.set_title("Produtividade média por porte — inicial vs. final", fontweight="bold", color=AZUL)
    if excl:
        fig.text(0.99, -0.03, "* sem a empresa de produtividade inicial negativa", ha="right", fontsize=8, color="#555555")
    salvar(fig, "fig03_produtividade_porte.png")


def ordem_ranking(c):
    v = c.assign(var=np.where(c["produtividade_t0"] > 0, (c["produtividade_tf"] / c["produtividade_t0"] - 1) * 100, np.nan))
    return pd.concat([v[v["var"].notna()].sort_values("var", ascending=False), v[v["var"].isna()]])


def fig04a(c):
    v = ordem_ranking(c); v = v[v["var"].notna()]
    fig, ax = plt.subplots(figsize=(6.6, 8))
    y = np.arange(len(v))[::-1]
    ax.barh(y, v["var"], color=[VERDE if x >= 0 else VERMELHO for x in v["var"]])
    for yi, x in zip(y, v["var"]):
        ax.text(x + (8 if x >= 0 else -8), yi, f"{x:+.0f}%", va="center", ha="left" if x >= 0 else "right", fontsize=8, fontweight="bold", color=AZUL)
    ax.axvline(0, color="black", lw=0.8); ax.set_yticks(y); ax.set_yticklabels(v["codigo"])
    ax.set_xlim(min(v["var"].min() - 70, -150), v["var"].max() + 90)
    ax.set_xlabel("Variação da produtividade (%)"); ax.grid(axis="x", ls="--", color="#E4E4E4"); ax.set_axisbelow(True)
    ax.set_title(f"Ranking da variação da produtividade ({len(v)} empresas)", fontweight="bold", color=AZUL)
    salvar(fig, "fig04a_ranking_variacao.png")


def fig04b(c):
    d = ordem_ranking(c)
    fig, ax = plt.subplots(figsize=(8.5, 10.25)); ys = np.arange(len(d))[::-1]
    for yi, (_, r) in zip(ys, d.iterrows()):
        cor = VERDE if r["produtividade_tf"] > r["produtividade_t0"] else VERMELHO
        x0, x1 = max(r["produtividade_t0"], 1), max(r["produtividade_tf"], 1)
        ax.plot([x0, x1], [yi, yi], color=cor, lw=2.5, alpha=0.8, zorder=1)
        for x, bruto, cc in ((x0, r["produtividade_t0"], CINZA), (x1, r["produtividade_tf"], cor)):
            if bruto <= 0:
                ax.scatter(x, yi, s=70, facecolors="white", edgecolors=cc, linewidths=2, zorder=3)
            else:
                ax.scatter(x, yi, s=70, color=cc, zorder=3)
    ax.set_xscale("log"); ax.set_yticks(ys); ax.set_yticklabels(d["codigo"], fontsize=11); ax.set_ylim(-0.8, len(d) - 0.2)
    ax.set_xlabel("Produtividade (R$/pessoa, escala log)", fontsize=13)
    ax.grid(axis="x", ls="--", color="#E4E4E4"); ax.set_axisbelow(True)
    leg = [Line2D([0], [0], marker="o", color="w", markerfacecolor=CINZA, markersize=9, label="inicial (T0)"),
           Line2D([0], [0], marker="o", color=VERDE, lw=2.5, markerfacecolor=VERDE, markersize=9, label="final (TF), melhora"),
           Line2D([0], [0], marker="o", color=VERMELHO, lw=2.5, markerfacecolor=VERMELHO, markersize=9, label="final (TF), piora"),
           Line2D([0], [0], marker="o", color="w", markerfacecolor="white", markeredgecolor="#555555", markeredgewidth=2, markersize=9, label="valor ≤ 0, fixado em R$ 1")]
    ax.legend(handles=leg, loc="upper left", fontsize=10)
    salvar(fig, "fig04b_produtividade_log.png")


def fig05(c):
    fig, ax = plt.subplots(figsize=(7, 6))
    for prt, cor in (("EPP", VERDE), ("ME", AZUL), ("MEI", LARANJA)):
        g = c[c["porte"] == prt]
        ax.scatter(g["faturamento_t0"], g["faturamento_tf"], s=60, color=cor, alpha=0.85, label=prt)
    lim = max(c["faturamento_t0"].max(), c["faturamento_tf"].max()) * 1.05
    ax.plot([0, lim], [0, lim], ls="--", color="#999999", lw=1, label="Sem variação (y = x)")
    ax.set_xlim(0, lim); ax.set_ylim(0, lim)
    k = FuncFormatter(lambda v, p: f"{v / 1000:.0f}k"); ax.xaxis.set_major_formatter(k); ax.yaxis.set_major_formatter(k)
    ax.set_xlabel("Faturamento bruto inicial (R$)"); ax.set_ylabel("Faturamento bruto final (R$)")
    ax.grid(ls="--", color="#E4E4E4"); ax.set_axisbelow(True); ax.legend(loc="upper left")
    ax.set_title("Faturamento bruto — inicial vs. final\n(acima da linha tracejada = empresa cresceu)", fontweight="bold", color=AZUL, fontsize=11)
    salvar(fig, "fig05_faturamento_porte.png")


def fig06_A1(D):
    rot = [r for _, r, _ in DIMENSOES]; sig = ["CG", "GO", "MK", "PS", "PI", "TD"]
    ang = np.linspace(0, 2 * np.pi, 6, endpoint=False).tolist(); ac = ang + ang[:1]
    ini = [D.loc[D[f"{r}|TF"].notna() & D[f"{r}|T0"].notna(), f"{r}|T0"].mean() for r in rot]
    fin = [D.loc[D[f"{r}|TF"].notna() & D[f"{r}|T0"].notna(), f"{r}|TF"].mean() for r in rot]
    quebra = {r: r.replace(" ", "\n", 1) if r != "Marketing" else r for r in rot}
    fig = plt.figure(figsize=(5.2, 4.3)); ax = plt.subplot(111, polar=True)
    ax.set_theta_offset(np.pi / 2); ax.set_theta_direction(-1); ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5]); ax.set_yticklabels(list("12345"), fontsize=7, color="#595959"); ax.set_rlabel_position(30)
    ax.set_xticks(ang); ax.set_xticklabels([])
    for a, r in zip(ang, rot):
        g = np.degrees(a) % 360
        ax.text(a, 5.55, quebra[r], ha="center" if g in (0, 180) else ("left" if g < 180 else "right"),
                va="bottom" if g == 0 else ("top" if g == 180 else "center"), fontsize=9)
    for vals, cor, lab in ((ini, CINZA, "T0 (inicial)"), (fin, AZUL, "TF (final)")):
        ax.plot(ac, vals + vals[:1], color=cor, lw=1.8, marker="o", ms=4, label=lab); ax.fill(ac, vals + vals[:1], color=cor, alpha=0.15)
    for a, v in zip(ang, fin): ax.text(a, v + 0.5, virg(v), ha="center", va="center", fontsize=7.5, color=AZUL, fontweight="bold")
    for a, v in zip(ang, ini): ax.text(a, max(v - 0.6, 0.5), virg(v), ha="center", va="center", fontsize=7, color="#595959")
    ax.spines["polar"].set_color("#BFBFBF"); ax.grid(color="#D9D9D9")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=2, frameon=False, fontsize=8.5)
    salvar(fig, "fig06_radar_medio.png")

    fig, axs = plt.subplots(3, 6, figsize=(9, 5.2), subplot_kw=dict(polar=True))
    for ax, (_, r) in zip(axs.flat, D.iterrows()):
        ax.set_theta_offset(np.pi / 2); ax.set_theta_direction(-1); ax.set_ylim(0, 5)
        ax.set_yticks([1, 2, 3, 4, 5]); ax.set_yticklabels([]); ax.set_xticks(ang); ax.set_xticklabels(sig, fontsize=8); ax.tick_params(axis="x", pad=-3)
        for s, cor in (("T0", CINZA), ("TF", AZUL)):
            arr = [float(r[f"{x}|{s}"]) if pd.notna(r[f"{x}|{s}"]) else np.nan for x in rot]
            ax.plot(ac, arr + arr[:1], color=cor, lw=1.3, marker="o", ms=2.2)     # valor ausente interrompe a linha
            if not any(np.isnan(arr)):
                ax.fill(ac, arr + arr[:1], color=cor, alpha=0.15)
        ax.set_title(r["codigo"], fontsize=10, pad=6, fontweight="bold"); ax.spines["polar"].set_color("#BFBFBF"); ax.grid(color="#E0E0E0", lw=0.6)
    for ax in list(axs.flat)[len(D):]:
        ax.axis("off")
    fig.legend(handles=[Line2D([0], [0], color=CINZA, marker="o", lw=1.8, label="T0 (inicial)"), Line2D([0], [0], color=AZUL, marker="o", lw=1.8, label="TF (final)")],
               loc="lower center", ncol=2, frameon=False, fontsize=9.5, bbox_to_anchor=(0.5, -0.01))
    plt.subplots_adjust(hspace=0.55, wspace=0.45, bottom=0.09, top=0.93, left=0.02, right=0.98)
    salvar(fig, "figA1_radares_empresas.png")


def main():
    b = pd.read_csv(BASE_ANALITICA); c = b[b["concluiu"]]
    fig01(b); fig02(c); fig03(c); fig04a(c); fig04b(c); fig05(c); fig06_A1(recorte_radar(b))
    print("Figuras salvas em", FIGURAS)


if __name__ == "__main__":
    main()
