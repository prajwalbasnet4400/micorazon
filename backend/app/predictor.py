"""Loads the trained pipeline and produces risk predictions with per-patient explanations."""

import json
from dataclasses import dataclass
from functools import lru_cache

import joblib
import numpy as np
import pandas as pd

from . import config

FEATURE_LABELS = {
    "age": "Age",
    "anaemia": "Anaemia",
    "creatinine_phosphokinase": "Creatinine Phosphokinase",
    "diabetes": "Diabetes",
    "ejection_fraction": "Ejection Fraction",
    "high_blood_pressure": "High Blood Pressure",
    "platelets": "Platelets",
    "serum_creatinine": "Serum Creatinine",
    "serum_sodium": "Serum Sodium",
    "sex": "Sex",
    "smoking": "Smoking",
    "time": "Follow-up Time",
}


@dataclass
class Prediction:
    probability_at_risk: float
    status: str
    risk_level: str
    factors: list[dict]


def risk_level(probability: float) -> str:
    if probability < 0.25:
        return "Low"
    if probability < 0.5:
        return "Moderate"
    if probability < 0.75:
        return "High"
    return "Very High"


class Predictor:
    def __init__(self, model_path=None, meta_path=None):
        self.pipeline = joblib.load(model_path or config.ARTIFACTS_DIR / "model.joblib")
        self.meta = json.loads((meta_path or config.ARTIFACTS_DIR / "model_meta.json").read_text())
        self.features: list[str] = self.meta["features"]
        self.threshold: float = self.meta.get("threshold", 0.5)

    def _contributions(self, frame: pd.DataFrame) -> np.ndarray:
        """Per-feature contributions (log-odds) for one patient.

        XGBoost provides exact TreeSHAP values natively via ``pred_contribs``. Linear models use
        coefficient x standardized value; other models fall back to global importance signed by
        how far the input is from the training mean.
        """
        scaler = self.pipeline.named_steps["scaler"]
        model = self.pipeline.named_steps["model"]
        scaled = scaler.transform(frame)
        if hasattr(model, "get_booster"):
            import xgboost as xgb

            contribs = model.get_booster().predict(xgb.DMatrix(scaled, feature_names=self.features), pred_contribs=True)
            return contribs[0, :-1]  # last column is the bias term
        if hasattr(model, "coef_"):
            return np.asarray(model.coef_).ravel() * scaled[0]
        importances = self.meta.get("feature_importances") or {f: 1 / len(self.features) for f in self.features}
        return np.array([importances[f] for f in self.features]) * scaled[0]

    def predict(self, inputs: dict, top_k: int = 5) -> Prediction:
        frame = pd.DataFrame([[inputs[f] for f in self.features]], columns=self.features)
        probability = float(self.pipeline.predict_proba(frame)[0, 1])

        contributions = self._contributions(frame)
        order = np.argsort(-np.abs(contributions))[:top_k]
        factors = [
            {
                "feature": self.features[i],
                "label": FEATURE_LABELS.get(self.features[i], self.features[i]),
                "value": float(inputs[self.features[i]]),
                "contribution": round(float(contributions[i]), 4),
                "direction": "increases" if contributions[i] > 0 else "decreases",
            }
            for i in order
        ]
        return Prediction(
            probability_at_risk=probability,
            status="At Risk" if probability >= self.threshold else "Healthy",
            risk_level=risk_level(probability),
            factors=factors,
        )


@lru_cache(maxsize=1)
def get_predictor() -> Predictor:
    return Predictor()
