"""Generate report charts (dataset, results, Gantt) and equation images.

    uv run python report/tools/make_charts.py
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "report" / "figures" / "generated"
EQ = ROOT / "report" / "figures" / "equations"
OUT.mkdir(parents=True, exist_ok=True)
EQ.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"], "font.size": 11})

LABELS = {
    "age": "Age", "anaemia": "Anaemia", "creatinine_phosphokinase": "CPK", "diabetes": "Diabetes",
    "ejection_fraction": "Ejection Fraction", "high_blood_pressure": "High BP", "platelets": "Platelets",
    "serum_creatinine": "Serum Creatinine", "serum_sodium": "Serum Sodium", "sex": "Sex", "smoking": "Smoking",
    "time": "Follow-up Time", "DEATH_EVENT": "Death Event",
}


def class_distribution():
    uci = pd.read_csv(ROOT / "data" / "heart_failure_clinical_records_uci.csv")
    full = pd.read_csv(ROOT / "data" / "heart_failure_clinical_records_2000.csv")
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.6))
    for ax, df, title in ((axes[0], uci, "Original UCI dataset (n = 299)"), (axes[1], full, "Expanded dataset (n = 2000)")):
        counts = df["DEATH_EVENT"].value_counts().sort_index()
        bars = ax.bar(["Survived (0)", "Death event (1)"], counts.values, color=["#4ade80", "#f87171"], edgecolor="black")
        for b, v in zip(bars, counts.values):
            ax.text(b.get_x() + b.get_width() / 2, v, f"{v} ({v / len(df):.0%})", ha="center", va="bottom")
        ax.set_title(title)
        ax.set_ylabel("Patients")
        ax.set_ylim(0, counts.max() * 1.18)
    fig.tight_layout()
    fig.savefig(OUT / "class_distribution.png", dpi=200)
    plt.close(fig)


def correlation():
    df = pd.read_csv(ROOT / "data" / "heart_failure_clinical_records_uci.csv").rename(columns=LABELS)
    fig, ax = plt.subplots(figsize=(8, 6.5))
    sns.heatmap(df.corr(), annot=True, fmt=".2f", cmap="RdBu_r", center=0, vmin=-1, vmax=1, ax=ax,
                annot_kws={"size": 8}, cbar_kws={"shrink": 0.8})
    ax.set_title("Correlation Matrix of Clinical Features (UCI dataset)")
    fig.tight_layout()
    fig.savefig(OUT / "correlation.png", dpi=200)
    plt.close(fig)


def confusion_grid():
    metrics = json.loads((ROOT / "reports" / "metrics.json").read_text())["models"]
    fig, axes = plt.subplots(2, 3, figsize=(11, 6.6))
    for ax, (key, m) in zip(axes.flat, metrics.items()):
        sns.heatmap(m["confusion_matrix"], annot=True, fmt="d", cmap="Blues", cbar=False, ax=ax,
                    xticklabels=["Pred. Alive", "Pred. Dead"], yticklabels=["Actual Alive", "Actual Dead"],
                    annot_kws={"size": 13})
        ax.set_title(m["name"].replace(" (SVM)", ""), fontsize=12)
    fig.tight_layout()
    fig.savefig(OUT / "confusion_all.png", dpi=200)
    plt.close(fig)


def metric_bars():
    metrics = json.loads((ROOT / "reports" / "metrics.json").read_text())["models"]
    df = pd.DataFrame(
        {m["name"].replace("Support Vector Machine (SVM)", "SVM"): m["test"] for m in metrics.values()}
    ).T[["accuracy", "precision", "recall", "f1", "roc_auc"]]
    df.columns = ["Accuracy", "Precision", "Recall", "F1-score", "ROC-AUC"]
    ax = df.plot(kind="bar", figsize=(10, 4.6), width=0.8, edgecolor="black", linewidth=0.4,
                 color=["#93c5fd", "#a78bfa", "#f9a8d4", "#fcd34d", "#86efac"])
    ax.set_ylim(0, 1)
    ax.set_ylabel("Score")
    ax.set_title("Test-set Performance of the Six Classifiers")
    ax.legend(ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.22), frameon=False)
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(OUT / "metric_comparison.png", dpi=200)
    plt.close()


def gantt():
    # Project timeline from the team's work schedule.
    tasks = [
        ("Research & Analysis", "2025-01-01", "2025-02-15"),
        ("Tool Familiarization", "2025-01-15", "2025-02-28"),
        ("Design & Coding", "2025-03-01", "2025-05-31"),
        ("Testing & Debugging", "2025-04-16", "2025-06-15"),
        ("Documentation & Report", "2025-05-16", "2025-06-30"),
    ]
    fig, ax = plt.subplots(figsize=(9, 3.4))
    colors = ["#93c5fd", "#a78bfa", "#f9a8d4", "#fcd34d", "#86efac"]
    for i, (name, start, end) in enumerate(reversed(tasks)):
        s, e = pd.Timestamp(start), pd.Timestamp(end)
        ax.barh(i, (e - s).days, left=mdates.date2num(s), color=colors[len(tasks) - 1 - i], edgecolor="black")
    ax.set_yticks(range(len(tasks)))
    ax.set_yticklabels([t[0] for t in reversed(tasks)])
    ax.xaxis_date()
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.grid(axis="x", linestyle=":", alpha=0.6)
    ax.set_title("Project Schedule (January - June 2025)")
    fig.tight_layout()
    fig.savefig(OUT / "gantt.png", dpi=200)
    plt.close(fig)


EQUATIONS = {
    "standardize": r"$z_{ij} = \dfrac{x_{ij} - \mu_j}{\sigma_j}$",
    "rf_prob": r"$P(\mathrm{HF} \mid X_i) = \dfrac{1}{N}\sum_{k=1}^{N} p_k(X_i)$",
    "threshold": r"$\hat{y}_i = 1$ if $P(\mathrm{HF} \mid X_i) \geq \theta$, otherwise $0$,  with $\theta = 0.5$",
    "entropy": r"$\mathrm{Entropy}(S) = -\sum_{i=1}^{c} p_i \log_2 p_i$",
    "gini": r"$\mathrm{Gini}(S) = 1 - \sum_{i=1}^{c} p_i^2$",
    "info_gain": r"$\mathrm{Gain}(S, A) = \mathrm{Entropy}(S) - \sum_{v \in \mathrm{Values}(A)} \dfrac{|S_v|}{|S|}\,\mathrm{Entropy}(S_v)$",
    "leaf": r"$\mathrm{Leaf} = \arg\max_{c}\, P(c)$",
    "xgb_obj": r"$\mathcal{L}^{(t)} = \sum_{i=1}^{n} l\left(y_i,\, \hat{y}_i^{(t-1)} + f_t(x_i)\right) + \Omega(f_t)$",
    "xgb_reg": r"$\Omega(f) = \gamma T + \dfrac{1}{2}\lambda \sum_{j=1}^{T} w_j^2$",
    "xgb_update": r"$\hat{y}_i^{(t)} = \hat{y}_i^{(t-1)} + \eta\, f_t(x_i)$",
    "sigmoid": r"$P(y = 1 \mid x) = \sigma(z) = \dfrac{1}{1 + e^{-z}}$",
    "logloss": r"$l(y, \hat{p}) = -\left[\, y \log \hat{p} + (1 - y) \log (1 - \hat{p}) \,\right]$",
    "logreg": r"$z = \beta_0 + \beta_1 x_1 + \beta_2 x_2 + \cdots + \beta_{12} x_{12}$",
    "shap": r"$f(x) = \phi_0 + \sum_{j=1}^{12} \phi_j$",
    "precision": r"$\mathrm{Precision} = \dfrac{TP}{TP + FP}$",
    "recall": r"$\mathrm{Recall} = \dfrac{TP}{TP + FN}$",
    "f1": r"$F_1 = 2 \times \dfrac{\mathrm{Precision} \times \mathrm{Recall}}{\mathrm{Precision} + \mathrm{Recall}}$",
    "accuracy": r"$\mathrm{Accuracy} = \dfrac{TP + TN}{TP + TN + FP + FN}$",
    "spw": r"$\mathrm{scale\_pos\_weight} = \dfrac{\mathrm{number\ of\ negative\ samples}}{\mathrm{number\ of\ positive\ samples}}$",
}


def equations():
    plt.rcParams.update({"mathtext.fontset": "stix"})
    for name, tex in EQUATIONS.items():
        fig = plt.figure(figsize=(0.01, 0.01))
        fig.text(0, 0, tex, fontsize=15, family="STIXGeneral")
        fig.savefig(EQ / f"{name}.png", dpi=300, bbox_inches="tight", pad_inches=0.04, transparent=False)
        plt.close(fig)


if __name__ == "__main__":
    class_distribution()
    correlation()
    confusion_grid()
    metric_bars()
    gantt()
    equations()
    print("charts and equations written")
