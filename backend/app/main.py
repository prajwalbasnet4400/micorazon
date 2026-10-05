"""Heart Failure Prediction (HFP) API.

Run with:  uv run uvicorn app.main:app --reload --app-dir backend
"""

import json
import sqlite3
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import config, db
from .predictor import get_predictor
from .schemas import (
    AuthResponse,
    HealthData,
    LoginRequest,
    PredictionResult,
    ResetPasswordRequest,
    SignupRequest,
    User,
)
from .security import create_token, decode_token, hash_password, verify_password
from .suggestions import build_suggestions


@asynccontextmanager
async def lifespan(_: FastAPI):
    db.init_db()
    if config.SEED_DEMO:
        db.seed_demo_user(hash_password(config.DEMO_USER["password"]))
    get_predictor()  # load the model once at startup
    yield


app = FastAPI(title="Heart Failure Prediction API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _user_from_row(row: sqlite3.Row) -> User:
    return User(id=row["id"], name=row["name"], email=row["email"], phone=row["phone"], address=row["address"])


def current_user(authorization: Annotated[str | None, Header()] = None) -> User:
    unauthorized = HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    if not authorization or not authorization.lower().startswith("bearer "):
        raise unauthorized
    user_id = decode_token(authorization.split(" ", 1)[1])
    if user_id is None:
        raise unauthorized
    with db.connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None:
        raise unauthorized
    return _user_from_row(row)


CurrentUser = Annotated[User, Depends(current_user)]


# --- Auth -------------------------------------------------------------------------------


@app.post("/api/auth/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(body: SignupRequest):
    email = body.email.lower()
    try:
        with db.connect() as conn:
            cur = conn.execute(
                "INSERT INTO users (name, email, phone, address, password_hash) VALUES (?, ?, ?, ?, ?)",
                (body.name, email, body.phone, body.address, hash_password(body.password)),
            )
            row = conn.execute("SELECT * FROM users WHERE id = ?", (cur.lastrowid,)).fetchone()
    except sqlite3.IntegrityError:
        raise HTTPException(status.HTTP_409_CONFLICT, "An account with this email already exists")
    return AuthResponse(token=create_token(row["id"]), user=_user_from_row(row))


@app.post("/api/auth/login", response_model=AuthResponse)
def login(body: LoginRequest):
    with db.connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (body.email.lower(),)).fetchone()
    if row is None or not verify_password(body.password, row["password_hash"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    return AuthResponse(token=create_token(row["id"]), user=_user_from_row(row))


@app.post("/api/auth/reset-password")
def reset_password(body: ResetPasswordRequest):
    """Reset a password by confirming the phone number registered with the account."""
    with db.connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (body.email.lower(),)).fetchone()
        if row is None or row["phone"] != body.phone.strip():
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email and phone number do not match our records")
        conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hash_password(body.new_password), row["id"]))
    return {"message": "Password updated successfully. You can now log in."}


@app.get("/api/auth/me", response_model=User)
def me(user: CurrentUser):
    return user


# --- Prediction -------------------------------------------------------------------------


def _result_from_rows(health: sqlite3.Row, pred: sqlite3.Row) -> PredictionResult:
    details = json.loads(pred["details_json"])
    return PredictionResult(
        id=pred["id"],
        status=pred["status"],
        risk_level=pred["risk_level"],
        probability_healthy=pred["probability_healthy"],
        probability_at_risk=pred["probability_at_risk"],
        top_factors=details["top_factors"],
        suggestions=details["suggestions"],
        inputs=HealthData(**json.loads(health["inputs_json"])),
        created_at=pred["created_at"],
    )


@app.post("/api/predict", response_model=PredictionResult)
def predict(body: HealthData, user: CurrentUser):
    inputs = body.model_dump()
    result = get_predictor().predict(inputs)
    p_risk = round(result.probability_at_risk, 4)
    details = {"top_factors": result.factors, "suggestions": build_suggestions(inputs, result.status)}

    with db.connect() as conn:
        health_id = conn.execute(
            "INSERT INTO health_data (user_id, inputs_json) VALUES (?, ?)", (user.id, json.dumps(inputs))
        ).lastrowid
        pred_id = conn.execute(
            """INSERT INTO predictions
               (health_data_id, status, risk_level, probability_healthy, probability_at_risk, details_json)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (health_id, result.status, result.risk_level, round(1 - p_risk, 4), p_risk, json.dumps(details)),
        ).lastrowid
        health = conn.execute("SELECT * FROM health_data WHERE id = ?", (health_id,)).fetchone()
        pred = conn.execute("SELECT * FROM predictions WHERE id = ?", (pred_id,)).fetchone()
    return _result_from_rows(health, pred)


@app.get("/api/predictions", response_model=list[PredictionResult])
def prediction_history(user: CurrentUser, limit: int = 50):
    with db.connect() as conn:
        rows = conn.execute(
            """SELECT h.id AS h_id, h.inputs_json, p.*
               FROM predictions p JOIN health_data h ON h.id = p.health_data_id
               WHERE h.user_id = ? ORDER BY p.id DESC LIMIT ?""",
            (user.id, min(max(limit, 1), 200)),
        ).fetchall()
    return [_result_from_rows(row, row) for row in rows]


@app.get("/api/predictions/{prediction_id}", response_model=PredictionResult)
def prediction_detail(prediction_id: int, user: CurrentUser):
    with db.connect() as conn:
        row = conn.execute(
            """SELECT h.inputs_json, p.*
               FROM predictions p JOIN health_data h ON h.id = p.health_data_id
               WHERE p.id = ? AND h.user_id = ?""",
            (prediction_id, user.id),
        ).fetchone()
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Prediction not found")
    return _result_from_rows(row, row)


# --- Model information ------------------------------------------------------------------


@app.get("/api/model")
def model_info():
    meta = get_predictor().meta
    figures = sorted(p.name for p in config.FIGURES_DIR.glob("*.png")) if config.FIGURES_DIR.exists() else []
    return {**meta, "figures": [f"/api/figures/{name}" for name in figures]}


@app.get("/api/health")
def health():
    return {"status": "ok"}


if config.FIGURES_DIR.exists():
    app.mount("/api/figures", StaticFiles(directory=config.FIGURES_DIR), name="figures")

# Serve the built React app (npm run build) so the whole system runs from one process.
if config.FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=config.FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str):
        file = config.FRONTEND_DIST / path
        if path and file.is_file() and config.FRONTEND_DIST in file.resolve().parents:
            return FileResponse(file)
        return FileResponse(config.FRONTEND_DIST / "index.html")
