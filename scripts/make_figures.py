"""Figures for the paper from results/stats.json. Writes report/fig_modes.png and report/fig_dprime.png."""
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

S = json.load(open("results/stats.json"))
FRAUD, LEGIT = "#2a78d6", "#eb6834"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.edgecolor": INK2,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2})

models = sorted({k.split("|")[0] for k in S["main"]})
modes = ["A", "T1", "T2", "T3"]
names = {"A": "Advice", "T1": "Table", "T2": "Invite", "T3": "Borrow"}

fig, axes = plt.subplots(1, len(models), figsize=(2.3 * len(models), 2.3), sharey=True)
if len(models) == 1:
    axes = [axes]
for ax, m in zip(axes, models):
    st = S["main"].get(f"{m}|default")
    if not st:
        continue
    x = range(len(modes))
    f = [100 * (st["fraud_by_mode"][md] or 0) for md in modes]
    lg = [100 * (st["legit_by_mode"][md] or 0) for md in modes]
    w = 0.38
    ax.bar([i - w / 2 - 0.01 for i in x], f, w, color=FRAUD, label="Fraud", zorder=3)
    ax.bar([i + w / 2 + 0.01 for i in x], lg, w, color=LEGIT, label="Legitimate", zorder=3)
    for i, (a, b) in enumerate(zip(f, lg)):
        ax.text(i - w / 2 - 0.01, a + 1.5, f"{a:.0f}", ha="center", fontsize=6, color=INK)
        ax.text(i + w / 2 + 0.01, b + 1.5, f"{b:.0f}", ha="center", fontsize=6, color=INK)
    ax.set_xticks(list(x), [names[md] for md in modes])
    ax.set_title(m, color=INK, fontsize=9)
    ax.set_ylim(0, 110)
    ax.grid(axis="y", color=GRID, zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
axes[0].set_ylabel("Replies that warn (%)")
fig.suptitle("Warning rate by request type, default system prompt", color=INK, fontsize=9, x=0.02, ha="left")
h_, l_ = axes[0].get_legend_handles_labels()
fig.legend(h_, l_, frameon=False, fontsize=7, ncol=2, loc="upper left", bbox_to_anchor=(0.0, 0.93))
fig.tight_layout(rect=(0, 0, 1, 0.86))
fig.savefig("report/fig_modes.png", dpi=220)

# d' and c per model and system prompt
fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.2))
systems = ["default", "generic", "guardian"]
cols = ["#2a78d6", "#1baf7a", "#6250d6"]
for ax, key, lab in ((axes[0], "task_d", "Sensitivity d′ (higher = tells scam from real)"),
                     (axes[1], "task_c", "Criterion c (lower = warns more)")):
    for j, (s, col) in enumerate(zip(systems, cols)):
        xs, ys, lo, hi = [], [], [], []
        for i, m in enumerate(models):
            st = S["main"].get(f"{m}|{s}")
            if not st or key not in st:
                continue
            xs.append(i + (j - 1) * 0.22)
            ys.append(st[key])
            c = st.get(key + "_ci") or [st[key], st[key]]
            lo.append(st[key] - c[0])
            hi.append(c[1] - st[key])
        ax.errorbar(xs, ys, yerr=[lo, hi], fmt="o", ms=5, color=col, ecolor=col, elinewidth=1.2,
                    capsize=0, label=s, zorder=3)
    ax.axhline(0, color=INK2, lw=0.8)
    ax.set_xticks(range(len(models)), models)
    ax.set_title(lab, color=INK, fontsize=8, loc="left")
    ax.grid(axis="y", color=GRID, zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
axes[0].legend(frameon=False, fontsize=7, title="System prompt", title_fontsize=7)
fig.tight_layout()
fig.savefig("report/fig_dprime.png", dpi=220)
print("figures written")
