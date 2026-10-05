import pytest
from fastapi.testclient import TestClient

from app import config

HEALTHY_PATIENT = {
    "age": 45,
    "sex": 1,
    "anaemia": 0,
    "creatinine_phosphokinase": 120,
    "diabetes": 0,
    "ejection_fraction": 60,
    "high_blood_pressure": 0,
    "platelets": 260000,
    "serum_creatinine": 0.9,
    "serum_sodium": 140,
    "smoking": 0,
    "time": 240,
}

HIGH_RISK_PATIENT = {
    "age": 85,
    "sex": 1,
    "anaemia": 1,
    "creatinine_phosphokinase": 900,
    "diabetes": 1,
    "ejection_fraction": 20,
    "high_blood_pressure": 1,
    "platelets": 160000,
    "serum_creatinine": 3.5,
    "serum_sodium": 128,
    "smoking": 1,
    "time": 10,
}

USER = {
    "name": "Anup Karki",
    "email": "anup@example.com",
    "phone": "9861186365",
    "address": "Kathmandu",
    "password": "supersecret1",
}


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "test.db")
    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture()
def auth(client):
    token = client.post("/api/auth/signup", json=USER).json()["token"]
    return {"Authorization": f"Bearer {token}"}


def test_signup_login_and_me(client):
    res = client.post("/api/auth/signup", json=USER)
    assert res.status_code == 201
    assert res.json()["user"]["email"] == USER["email"]

    assert client.post("/api/auth/signup", json=USER).status_code == 409

    res = client.post("/api/auth/login", json={"email": "ANUP@example.com", "password": USER["password"]})
    assert res.status_code == 200
    token = res.json()["token"]

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.json()["name"] == USER["name"]


def test_login_rejects_wrong_password(client, auth):
    res = client.post("/api/auth/login", json={"email": USER["email"], "password": "wrong-password"})
    assert res.status_code == 401


def test_signup_validation(client):
    bad = {**USER, "password": "short", "phone": "abc"}
    assert client.post("/api/auth/signup", json=bad).status_code == 422


def test_reset_password(client, auth):
    wrong_phone = {"email": USER["email"], "phone": "0000000", "new_password": "newpassword1"}
    assert client.post("/api/auth/reset-password", json=wrong_phone).status_code == 400

    ok = {"email": USER["email"], "phone": USER["phone"], "new_password": "newpassword1"}
    assert client.post("/api/auth/reset-password", json=ok).status_code == 200
    res = client.post("/api/auth/login", json={"email": USER["email"], "password": "newpassword1"})
    assert res.status_code == 200


def test_predict_requires_auth(client):
    assert client.post("/api/predict", json=HEALTHY_PATIENT).status_code == 401
    bad = {"Authorization": "Bearer not-a-token"}
    assert client.post("/api/predict", json=HEALTHY_PATIENT, headers=bad).status_code == 401


def test_predict_healthy_vs_high_risk(client, auth):
    healthy = client.post("/api/predict", json=HEALTHY_PATIENT, headers=auth).json()
    risky = client.post("/api/predict", json=HIGH_RISK_PATIENT, headers=auth).json()

    assert healthy["status"] == "Healthy"
    assert risky["status"] == "At Risk"
    assert risky["probability_at_risk"] > healthy["probability_at_risk"]
    for result in (healthy, risky):
        assert result["probability_healthy"] + result["probability_at_risk"] == pytest.approx(1, abs=1e-3)
        assert 1 <= len(result["top_factors"]) <= 5
        assert result["suggestions"]

    assert any("cardiologist" in s for s in risky["suggestions"])


def test_predict_validation(client, auth):
    invalid = {**HEALTHY_PATIENT, "ejection_fraction": 150, "smoking": 2}
    res = client.post("/api/predict", json=invalid, headers=auth)
    assert res.status_code == 422
    fields = {err["loc"][-1] for err in res.json()["detail"]}
    assert {"ejection_fraction", "smoking"} <= fields

    missing = {k: v for k, v in HEALTHY_PATIENT.items() if k != "age"}
    assert client.post("/api/predict", json=missing, headers=auth).status_code == 422


def test_prediction_history_is_per_user(client, auth):
    client.post("/api/predict", json=HEALTHY_PATIENT, headers=auth)
    first = client.post("/api/predict", json=HIGH_RISK_PATIENT, headers=auth).json()

    history = client.get("/api/predictions", headers=auth).json()
    assert [h["id"] for h in history][:2] == [first["id"], first["id"] - 1]
    assert client.get(f"/api/predictions/{first['id']}", headers=auth).json()["status"] == "At Risk"

    other = client.post("/api/auth/signup", json={**USER, "email": "other@example.com"}).json()["token"]
    other_auth = {"Authorization": f"Bearer {other}"}
    assert client.get("/api/predictions", headers=other_auth).json() == []
    assert client.get(f"/api/predictions/{first['id']}", headers=other_auth).status_code == 404


def test_model_info(client):
    info = client.get("/api/model").json()
    assert info["model_name"] == "XGBoost"
    assert len(info["features"]) == 12
    assert set(info["metrics"]) >= {"accuracy", "precision", "recall", "f1"}
    assert len(info["comparison"]) == 6
