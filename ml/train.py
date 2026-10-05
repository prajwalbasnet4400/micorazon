"""Train and compare the HFP classifiers, then export the deployed model.

Models compared (as in the project report): Logistic Regression, SVM, Decision Tree,
Random Forest, XGBoost and Gradient Boosting. Each is wrapped in a scikit-learn
Pipeline with a StandardScaler so the backend can feed raw clinical values.

The test set is split by ``source_id`` (the real patient a row was derived from), so
synthetic near-copies of a test patient never appear in training.

Outputs:
    backend/app/artifacts/model.joblib     deployed pipeline (XGBoost by default)
    backend/app/artifacts/model_meta.json  features, metrics, feature importances
    reports/metrics.json                   full comparison table
    reports/figures/*.png                  confusion matrices, ROC curves, importances

Usage:
    uv run python ml/train.py [--deploy xgboost]
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402
from sklearn.calibration import CalibratedClassifierCV  # noqa: E402
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import (  # noqa: E402
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import GridSearchCV, GroupShuffleSplit, StratifiedGroupKFold, cross_validate  # noqa: E402
from sklearn.pipeline import Pipeline  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402
from sklearn.svm import SVC  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402
from xgboost import XGBClassifier  # noqa: E402

from features import FEATURE_LABELS, FEATURES, TARGET  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATASET = ROOT / "data" / "heart_failure_clinical_records_2000.csv"
ARTIFACTS = ROOT / "backend" / "app" / "artifacts"
REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"

SEED = 42
TEST_SIZE = 0.3
THRESHOLD = 0.5


def build_models(scale_pos_weight: float) -> dict[str, object]:
    return {
        "logistic_regression": LogisticRegression(max_iter=1000, random_state=SEED),
        "svm": CalibratedClassifierCV(SVC(kernel="rbf", random_state=SEED), ensemble=False),
        "decision_tree": DecisionTreeClassifier(max_depth=5, min_samples_leaf=10, random_state=SEED),
        "random_forest": RandomForestClassifier(
            n_estimators=300, max_depth=8, min_samples_leaf=5, class_weight="balanced", random_state=SEED, n_jobs=-1
        ),
        "xgboost": XGBClassifier(
            n_estimators=300,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_lambda=1.0,
            scale_pos_weight=scale_pos_weight,
            eval_metric="logloss",
            random_state=SEED,
            n_jobs=-1,
        ),
        "gradient_boosting": GradientBoostingClassifier(n_estimators=200, max_depth=3, random_state=SEED),
    }


# Small grid tuned with group-aware CV on the training split only (scored on F1, since
# balanced precision/recall matters more than raw accuracy for this medical task).
XGB_GRID = {
    "model__max_depth": [2, 3, 4],
    "model__n_estimators": [150, 300],
    "model__learning_rate": [0.03, 0.1],
    "model__min_child_weight": [1, 5],
}


MODEL_NAMES = {
    "logistic_regression": "Logistic Regression",
    "svm": "Support Vector Machine (SVM)",
    "decision_tree": "Decision Tree",
    "random_forest": "Random Forest",
    "xgboost": "XGBoost",
    "gradient_boosting": "Gradient Boosting",
}


def evaluate(y_true: np.ndarray, proba: np.ndarray) -> dict[str, float]:
    pred = (proba >= THRESHOLD).astype(int)
    return {
        "accuracy": round(accuracy_score(y_true, pred), 4),
        "precision": round(precision_score(y_true, pred, zero_division=0), 4),
        "recall": round(recall_score(y_true, pred, zero_division=0), 4),
        "f1": round(f1_score(y_true, pred, zero_division=0), 4),
        "roc_auc": round(roc_auc_score(y_true, proba), 4),
    }


def plot_confusion(cm: np.ndarray, title: str, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6, 4.5))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Predicted Alive", "Predicted Dead"],
        yticklabels=["Actual Alive", "Actual Dead"],
        ax=ax,
    )
    ax.set_title(f"Confusion Matrix - {title}")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def plot_roc(curves: dict[str, tuple[np.ndarray, np.ndarray, float]], path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6.5, 5))
    for key, (fpr, tpr, auc) in curves.items():
        ax.plot(fpr, tpr, label=f"{MODEL_NAMES[key]} (AUC = {auc:.2f})")
    ax.plot([0, 1], [0, 1], "k--", linewidth=1)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curves")
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def plot_importance(importances: dict[str, float], title: str, path: Path) -> None:
    items = sorted(importances.items(), key=lambda kv: kv[1])
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.barh([FEATURE_LABELS[k] for k, _ in items], [v for _, v in items], color="#7c3aed")
    ax.set_title(f"Feature Importance - {title}")
    ax.set_xlabel("Importance")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def feature_importances(pipeline: Pipeline) -> dict[str, float] | None:
    model = pipeline.named_steps["model"]
    if hasattr(model, "feature_importances_"):
        raw = np.asarray(model.feature_importances_, dtype=float)
    elif hasattr(model, "coef_"):
        raw = np.abs(np.asarray(model.coef_, dtype=float)).ravel()
    else:
        return None
    raw = raw / raw.sum() if raw.sum() else raw
    return {f: round(float(v), 4) for f, v in zip(FEATURES, raw)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--deploy", default="xgboost", choices=list(MODEL_NAMES), help="model to export")
    args = parser.parse_args()

    df = pd.read_csv(DATASET)
    X, y, groups = df[FEATURES], df[TARGET].to_numpy(), df["source_id"].to_numpy()

    splitter = GroupShuffleSplit(n_splits=1, test_size=TEST_SIZE, random_state=SEED)
    train_idx, test_idx = next(splitter.split(X, y, groups))
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    print(f"Dataset: {len(df)} rows | train {len(train_idx)} | test {len(test_idx)}")

    scale_pos_weight = float((y_train == 0).sum() / max((y_train == 1).sum(), 1))
    cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED)
    FIGURES.mkdir(parents=True, exist_ok=True)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)

    results, fitted, curves = {}, {}, {}
    for key, estimator in build_models(scale_pos_weight).items():
        pipeline = Pipeline([("scaler", StandardScaler()), ("model", estimator)])
        if key == "xgboost":
            search = GridSearchCV(pipeline, XGB_GRID, scoring="f1", cv=cv, n_jobs=-1)
            search.fit(X_train, y_train, groups=groups[train_idx])
            pipeline = search.best_estimator_
            print(f"XGBoost best params: {search.best_params_}")
        cv_scores = cross_validate(
            pipeline, X_train, y_train, groups=groups[train_idx], cv=cv, scoring=["accuracy", "precision"]
        )
        pipeline.fit(X_train, y_train)
        proba = pipeline.predict_proba(X_test)[:, 1]
        cm = confusion_matrix(y_test, (proba >= THRESHOLD).astype(int))

        metrics = evaluate(y_test, proba)
        results[key] = {
            "name": MODEL_NAMES[key],
            "train_cv_accuracy": round(float(cv_scores["test_accuracy"].mean()), 4),
            "train_cv_precision": round(float(cv_scores["test_precision"].mean()), 4),
            "test": metrics,
            "confusion_matrix": cm.tolist(),
        }
        fitted[key] = pipeline
        fpr, tpr, _ = roc_curve(y_test, proba)
        curves[key] = (fpr, tpr, metrics["roc_auc"])
        plot_confusion(cm, MODEL_NAMES[key], FIGURES / f"confusion_{key}.png")
        print(
            f"{MODEL_NAMES[key]:<30} acc={metrics['accuracy']:.4f} prec={metrics['precision']:.4f} "
            f"rec={metrics['recall']:.4f} f1={metrics['f1']:.4f} auc={metrics['roc_auc']:.4f}"
        )

    plot_roc(curves, FIGURES / "roc_curves.png")

    deployed = fitted[args.deploy]
    importances = feature_importances(deployed)
    if importances:
        plot_importance(importances, MODEL_NAMES[args.deploy], FIGURES / "feature_importance.png")

    trained_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    (REPORTS / "metrics.json").write_text(json.dumps({"trained_at": trained_at, "models": results}, indent=2))

    joblib.dump(deployed, ARTIFACTS / "model.joblib")
    meta = {
        "model_key": args.deploy,
        "model_name": MODEL_NAMES[args.deploy],
        "features": FEATURES,
        "threshold": THRESHOLD,
        "trained_at": trained_at,
        "dataset_rows": int(len(df)),
        "train_rows": int(len(train_idx)),
        "test_rows": int(len(test_idx)),
        "metrics": results[args.deploy]["test"],
        "feature_importances": importances,
        "comparison": results,
    }
    (ARTIFACTS / "model_meta.json").write_text(json.dumps(meta, indent=2))
    print(f"\nDeployed {MODEL_NAMES[args.deploy]} -> {(ARTIFACTS / 'model.joblib').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
