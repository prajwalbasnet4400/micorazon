# Heart Failure Prediction (HFP)

A machine learning web application that predicts the risk of heart failure from clinical
data, built for the BIT 8th semester project (Aryan School of Engineering and Management,
Purbanchal University — project code BIT453CO).

It takes a patient's clinical data, predicts their risk with an XGBoost model, explains which
factors drove that prediction, gives suggestions for high-risk patients and lets the user
download a PDF report.

## Architecture

```
Data Collection → Data Preprocessing → Train ML Model → Save Model
                                                            │
React frontend  ──POST /api/predict──▶  FastAPI backend ──▶ XGBoost pipeline
   │  (Vite)                               │  (SQLite)
   └── Download PDF report (jsPDF)         └── users, health_data, predictions
```

| Layer    | Tech                                                        | Location    |
| -------- | ----------------------------------------------------------- | ----------- |
| ML       | pandas, scikit-learn, XGBoost, matplotlib, seaborn          | `ml/`       |
| Backend  | FastAPI, SQLite, PBKDF2 password hashing, JWT auth          | `backend/`  |
| Frontend | React 19, React Router, jsPDF (Vite)                        | `frontend/` |

## Features

- Sign up / login / password reset (confirmed with the registered phone number)
- Clinical data entry, grouped into General, Medical and Habit info, with field descriptions and validation
- Heart failure risk prediction: status, probabilities and risk level
- Per-patient explanation: SHAP contributions computed natively by XGBoost
- Rule-based suggestions for abnormal values and high-risk patients
- Downloadable PDF report
- Prediction history for each user

## Dataset

The 12 clinical features and the `DEATH_EVENT` target come from the UCI
[Heart Failure Clinical Records](https://archive.ics.uci.edu/dataset/519/heart+failure+clinical+records)
dataset (299 patients; Chicco & Jurman, 2020), saved as `data/heart_failure_clinical_records_uci.csv`.

The report specifies 2000 records, so `ml/make_dataset.py` expands the data to 2000 rows with
synthetic patients. Each one is made by adding noise to a real record. Every row keeps a
`source_id` that points to the real patient it came from. Training splits by that ID, so the
test set never contains near-copies of training rows.

## Model results (held-out test set, 589 records)

| Model               | Accuracy | Precision | Recall | F1    | ROC-AUC |
| ------------------- | -------- | --------- | ------ | ----- | ------- |
| Logistic Regression | 0.764    | 0.805     | 0.532  | 0.641 | 0.805   |
| SVM                 | 0.727    | 0.707     | 0.528  | 0.604 | 0.769   |
| Decision Tree       | 0.744    | 0.697     | 0.622  | 0.658 | 0.734   |
| Random Forest       | 0.769    | 0.724     | 0.674  | 0.698 | 0.848   |
| **XGBoost**         | 0.750    | 0.699     | 0.648  | 0.673 | 0.848   |
| Gradient Boosting   | 0.691    | 0.647     | 0.481  | 0.552 | 0.775   |

XGBoost is the deployed model, as chosen in the report. It balances precision and recall
better than the linear models, which miss many positive cases. It is tuned with group-aware
cross-validation on the training split only. Figures are written to `reports/figures/`, and
the full metrics are in `reports/metrics.json`.

## Getting started

Requirements: Python 3.11+ with [uv](https://docs.astral.sh/uv/), Node.js 20+.
On macOS, XGBoost also needs OpenMP: `brew install libomp`.

```bash
# 1. Python dependencies
uv sync

# 2. (Optional) regenerate the dataset and retrain. A trained model is already committed.
uv run python ml/make_dataset.py
uv run python ml/train.py

# 3. Run the backend (http://127.0.0.1:8000, API docs at /docs)
uv run uvicorn app.main:app --reload --app-dir backend

# 4. Run the frontend in another terminal (http://localhost:5173)
cd frontend
npm install
npm run dev
```

To run everything from one process, build the frontend (`cd frontend && npm run build`) and
open http://127.0.0.1:8000. FastAPI serves the built app.

### Configuration

| Variable            | Default                  | Purpose                                     |
| ------------------- | ------------------------ | ------------------------------------------- |
| `HFP_SECRET_KEY`    | random on each start     | JWT signing key. Set it so logins survive restarts. |
| `HFP_DB_PATH`       | `backend/hfp.db`         | SQLite database file                        |
| `HFP_TOKEN_TTL_HOURS` | `12`                   | Login session lifetime                      |
| `HFP_SEED_DEMO`     | off                      | `1` creates the demo account `demo@hfp.com` / `demo12345`. The dev login form is prefilled with it. |
| `HFP_CORS_ORIGINS`  | `http://localhost:5173,…` | Allowed frontend origins                    |

## API

| Method | Endpoint                    | Description                          |
| ------ | --------------------------- | ------------------------------------ |
| POST   | `/api/auth/signup`          | Create an account, returns a token   |
| POST   | `/api/auth/login`           | Log in, returns a token              |
| POST   | `/api/auth/reset-password`  | Reset password (email + phone)       |
| GET    | `/api/auth/me`              | Current user                         |
| POST   | `/api/predict`              | Predict risk from clinical data      |
| GET    | `/api/predictions`          | The user's prediction history        |
| GET    | `/api/predictions/{id}`     | A single prediction                  |
| GET    | `/api/model`                | Model metrics, importances, figures  |

## Testing

```bash
uv run pytest
```

These tests cover:

- Unit tests for dataset generation
- API integration tests: auth, validation of invalid input, predictions and per-user history isolation

## Project structure

```
data/                 UCI source data + generated 2000-record dataset
ml/                   make_dataset.py, train.py, features.py, tests
backend/app/          FastAPI app, predictor, suggestions, auth, SQLite
backend/app/artifacts trained model.joblib + model_meta.json
backend/tests/        API tests
frontend/src/         React pages, PDF report generator, field metadata
reports/              metrics.json and evaluation figures
```

## Team

Anup Karki (380181), Dipesh Kumar Sharma (380184), Puskar Sarki (380191).
Supervisor: Mr. Sunny Sharma.

> This system supports clinical decision-making. It does not replace professional medical diagnosis.
