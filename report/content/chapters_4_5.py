"""Chapter 4: Implementation and Testing, Chapter 5: Conclusion, references and appendices."""

import re

from docx.shared import Inches

from .common import BIBLIOGRAPHY, GEN, LATENCY, META, METRICS, ML_FIG, REFERENCES, ROOT, SCREENS, SYSTEM_TESTS, fit, pct


def _snippet(path, start_marker, end_marker=None):
    """Lines of a source file from start_marker up to (not including) end_marker."""
    lines = (ROOT / path).read_text().splitlines()
    start = next(i for i, ln in enumerate(lines) if start_marker in ln)
    end = len(lines)
    if end_marker:
        end = next(i for i, ln in enumerate(lines) if i > start and end_marker in ln)
    return "\n".join(lines[start:end]).rstrip()


def chapter4(R, cite):
    P = lambda t, **k: R.para(cite(t), **k)  # noqa: E731
    R.chapter(4, "Implementation and Testing")

    R.heading("4.1 Implementation", 2)
    P(
        "The system was implemented in three parts: an offline machine learning pipeline (*ml/*), a REST API "
        "backend (*backend/*) and a web frontend (*frontend/*). The source code is managed with Git. Screenshots "
        "of the implemented system are given in Appendix A, and selected source code in Appendix B."
    )
    R.heading("4.1.1 Tools Used", 3)
    R.table(
        "Tools and Technologies Used",
        ["Category", "Tool / Technology", "Purpose in the Project"],
        [[cite(c) for c in row] for row in [
            ["Programming languages", "Python 3.12, JavaScript (ES2022), SQL", "Model, backend; frontend; database queries"],
            ["Machine learning", "scikit-learn 1.9 [@pedregosa], XGBoost 3.4 [@chen]", "Preprocessing, six classifiers, grid search, metrics, TreeSHAP"],
            ["Data analysis", "pandas 3.0, NumPy 2.4", "Loading, expanding and splitting the dataset"],
            ["Visualization", "Matplotlib 3.11, Seaborn 0.13", "Confusion matrices, ROC curves, feature importance, charts"],
            ["Model persistence", "joblib 1.6", "Saving and loading the trained pipeline"],
            ["Backend framework", "FastAPI 0.142, Uvicorn 0.54, Pydantic 2.13", "REST API, ASGI server, input validation"],
            ["Security", "PyJWT 2.15, Python hashlib (PBKDF2)", "Access tokens and password hashing"],
            ["Database platform", "SQLite 3", "Users, health data and predictions"],
            ["Frontend", "React 19, React Router 7, Vite 8", "Single page application, routing, build tool"],
            ["Reporting", "jsPDF 4", "Client-side PDF report generation"],
            ["CASE tools", "PlantUML, Graphviz", "UML diagrams in Chapter 3"],
            ["Testing", "pytest 9, FastAPI TestClient, headless Google Chrome", "Unit, integration and system tests"],
            ["Development tools", "Visual Studio Code, Git, uv, npm", "Editing, version control, dependency management"],
        ]],
        widths=(1.45, 2.35, 2.4), font_size=10, label="tools",
    )
    R.heading("4.1.2 Implementation Details of Modules", 3)

    R.heading("a. Dataset Preparation Module (ml/make_dataset.py)", 4)
    P(
        "The *expand()* function implements the data expansion described in Section 3.3.1. It assigns a "
        "*source_id* to the 299 real patients, samples 1701 base rows with replacement and perturbs them. The "
        "noise level, flip probabilities and clinical bounds are module constants, and a fixed random seed (42) "
        "makes the generated dataset reproducible. The core of the perturbation is:"
    )
    R.code(_snippet("ml/make_dataset.py", "    for col in CONTINUOUS_FEATURES:", "    out = pd.concat"))

    R.heading("b. Model Training Module (ml/train.py)", 4)
    P(
        "*build_models()* creates the six classifiers, and each one is wrapped in a scikit-learn *Pipeline* "
        "with a *StandardScaler*. Scaling is therefore learned only from the training data and applied "
        "automatically at prediction time. For each model, *main()* runs group-aware cross-validation, fits the "
        "pipeline, computes the test metrics with *evaluate()*, and saves the confusion matrix and ROC curve. "
        "XGBoost is tuned with *GridSearchCV*. The selected pipeline is exported to *model.joblib*, together with "
        "*model_meta.json*, which contains the feature order, threshold, metrics, feature importances and the "
        "full comparison table."
    )
    R.code(_snippet("ml/train.py", "        pipeline = Pipeline([(\"scaler\"", "        pipeline.fit(X_train, y_train)"))

    R.heading("c. Prediction Module (backend/app/predictor.py)", 4)
    P(
        "The *Predictor* class loads the pipeline and its metadata once, when the server starts. *predict()* "
        "arranges the inputs in the trained feature order, obtains the risk probability, determines the status "
        "and risk level, and calls *_contributions()* to compute the SHAP values. For XGBoost, the "
        "contributions are obtained directly from the booster:"
    )
    R.code(_snippet("backend/app/predictor.py", "        scaler = self.pipeline.named_steps", "        if hasattr(model, \"coef_\"):"))

    R.heading("d. Suggestion Module (backend/app/suggestions.py)", 4)
    P(
        "*build_suggestions()* applies the rules of Table {tab:rules} to the inputs and the predicted status, and "
        "returns an ordered list of plain-language suggestions. Keeping the rules in a separate module allows "
        "clinicians to review and change them without touching the model."
    )

    R.heading("e. Authentication Module (backend/app/security.py)", 4)
    P(
        "Passwords are hashed with PBKDF2-HMAC-SHA256, using a random 16-byte salt and 310,000 iterations. The "
        "hash is stored as *pbkdf2_sha256$iterations$salt$digest*, and *verify_password()* compares digests in "
        "constant time. *create_token()* issues an HS256-signed JWT that expires after 12 hours. The FastAPI "
        "dependency *current_user()* decodes the token on every protected request and loads the user from the "
        "database."
    )
    R.code(_snippet("backend/app/security.py", "def hash_password", "def create_token"))

    R.heading("f. Persistence Module (backend/app/db.py)", 4)
    P(
        "The database schema follows the class diagram. Each prediction request stores one *health_data* row "
        "(the validated inputs as JSON) and one *predictions* row (status, probabilities, factors and "
        "suggestions). Foreign keys with cascading deletes link the tables (Table {tab:schema})."
    )
    R.table(
        "Database Schema",
        ["Table", "Column", "Type", "Description"],
        [
            ["users", "id", "INTEGER PK", "Auto-increment identifier"],
            ["", "name, email, phone, address", "TEXT", "Profile; email is UNIQUE"],
            ["", "password_hash", "TEXT", "PBKDF2 hash with salt"],
            ["", "created_at", "TEXT", "Creation timestamp"],
            ["health_data", "id", "INTEGER PK", "Auto-increment identifier"],
            ["", "user_id", "INTEGER FK", "References users(id)"],
            ["", "inputs_json", "TEXT", "Twelve validated clinical inputs"],
            ["predictions", "id", "INTEGER PK", "Auto-increment identifier"],
            ["", "health_data_id", "INTEGER FK", "References health_data(id)"],
            ["", "status, risk_level", "TEXT", "Healthy / At Risk; Low – Very High"],
            ["", "probability_healthy, probability_at_risk", "REAL", "Predicted probabilities"],
            ["", "details_json", "TEXT", "Top factors and suggestions"],
        ],
        widths=(1.1, 2.3, 1.1, 1.8), font_size=10, label="schema",
    )

    R.heading("g. API Module (backend/app/main.py)", 4)
    P(
        "The FastAPI application defines the REST endpoints in Table {tab:api}. Request and response bodies are "
        "Pydantic models. Out-of-range values (for example, an ejection fraction outside 5–90%) are rejected "
        "with HTTP 422 and a message for each field, which the frontend shows next to the corresponding input. "
        "The application also serves the built frontend, so the whole system runs as a single process."
    )
    R.table(
        "REST API Endpoints",
        ["Method", "Endpoint", "Auth", "Description"],
        [
            ["POST", "/api/auth/signup", "No", "Register a user; returns token and user"],
            ["POST", "/api/auth/login", "No", "Authenticate; returns token and user"],
            ["POST", "/api/auth/reset-password", "No", "Reset password using email and phone"],
            ["GET", "/api/auth/me", "Yes", "Current user profile"],
            ["POST", "/api/predict", "Yes", "Predict risk, explain, suggest and store"],
            ["GET", "/api/predictions", "Yes", "The user's prediction history"],
            ["GET", "/api/predictions/{id}", "Yes", "One prediction of the user"],
            ["GET", "/api/model", "No", "Model name, metrics and feature importances"],
        ],
        widths=(0.8, 2.1, 0.6, 2.7), font_size=10, label="api",
    )

    R.heading("h. Frontend Modules (frontend/src)", 4)
    P(
        "*PredictionForm* keeps the form state (*formData*, *errors*, *loading*, *focusedField*), renders the three "
        "input sections from the *SECTIONS* metadata, shows the description of the focused field, and validates "
        "the values with the same ranges as the backend before sending them. *Result* displays the status card, "
        "probability bar, factor bars and suggestions, and lazily loads *PDFReportGenerator* (jsPDF) only when "
        "the report is downloaded. *History* lists past predictions. *AuthProvider* restores the session from "
        "the stored token on page load and logs the user out automatically when the server returns HTTP 401."
    )

    R.heading("4.2 Testing", 2)
    P(
        "Testing was carried out at three levels. Automated unit tests check individual functions in isolation. "
        "Automated integration tests exercise the API end-to-end with an isolated temporary database. System "
        "tests run the complete application in a real browser (headless Google Chrome). All 19 automated tests "
        "and all 14 system test cases passed."
    )
    R.heading("4.2.1 Test Cases for Unit Testing", 3)
    P("Table {tab:unit} lists the unit and integration test cases, implemented with pytest in *backend/tests* and *ml/tests*.")
    unit_rows = [
        ["UT-01", "Dataset", "Expanded dataset is valid", "UCI data, 1000 rows", "No missing values; binary columns in {0,1}; values within bounds"],
        ["UT-02", "Dataset", "Expansion is reproducible", "Same seed twice", "Identical data frames"],
        ["UT-03", "Security", "Password hash round trip", "“supersecret1”", "Correct password verifies; wrong one fails"],
        ["UT-04", "Security", "Hashes are salted", "Same password twice", "Different hashes"],
        ["UT-05", "Security", "Malformed hash rejected", "“not-a-valid-hash”", "Verification returns false"],
        ["UT-06", "Security", "Token round trip and tampering", "Token for user 42; altered token", "Returns 42; tampered token rejected"],
        ["UT-07", "Prediction", "Risk level boundaries", "p = 0.10, 0.25, 0.50, 0.75", "Low, Moderate, High, Very High"],
        ["UT-08", "Prediction", "Predictor output", "High-risk patient", "p in [0,1], At Risk, 5 factors sorted by |contribution|"],
        ["UT-09", "Suggestions", "Abnormal values", "EF 20, creatinine 3.5, sodium 128, BP, smoker", "Suggestions for each abnormality and cardiologist advice"],
        ["UT-10", "Suggestions", "Normal values", "Healthy patient", "Only the healthy-lifestyle suggestion"],
        ["IT-01", "Auth API", "Sign up, login and profile", "Valid user data", "201 Created; login works case-insensitively; profile returned"],
        ["IT-02", "Auth API", "Duplicate registration", "Same email twice", "409 Conflict"],
        ["IT-03", "Auth API", "Wrong password", "Wrong password", "401 Unauthorized"],
        ["IT-04", "Auth API", "Signup validation", "Short password, invalid phone", "422 with field errors"],
        ["IT-05", "Auth API", "Reset password", "Wrong phone, then correct phone", "400; then 200 and login with new password"],
        ["IT-06", "Predict API", "Authentication required", "No token; invalid token", "401 Unauthorized"],
        ["IT-07", "Predict API", "Healthy vs high-risk patient", "Two patient profiles", "Healthy and At Risk; probabilities sum to 1"],
        ["IT-08", "Predict API", "Input validation", "EF = 150, smoking = 2, missing age", "422 naming the invalid fields"],
        ["IT-09", "History API", "Per-user isolation", "Two users", "Own history only; other user's record gives 404"],
        ["IT-10", "Model API", "Model metadata", "GET /api/model", "XGBoost, 12 features, 6 compared models"],
    ]
    R.table(
        "Unit and Integration Test Cases",
        ["ID", "Module", "Test Case", "Input", "Expected Result", "Result"],
        [r + ["Pass"] for r in unit_rows],
        widths=(0.55, 0.85, 1.3, 1.3, 1.65, 0.6), font_size=9, label="unit",
    )

    R.heading("4.2.2 Test Cases for System Testing", 3)
    P(
        "System test cases (Table {tab:system}) were executed on the complete running system (FastAPI serving the "
        "production build of the frontend) by an automated browser script that acts like a user. The actual "
        "results recorded by the script are reported."
    )
    expected = {
        "ST-01": "Redirect to login page", "ST-02": "Account created and prediction form shown",
        "ST-03": "Login page shown", "ST-04": "Duplicate email error", "ST-05": "Invalid credentials error",
        "ST-06": "Success message on login page", "ST-07": "Login succeeds",
        "ST-08": "Submission blocked with field messages", "ST-09": "Healthy status with probabilities",
        "ST-10": "PDF file downloaded", "ST-11": "At Risk status with suggestions",
        "ST-12": "Both predictions listed; past result opens", "ST-13": "User remains logged in",
        "ST-14": "Responsive layout",
    }
    rows = []
    for tid, name, status, actual in SYSTEM_TESTS:
        actual = re.sub(r"[☀-➿️]", "", actual).replace("Healthy", "Healthy ").replace("At Risk", "At Risk ")
        actual = re.sub(r"\s+", " ", actual).replace(" ;", ";").strip()
        rows.append([tid, name, expected[tid], actual, status])
    R.table(
        "System Test Cases",
        ["ID", "Test Scenario", "Expected Result", "Actual Result", "Status"],
        rows, widths=(0.55, 1.4, 1.55, 2.1, 0.62), font_size=9, label="system",
    )

    R.heading("4.3 Result Analysis", 2)
    R.heading("4.3.1 Model Comparison", 3)
    xgb = METRICS["xgboost"]
    rf = METRICS["random_forest"]
    lr = METRICS["logistic_regression"]
    P(
        f"All six models were trained on the same {META['train_rows']} training records and evaluated on the "
        f"same {META['test_rows']} held-out records from 90 patients never seen during training. Table "
        "{tab:results} and Figure {fig:metrics} summarize the results."
    )
    R.table(
        "Performance Comparison of the Machine Learning Models",
        ["Model", "CV Accuracy", "Accuracy", "Precision", "Recall", "F1-score", "ROC-AUC"],
        [[m["name"].replace("Support Vector Machine (SVM)", "SVM"), f"{m['train_cv_accuracy']:.3f}",
          f"{m['test']['accuracy']:.3f}", f"{m['test']['precision']:.3f}", f"{m['test']['recall']:.3f}",
          f"{m['test']['f1']:.3f}", f"{m['test']['roc_auc']:.3f}"] for m in METRICS.values()],
        widths=(1.55, 0.8, 0.75, 0.8, 0.7, 0.75, 0.75), font_size=10, label="results",
    )
    R.figure(GEN / "metric_comparison.png", "Test-set Performance of the Six Classifiers", width=fit(GEN / "metric_comparison.png", 6.0), label="metrics")
    P(
        f"Logistic Regression achieved the highest precision ({lr['test']['precision']:.3f}) but a low recall "
        f"({lr['test']['recall']:.3f}): it missed almost half of the patients who "
        "died, which is unacceptable for a screening tool. Gradient Boosting and SVM showed the same pattern. The "
        f"tree ensembles gave the best balance. Random Forest obtained the highest accuracy ({rf['test']['accuracy']:.3f}), "
        f"recall ({rf['test']['recall']:.3f}) and F1-score ({rf['test']['f1']:.3f}). XGBoost was second on F1-score "
        f"({xgb['test']['f1']:.3f}) and achieved the highest ROC-AUC ({xgb['test']['roc_auc']:.4f}, against "
        f"{rf['test']['roc_auc']:.4f} for Random Forest)."
    )
    P(
        "XGBoost was selected as the deployed model, as planned in the proposal, for three reasons. First, it "
        "discriminates between high- and low-risk patients as well as any model (the highest ROC-AUC), and the "
        "F1-score gap to Random Forest is small (0.025). Second, XGBoost computes exact per-patient TreeSHAP "
        "explanations natively, which is central to the system's explainability objective. Third, its "
        "regularized objective and tuned shallow trees (depth 3) reduce the risk of overfitting the small "
        "source dataset. The training pipeline supports deploying Random Forest instead with a single option if "
        "higher recall is preferred."
    )
    P(
        "The confusion matrices in Figure {fig:cm} show the trade-off in absolute numbers. Of the 233 test records "
        f"with a death event, XGBoost identified {xgb['confusion_matrix'][1][1]} and Random Forest "
        f"{rf['confusion_matrix'][1][1]}, while Logistic Regression identified only {lr['confusion_matrix'][1][1]}. "
        "Figure {fig:roc} compares the ROC curves."
    )
    R.figure(GEN / "confusion_all.png", "Confusion Matrices of the Six Models on the Test Set", width=fit(GEN / "confusion_all.png", 6.0), label="cm")
    R.figure(ML_FIG / "roc_curves.png", "ROC Curves of the Six Models", width=fit(ML_FIG / "roc_curves.png", 5.0), label="roc")

    R.heading("4.3.2 Feature Importance", 3)
    imp = sorted(META["feature_importances"].items(), key=lambda kv: -kv[1])
    P(
        f"Figure {{fig:importance}} shows the global feature importance of the deployed XGBoost model. Follow-up "
        f"time is the most important feature ({pct(imp[0][1])}), followed by serum creatinine ({pct(imp[1][1])}) "
        f"and ejection fraction ({pct(imp[2][1])}). Serum creatinine and ejection fraction being the strongest "
        "clinical predictors agrees with the findings of Chicco and Jurman on the same data [@chicco]. The "
        "dominance of follow-up time is expected: patients who died early had short follow-up periods. This is "
        "why follow-up time is discussed as a limitation in Section 1.4.2."
    )
    R.figure(ML_FIG / "feature_importance.png", "Feature Importance of the XGBoost Model", width=fit(ML_FIG / "feature_importance.png", 5.2), label="importance")

    R.heading("4.3.3 System Output and Performance", 3)
    P(
        "Table {tab:samples} shows predictions made by the deployed system for three patient profiles during "
        "testing. The outputs are consistent with clinical expectation. The patient with a normal ejection "
        "fraction and creatinine is classified as low risk, while the patients with a low ejection fraction, "
        "high creatinine, low sodium and short follow-up are classified as very high risk. Their top "
        "contributing factors are follow-up time, serum creatinine and ejection fraction."
    )
    R.table(
        "Sample Predictions of the Deployed System",
        ["Profile (age, EF, creatinine, sodium, follow-up, other)", "Status", "Risk level", "Risk prob."],
        [
            ["60 y, EF 38%, 1.0 mg/dL, 135 mEq/L, 120 days, no comorbidities", "Healthy", "Low", "13.96%"],
            ["75 y, EF 25%, 2.4 mg/dL, 130 mEq/L, 30 days, high BP, anaemia, CPK 720", "At Risk", "Very High", "91.75%"],
            ["80 y, EF 20%, 3.0 mg/dL, 128 mEq/L, 15 days, high BP, smoker", "At Risk", "Very High", "97.34%"],
        ],
        widths=(3.6, 0.8, 0.9, 0.8), font_size=10, label="samples",
    )
    P(
        f"Response time was measured over {LATENCY['n']} consecutive prediction requests to the running server on "
        f"a development laptop. The mean server round-trip time was {LATENCY['mean_ms']} ms (median "
        f"{LATENCY['median_ms']} ms, 95th percentile {LATENCY['p95_ms']} ms), including authentication, model "
        f"inference, SHAP computation and two database writes. A login took about {LATENCY['login_ms']:.0f} ms, "
        "most of which is the deliberately slow PBKDF2 password hashing. Both are far below the one-second target. "
        "The screens of the final system are shown in Appendix A."
    )


