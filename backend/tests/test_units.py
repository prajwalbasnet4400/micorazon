from app.predictor import Predictor, risk_level
from app.security import create_token, decode_token, hash_password, verify_password
from app.suggestions import build_suggestions
from test_api import HEALTHY_PATIENT, HIGH_RISK_PATIENT


def test_password_hash_roundtrip():
    stored = hash_password("supersecret1")
    assert stored.startswith("pbkdf2_sha256$310000$")
    assert verify_password("supersecret1", stored)
    assert not verify_password("wrong-password", stored)


def test_password_hash_is_salted():
    assert hash_password("same-password") != hash_password("same-password")


def test_verify_password_rejects_malformed_hash():
    assert not verify_password("anything", "not-a-valid-hash")


def test_token_roundtrip_and_tampering():
    token = create_token(42)
    assert decode_token(token) == 42
    assert decode_token(token[:-2] + "xx") is None
    assert decode_token("garbage") is None


def test_risk_level_boundaries():
    assert risk_level(0.10) == "Low"
    assert risk_level(0.25) == "Moderate"
    assert risk_level(0.50) == "High"
    assert risk_level(0.75) == "Very High"


def test_suggestions_for_abnormal_values():
    tips = build_suggestions(HIGH_RISK_PATIENT, "At Risk")
    text = " ".join(tips)
    for keyword in ("Ejection fraction", "creatinine", "sodium", "blood pressure", "smoking", "cardiologist"):
        assert keyword.lower() in text.lower()


def test_suggestions_for_healthy_patient():
    tips = build_suggestions(HEALTHY_PATIENT, "Healthy")
    assert tips == ["Keep up a heart-healthy lifestyle: balanced diet, regular exercise and routine check-ups."]


def test_predictor_output_shape():
    predictor = Predictor()
    result = predictor.predict(HIGH_RISK_PATIENT)
    assert 0.0 <= result.probability_at_risk <= 1.0
    assert result.status == "At Risk"
    assert len(result.factors) == 5
    assert {f["direction"] for f in result.factors} <= {"increases", "decreases"}
    contributions = [abs(f["contribution"]) for f in result.factors]
    assert contributions == sorted(contributions, reverse=True)
