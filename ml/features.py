"""Shared feature definitions for the Heart Failure Prediction (HFP) pipeline."""

TARGET = "DEATH_EVENT"

# Order matters: the trained model expects columns in exactly this order.
FEATURES = [
    "age",
    "anaemia",
    "creatinine_phosphokinase",
    "diabetes",
    "ejection_fraction",
    "high_blood_pressure",
    "platelets",
    "serum_creatinine",
    "serum_sodium",
    "sex",
    "smoking",
    "time",
]

BINARY_FEATURES = ["anaemia", "diabetes", "high_blood_pressure", "sex", "smoking"]

CONTINUOUS_FEATURES = [f for f in FEATURES if f not in BINARY_FEATURES]

# Heavily right-skewed features are jittered / reasoned about in log space.
LOG_SCALE_FEATURES = ["creatinine_phosphokinase", "serum_creatinine", "platelets"]

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