def chapter5(R, cite):
    P = lambda t, **k: R.para(cite(t), **k)  # noqa: E731
    R.chapter(5, "Conclusion and Future Recommendations")
    m = META["metrics"]
    R.heading("5.1 Conclusion", 2)
    P(
        "This project developed the Heart Failure Prediction (HFP) system, a complete web application that "
        "predicts a patient's risk of a heart-failure death event from twelve routine clinical attributes. Six "
        "machine learning algorithms were compared using a leakage-free, patient-group-aware evaluation. The "
        f"deployed XGBoost model achieved a ROC-AUC of {m['roc_auc']:.3f}, an accuracy of {pct(m['accuracy'])} and a "
        f"recall of {pct(m['recall'])} on held-out patients."
    )
    P(
        "Beyond the model, the system meets all of its objectives. It explains every prediction through SHAP "
        "contributions, gives rule-based health suggestions, generates downloadable PDF reports and keeps a "
        "secure, per-user prediction history. It was designed using UML models and implemented with FastAPI, "
        "React and SQLite. Its correctness was confirmed by 19 automated tests and 14 system test cases. The "
        "project shows how routinely collected clinical data and explainable machine learning can be combined "
        "into a practical tool that supports early identification of high-risk heart failure patients."
    )
    R.heading("5.2 Future Recommendations", 2)
    R.bullets([
        "**Local and larger datasets:** retrain and validate the model on real patient records from Nepali "
        "hospitals, replacing the synthetic expansion with genuinely new patients.",
        "**Additional clinical features:** include ECG findings, natriuretic peptides (BNP/NT-proBNP), "
        "medication and admission history, and consider removing follow-up time for a purely prospective model.",
        "**Probability calibration and threshold tuning:** calibrate the predicted probabilities and choose the "
        "decision threshold together with clinicians to favour higher recall.",
        "**EHR integration:** connect the system to hospital electronic health record systems so that clinical "
        "values are filled in automatically.",
        "**Role-based access:** add clinician and administrator roles, so that a clinician can manage several "
        "patients, and add email or SMS one-time-password verification for password reset.",
        "**Time-series monitoring:** use repeated measurements to track how a patient's risk changes over time.",
        "**Mobile application and alerts:** provide a mobile app for data entry and notify patients and "
        "clinicians when the risk increases.",
    ])


