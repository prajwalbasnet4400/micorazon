import os
import secrets
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BACKEND_DIR.parent

ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"
FIGURES_DIR = ROOT_DIR / "reports" / "figures"
FRONTEND_DIST = ROOT_DIR / "frontend" / "dist"

DB_PATH = Path(os.environ.get("HFP_DB_PATH", BACKEND_DIR / "hfp.db"))

# Set HFP_SECRET_KEY in production; the random fallback invalidates tokens on restart.
SECRET_KEY = os.environ.get("HFP_SECRET_KEY") or secrets.token_urlsafe(32)
TOKEN_TTL_HOURS = int(os.environ.get("HFP_TOKEN_TTL_HOURS", "12"))

# Development convenience: create a demo account at startup (matches the frontend's dev prefill).
SEED_DEMO = os.environ.get("HFP_SEED_DEMO", "").lower() in ("1", "true", "yes")
DEMO_USER = {
    "name": "Demo User",
    "email": "demo@hfp.com",
    "phone": "9800000000",
    "address": "Kathmandu",
    "password": "demo12345",
}

CORS_ORIGINS =os.environ.get("HFP_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