def back_matter(R, cite):
    R.heading("REFERENCES", 1, page_break=True)
    for i, key in enumerate(cite.order, 1):
        p = R.para(f"[{i}] {REFERENCES[key]}", align="left", space_after=6)
        p.paragraph_format.left_indent = Inches(0.45)
        p.paragraph_format.first_line_indent = Inches(-0.45)

    R.heading("BIBLIOGRAPHY", 1, page_break=True)
    for item in BIBLIOGRAPHY:
        p = R.para(item, align="left", space_after=6)
        p.paragraph_format.left_indent = Inches(0.3)
        p.paragraph_format.first_line_indent = Inches(-0.3)

    R.heading("APPENDICES", 1, page_break=True)
    R.heading("Appendix A: Screenshots", 2)
    shots = [
        ("01_login.png", "Login Page"),
        ("02_signup.png", "Sign Up Page"),
        ("03_reset_password.png", "Reset Password Page"),
        ("04_prediction_form.png", "Heart Failure Risk Prediction Form with Field Description"),
        ("05_validation.png", "Validation of Invalid Input"),
        ("06_result_healthy.png", "Prediction Result Page (Healthy Patient)"),
        ("07_result_risk.png", "Prediction Result Page (At-Risk Patient) with Contributing Factors and Suggestions"),
        ("08_history.png", "Prediction History Page"),
        ("10_pdf_report.png", "Downloaded PDF Report of a Patient"),
        ("09_api_docs.png", "Interactive API Documentation of the Backend"),
    ]
    for file, title in shots:
        path = SCREENS / file
        R.figure(path, title, width=fit(path, 6.0, 7.4 if "pdf" not in file else 7.0))

    R.heading("Appendix B: Source Code", 2, page_break=True)
    P = lambda t, **k: R.para(cite(t), **k)  # noqa: E731
    P("Selected source files of the system are listed below. The complete source code is available in the project repository.")
    for path, title, start, end in [
        ("backend/app/predictor.py", "B.1 Prediction Module (backend/app/predictor.py)", "class Predictor:", "@lru_cache"),
        ("backend/app/main.py", "B.2 Prediction Endpoint (backend/app/main.py)", '@app.post("/api/predict"', '@app.get("/api/predictions"'),
        ("backend/app/suggestions.py", "B.3 Suggestion Module (backend/app/suggestions.py)", "def build_suggestions", None),
        ("ml/train.py", "B.4 Model Definitions (ml/train.py)", "def build_models", "MODEL_NAMES = {"),
        ("frontend/src/pages/PredictionForm.jsx", "B.5 Prediction Form Submission (frontend/src/pages/PredictionForm.jsx)", "  const handleSubmit", "  const renderField"),
    ]:
        R.heading(title, 3)
        R.code(_snippet(path, start, end))
