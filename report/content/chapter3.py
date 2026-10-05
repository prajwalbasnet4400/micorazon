"""Chapter 3: System Analysis and Design."""

from docx.shared import Inches

from .common import EQ, GEN, META, ORIG, fit


def use_cases(R, cite):
    cases = [
        ("uc1", "UC-01: Register Account", [
            ("Use Case ID", "UC-01"), ("Use Case Name", "Register Account"), ("Actor", "User"),
            ("Description", "A new user creates an account to access the prediction features."),
            ("Pre-condition", "The user is not logged in."),
            ("Main Flow", ["1. User opens the Sign Up page.", "2. User enters name, email, phone number, address and password.",
                           "3. System validates the fields (valid email, 7–15 digit phone, password of at least 8 characters).",
                           "4. System stores the user with a salted PBKDF2 password hash.",
                           "5. System issues an access token and opens the prediction form."]),
            ("Alternate Flow", ["3a. Invalid field: the system shows a message next to the field.",
                                "4a. Email already registered: the system shows “An account with this email already exists”."]),
            ("Post-condition", "A new account exists and the user is logged in."),
        ]),
        ("uc2", "UC-02: Login", [
            ("Use Case ID", "UC-02"), ("Use Case Name", "Login"), ("Actor", "User"),
            ("Description", "A registered user signs in with email and password."),
            ("Pre-condition", "The user has an account."),
            ("Main Flow", ["1. User enters email and password.", "2. System finds the account and verifies the password hash.",
                           "3. System returns a signed JWT valid for 12 hours, stored in the browser.", "4. System opens the prediction form."]),
            ("Alternate Flow", ["2a. Wrong email or password: the system shows “Invalid email or password”."]),
            ("Post-condition", "The user is authenticated."),
        ]),
        ("uc3", "UC-03: Reset Password", [
            ("Use Case ID", "UC-03"), ("Use Case Name", "Reset Password"), ("Actor", "User"),
            ("Description", "A user who forgot the password sets a new one."),
            ("Pre-condition", "The user has an account and is not logged in."),
            ("Main Flow", ["1. User selects “Forgot password?” on the login page.",
                           "2. User enters the registered email, the registered phone number and a new password twice.",
                           "3. System verifies that the email and phone number match the same account.",
                           "4. System stores the new password hash and returns to the login page with a success message."]),
            ("Alternate Flow", ["2a. Passwords do not match: an error is shown.", "3a. Email and phone do not match: an error is shown."]),
            ("Post-condition", "The user can log in with the new password."),
        ]),
        ("uc4", "UC-04: Submit Health Data for Prediction", [
            ("Use Case ID", "UC-04"), ("Use Case Name", "Submit Health Data for Prediction"),
            ("Actors", "User (primary), Prediction Engine (secondary)"),
            ("Description", "The user enters twelve clinical values and requests a heart failure risk prediction."),
            ("Pre-condition", "The user is logged in."),
            ("Main Flow", ["1. User fills the General, Medical and Habit sections of the form (help text is shown for the focused field).",
                           "2. User clicks “Predict Risk”.", "3. System validates every field on the client (includes UC: Validate Clinical Input).",
                           "4. Backend authenticates the request and validates the values again.",
                           "5. Prediction Engine returns the risk probability and SHAP contributions.",
                           "6. System generates suggestions, stores the health data and prediction, and shows the result (includes UC-05)."]),
            ("Alternate Flow", ["3a. Missing or out-of-range value: the field is highlighted with a message and nothing is sent.",
                                "4a. Expired token: the user is returned to the login page."]),
            ("Post-condition", "A health data record and its prediction are stored for the user."),
        ]),
        ("uc5", "UC-05: View Prediction Result", [
            ("Use Case ID", "UC-05"), ("Use Case Name", "View Prediction Result"), ("Actor", "User"),
            ("Description", "The user views the status, probabilities and risk level of a prediction, with the contributing factors and suggestions (extension)."),
            ("Pre-condition", "A prediction has been made or selected from history."),
            ("Main Flow", ["1. System shows patient details, the status (Healthy / At Risk), the risk level and the healthy and risk probabilities.",
                           "2. System lists the five most influential factors, each marked as increasing or decreasing the risk.",
                           "3. System lists rule-based suggestions for the patient's abnormal values."]),
            ("Post-condition", "The user understands the predicted risk and its main causes."),
        ]),
        ("uc6", "UC-06: Download PDF Report", [
            ("Use Case ID", "UC-06"), ("Use Case Name", "Download PDF Report"), ("Actor", "User"),
            ("Description", "The user saves a PDF report of a prediction."),
            ("Pre-condition", "A prediction result is displayed."),
            ("Main Flow", ["1. User clicks “Download PDF Report”.",
                           "2. System generates a report containing the result, patient details, all clinical inputs, contributing factors and suggestions.",
                           "3. Browser downloads the file HFP_Report_<name>_<id>.pdf."]),
            ("Post-condition", "The report is saved on the user's device."),
        ]),
        ("uc7", "UC-07: View Prediction History", [
            ("Use Case ID", "UC-07"), ("Use Case Name", "View Prediction History"), ("Actor", "User"),
            ("Description", "The user reviews previous predictions."),
            ("Pre-condition", "The user is logged in."),
            ("Main Flow", ["1. User opens the History page.", "2. System lists the user's predictions, newest first, with date, status, risk level and key values.",
                           "3. User selects “View” to reopen a past result (UC-05)."]),
            ("Alternate Flow", ["2a. No predictions yet: the system shows a link to the prediction form."]),
            ("Post-condition", "Only the user's own records are shown."),
        ]),
        ("uc8", "UC-08: Logout", [
            ("Use Case ID", "UC-08"), ("Use Case Name", "Logout"), ("Actor", "User"),
            ("Description", "The user ends the session."),
            ("Pre-condition", "The user is logged in."),
            ("Main Flow", ["1. User clicks “Logout”.", "2. System removes the token from the browser and opens the login page."]),
            ("Post-condition", "Protected pages require logging in again."),
        ]),
    ]
    for label, title, pairs in cases:
        R.kv_table(f"Use Case Description – {title}", pairs, widths=(1.5, 4.5), font_size=10, label=label)


def chapter3(R, cite):
    P = lambda t, **k: R.para(cite(t), **k)  # noqa: E731
    R.chapter(3, "System Analysis and Design")

    R.heading("3.1 System Analysis", 2)
    P(
        "System analysis identifies what the HFP system must do and models its structure, behaviour and processes "
        "before implementation. The analysis is based on the problems identified in the existing manual process "
        "(Section 2.2) and on the needs of the intended users: patients, clinicians, data analysts and researchers."
    )
    R.heading("3.1.1 Requirement Analysis", 3)
    R.heading("i. Functional Requirements", 4)
    P(
        "The functional requirements of the system are captured in the use case diagram in Figure {fig:usecase}. "
        "The primary actor is the user (a patient or clinician). The secondary actor is the prediction engine, "
        "the trained XGBoost model that the system calls to score health data. Submitting health data always "
        "includes validation and displaying the result, while viewing the contributing factors and suggestions "
        "extends the result view."
    )
    R.figure(GEN / "use_case.png", "Use Case Diagram of the HFP System", width=fit(GEN / "use_case.png", 5.6, 6.6), label="usecase")
    P("The use cases are described in Tables {tab:uc1} to {tab:uc8}.")
    use_cases(R, cite)

    R.heading("ii. Non-Functional Requirements", 4)
    R.bullets([
        "**Accuracy:** the model must discriminate well between high- and low-risk patients, with a balance "
        "between precision and recall. It is evaluated on patients not seen during training "
        f"(the deployed model achieves a ROC-AUC of {META['metrics']['roc_auc']:.3f}).",
        "**Performance:** a prediction must be returned quickly enough for interactive use. The target is under "
        "one second; the measured server time is about 2 ms (Section 4.3).",
        "**Security:** passwords are stored only as salted PBKDF2-SHA256 hashes (310,000 iterations). API access "
        "requires a signed, expiring JWT, and each user can access only their own records.",
        "**Usability:** the interface groups the inputs into General, Medical and Habit sections, shows help text "
        "and units for every field, highlights invalid values and works on mobile screens.",
        "**Interpretability:** every prediction is accompanied by its main contributing factors and plain-language "
        "suggestions.",
        "**Reliability and maintainability:** inputs are validated on both the client and the server. The model, "
        "API and interface are separate modules covered by automated tests.",
        "**Portability:** the system runs in any modern browser (Chrome, Firefox, Edge) and the server runs on "
        "Windows, macOS or Linux with Python 3.11 or newer.",
    ])

    R.heading("3.1.2 Feasibility Analysis", 3)
    P("A feasibility study was carried out to confirm that the proposed system was practical to build and use.")
    R.heading("i. Technical Feasibility", 4)
    P(
        "The system is built entirely with mature, well-documented open-source technologies: Python with "
        "scikit-learn and XGBoost for machine learning, FastAPI for the backend, React for the frontend and "
        "SQLite for storage. The team had prior experience with Python and JavaScript, and the trained model is "
        "small (under 200 KB) and needs no special hardware. A laptop with 8 GB RAM and an Intel Core i5 class "
        "processor is enough for both training and serving. The main technical challenge was the small size of "
        "the available dataset, which was addressed with careful data expansion and leakage-free evaluation. "
        "The project is therefore technically feasible."
    )
    R.heading("ii. Operational Feasibility", 4)
    P(
        "The system requires only a web browser. Users enter values they already find in routine clinical "
        "reports, and the result appears within a second, with an explanation and a printable report. This fits "
        "into a consultation without disrupting existing work. The interface uses familiar web conventions and "
        "contextual help, so minimal training is needed. The system is therefore operationally feasible as a "
        "decision support tool, provided that users understand that it does not replace clinical diagnosis."
    )
    R.heading("iii. Economic Feasibility", 4)
    P(
        "All software used in development and deployment is free and open source, so there are no licensing "
        "costs. Development was done on the team's own computers, and the system can run on a single low-cost "
        "server or an existing hospital machine. The main investment is the team's development time. Against "
        "this low cost, earlier identification of high-risk patients can reduce emergency admissions and support "
        "better use of limited clinical resources. The project is therefore economically feasible."
    )
    R.heading("iv. Schedule Feasibility", 4)
    P(
        "The project was planned over six months, from January to June 2025, as shown in the Gantt chart in "
        "Figure {fig:gantt}. Overlapping phases and the iterative Agile approach allowed testing to begin while "
        "coding continued, and documentation to start before testing finished. All phases were completed within "
        "the academic schedule, so the project was feasible in terms of time."
    )
    R.figure(GEN / "gantt.png", "Gantt Chart of the Project Schedule", width=fit(GEN / "gantt.png", 6.0), label="gantt")

    R.heading("3.1.3 Object Modelling using Class and Object Diagrams", 3)
    P(
        "The analysis class diagram in Figure {fig:classa} shows the main domain concepts and their "
        "relationships. A **User** submits any number of **HealthData** records. Each HealthData record produces "
        "exactly one **Prediction**, which is composed of one to five contributing **Factor** objects and can be "
        "rendered as a **Report**. The **PredictionModel** uses HealthData to create Predictions and their "
        "explanations."
    )
    R.figure(GEN / "class_analysis.png", "Class Diagram of the HFP System", width=fit(GEN / "class_analysis.png", 4.0, 7.4), label="classa")
    P(
        "The object diagram in Figure {fig:objecta} shows a snapshot of these classes at run time, using the "
        "example patient whose prediction is shown in Appendix A: a 60-year-old male patient with an ejection "
        "fraction of 38% received a *Healthy* prediction with a risk probability of 13.96%."
    )
    R.figure(GEN / "object.png", "Object Diagram of the HFP System", width=fit(GEN / "object.png", 5.0, 6.0), label="objecta")

    R.heading("3.1.4 Dynamic Modelling using State and Sequence Diagrams", 3)
    P(
        "The state diagram in Figure {fig:statea} models the states a user passes through. A logged-out user can "
        "register, log in or reset the password. Inside the logged-in state, the user moves between entering "
        "health data, validation, prediction, viewing the result, downloading the report and viewing history. "
        "Logging out or an expired token returns the user to the logged-out state."
    )
    R.figure(GEN / "state.png", "State Diagram of the HFP System", width=fit(GEN / "state.png", 6.0, 6.0), label="statea")
    P(
        "The sequence diagram in Figure {fig:seqa} shows how the user, frontend, backend, database and ML model "
        "interact over time during login, prediction and report download."
    )
    R.figure(GEN / "sequence.png", "Sequence Diagram of the HFP System", width=fit(GEN / "sequence.png", 5.6, 7.2), label="seqa")

    R.heading("3.1.5 Process Modelling using Activity Diagrams", 3)
    P(
        "The activity diagram in Figure {fig:activitya} describes the complete prediction process from the "
        "user's point of view, including the decision points for authentication, input validation, report "
        "download and repeated prediction."
    )
    R.figure(GEN / "activity.png", "Activity Diagram of the Prediction Process", width=fit(GEN / "activity.png", 4.0, 7.6), label="activitya")

    R.heading("3.2 System Design", 2)
    P(
        "The system design refines the analysis models into the actual structure of the implemented system. "
        "Figure {fig:arch} gives an overview of the architecture. An offline machine learning pipeline prepares "
        "the data, trains and compares the models and exports the selected pipeline. The web application loads "
        "this pipeline in the FastAPI backend, which serves the React frontend and stores data in SQLite."
    )
    R.figure(GEN / "architecture.png", "System Architecture (Block Diagram) of the HFP System", width=fit(GEN / "architecture.png", 6.0), label="arch")

    R.heading("3.2.1 Refinement of Class, Object, State, Sequence and Activity Diagrams", 3)
    P(
        "**Refined class diagram.** Figure {fig:classd} maps the domain classes to the implemented modules. In the "
        "frontend, the *PredictionForm*, *Result* and *History* pages use the *ApiClient* module to call the backend, "
        "*AuthProvider* holds the logged-in user, *MedicalInfo* defines the field metadata and validation rules, and "
        "*PDFReportGenerator* builds the report. In the backend, *APIRoutes* exposes the REST endpoints and "
        "delegates to *Predictor* (model inference and explanations), *Security* (hashing and tokens), "
        "*Suggestions* (rule engine) and *Database* (SQLite access). *HealthData* is a Pydantic schema that "
        "validates the twelve clinical inputs."
    )
    R.figure(GEN / "class_design.png", "Refined Class Diagram of the HFP System", width=fit(GEN / "class_design.png", 6.0), label="classd")
    P(
        "**Refined object diagram.** Figure {fig:objectd} shows the objects that exist in the running backend. The "
        "FastAPI application holds a single *Predictor*, loaded once at start-up. The Predictor wraps a "
        "scikit-learn *Pipeline* made of a *StandardScaler* and the tuned *XGBClassifier*."
    )
    R.figure(GEN / "object_design.png", "Refined Object Diagram of the Backend at Run Time", width=fit(GEN / "object_design.png", 4.6, 5.0), label="objectd")
    P(
        "**Refined state diagram.** Figure {fig:stated} refines the prediction step into the states of a single "
        "*POST /api/predict* request on the server. Each state matches a step of the implementation, and the two "
        "failure paths return HTTP 401 (unauthenticated) or 422 (invalid input)."
    )
    R.figure(GEN / "state_design.png", "Refined State Diagram of a Prediction Request", width=fit(GEN / "state_design.png", 3.6, 7.2), label="stated")
    P(
        "**Refined sequence diagram.** Figure {fig:seqd} shows the prediction flow with the actual functions and "
        "endpoints called at each step, from *handleSubmit* in the form to the downloaded PDF file."
    )
    R.figure(GEN / "sequence_design.png", "Refined Sequence Diagram of the Prediction Flow", width=fit(GEN / "sequence_design.png", 6.0), label="seqd")
    P(
        "**Refined activity diagram.** Figure {fig:activityd} details the offline model training process "
        "implemented in *make_dataset.py* and *train.py*. The six models are trained in parallel branches, "
        "evaluated in the same way and compared before the XGBoost pipeline is exported."
    )
    R.figure(GEN / "activity_training.png", "Refined Activity Diagram of the Model Training Pipeline", width=fit(GEN / "activity_training.png", 5.0, 6.4), label="activityd")

    R.heading("3.2.2 Component Diagram", 3)
    P(
        "The component diagram in Figure {fig:component} shows the software components and their dependencies. "
        "The React pages depend on the authentication, API client, PDF and field-metadata components. The API "
        "client is the only component that communicates with the server, through the REST API. On the server, "
        "the FastAPI application depends on the authentication, prediction, suggestion and persistence modules. "
        "The prediction module reads the model artifact produced by the offline training components."
    )
    R.figure(GEN / "component.png", "Component Diagram of the HFP System", width=fit(GEN / "component.png", 6.0), label="component")

    R.heading("3.2.3 Deployment Diagram", 3)
    P(
        "The deployment diagram in Figure {fig:deployment} shows how the components are placed on hardware. The "
        "user's browser runs the React SPA and keeps the JWT in local storage. The application server runs the "
        "FastAPI application on the Uvicorn ASGI server. It also serves the built frontend files, loads the "
        "model artifact and stores data in an SQLite file. The model is trained on a developer workstation and "
        "copied to the server as an artifact."
    )
    R.figure(GEN / "deployment.png", "Deployment Diagram of the HFP System", width=fit(GEN / "deployment.png", 5.6, 6.0), label="deployment")

    R.heading("3.3 Algorithm Details", 2)
    R.heading("3.3.1 Data Preparation and Preprocessing", 3)
    P(
        "**Dataset expansion.** The 299 real patients were expanded to 2000 records by generating 1701 synthetic "
        "patients. Each synthetic patient copies a randomly chosen real patient and then: (i) adds Gaussian noise "
        "of 15% of the feature's standard deviation to each continuous feature, applied in log space for the "
        "skewed laboratory values (CPK, serum creatinine and platelets); (ii) clips each value to its "
        "clinically plausible range and rounds it like the original data; (iii) flips each binary feature with "
        "a probability of 5%; and (iv) flips the label with a probability of 5%, so that the expanded dataset is "
        "not unrealistically easy to separate. Every record keeps a *source_id* identifying its real patient."
    )
    P(
        "**Group-aware split.** The data was split 70/30 into training and test sets with *GroupShuffleSplit* on "
        "*source_id*, so all synthetic copies of a patient fall on the same side of the split. The training set "
        f"has {META['train_rows']} records (209 real patients) and the test set has {META['test_rows']} records "
        "(90 real patients). Cross-validation on the training set uses *StratifiedGroupKFold* with five folds "
        "for the same reason."
    )
    P("**Standardization.** Each feature is standardized using the mean and standard deviation of the training set:")
    R.equation(EQ / "standardize.png")
    P(
        "**Class imbalance.** The positive class is weighted in Random Forest (balanced class weights) and in "
        "XGBoost, where the weight of positive samples is set from the training set:"
    )
    R.equation(EQ / "spw.png", height=Inches(0.48))
    P("This gives scale_pos_weight = 981 / 430 = 2.28 for the training split.")

    R.heading("3.3.2 Logistic Regression and Support Vector Machine", 3)
    P(
        "Logistic Regression models the log-odds of a death event as a linear combination of the standardized "
        "features and converts it into a probability with the sigmoid function:"
    )
    R.equation(EQ / "logreg.png", height=Inches(0.3))
    R.equation(EQ / "sigmoid.png")
    P(
        "The Support Vector Machine uses a radial basis function (RBF) kernel to find a non-linear decision "
        "boundary with maximum margin. Because an SVM does not output probabilities directly, its scores were "
        "calibrated with *CalibratedClassifierCV*. Both models serve as baselines for the tree-based methods."
    )

    R.heading("3.3.3 Decision Tree Classifier", 3)
    P(
        "A decision tree recursively splits the patients on the feature and threshold that best separate the "
        "two classes [@quinlan]. For example, a split might send *ejection fraction < 30* to one branch and "
        "*serum creatinine > 1.5* to another. The quality of a split is measured by the impurity of the "
        "resulting subsets, using entropy or the Gini index:"
    )
    R.equation(EQ / "entropy.png")
    R.equation(EQ / "gini.png")
    P("The split with the highest information gain is chosen at each node:")
    R.equation(EQ / "info_gain.png", height=Inches(0.48))
    P(
        "Splitting stops when a node is pure, the maximum depth is reached, or a node has too few samples. Each "
        "leaf predicts its majority class:"
    )
    R.equation(EQ / "leaf.png", height=Inches(0.32))
    P(
        "To limit overfitting on the small dataset, the tree was restricted to a maximum depth of 5 with at "
        "least 10 samples per leaf. Figure {fig:dt} illustrates the structure of a decision tree."
    )
    R.figure(ORIG / "decision_tree.png", "Decision Tree Classifier", width=Inches(4.6), label="dt")

    R.heading("3.3.4 Random Forest Classifier", 3)
    P(
        "Random Forest builds an ensemble of N decision trees, each trained on a bootstrap sample of the "
        "patients and considering a random subset of features at each split [@breiman]. Figure {fig:rf} shows "
        "this process. The probability of heart failure for patient i is the average of the probabilities "
        "given by the trees:"
    )
    R.figure(ORIG / "random_forest.png", "Random Forest Classifier", width=Inches(4.8), label="rf")
    R.equation(EQ / "rf_prob.png", height=Inches(0.5))
    P("The final class is obtained with the decision threshold θ:")
    R.equation(EQ / "threshold.png", height=Inches(0.3))
    P("The forest used 300 trees with a maximum depth of 8, at least 5 samples per leaf and balanced class weights.")

    R.heading("3.3.5 XGBoost Classifier (Deployed Model)", 3)
    P(
        "XGBoost builds trees sequentially, where each new tree f_t corrects the errors of the current ensemble "
        "[@friedman, chen]. Figure {fig:xgb} illustrates this. At iteration t, it minimizes a regularized "
        "objective made of the training loss and a complexity penalty:"
    )
    R.figure(ORIG / "xgboost.png", "XGBoost Classifier", width=Inches(3.8), label="xgb")
    R.equation(EQ / "xgb_obj.png", height=Inches(0.36))
    R.equation(EQ / "xgb_reg.png", height=Inches(0.5))
    P(
        "Here T is the number of leaves, w_j the leaf weights, and γ and λ control tree complexity. For binary "
        "classification, the loss is the logistic loss:"
    )
    R.equation(EQ / "logloss.png", height=Inches(0.3))
    P("The prediction is updated with a learning rate η, and the final score is converted to a probability with the sigmoid function:")
    R.equation(EQ / "xgb_update.png", height=Inches(0.34))
    P(
        "**Hyperparameter tuning.** XGBoost was tuned with a grid search over 24 combinations, scored by F1-score "
        "with group-aware five-fold cross-validation on the training set only (Table {tab:grid}). Subsampling of "
        "rows and columns (0.8) and L2 regularization (λ = 1) were fixed."
    )
    R.table(
        "XGBoost Hyperparameter Grid and Selected Values",
        ["Hyperparameter", "Values searched", "Selected"],
        [
            ["max_depth", "2, 3, 4", "3"],
            ["n_estimators", "150, 300", "150"],
            ["learning_rate", "0.03, 0.1", "0.03"],
            ["min_child_weight", "1, 5", "1"],
            ["scale_pos_weight", "computed from the training set", "2.28"],
        ],
        widths=(1.8, 2.6, 1.2), label="grid",
    )

    R.heading("3.3.6 Explaining Predictions with TreeSHAP", 3)
    P(
        "For every prediction, the system computes SHAP values φ_j for the twelve features with XGBoost's exact "
        "TreeSHAP algorithm [@lundberg2020] (*pred_contribs=True*). The values satisfy the additivity property, "
        "where φ_0 is the expected model output (in log-odds) and f(x) is the output for the patient:"
    )
    R.equation(EQ / "shap.png", height=Inches(0.42))
    P(
        "The features are sorted by |φ_j|, and the five largest are shown to the user. A positive φ_j means the "
        "feature *increases* the risk, and a negative φ_j means it *decreases* the risk."
    )

    R.heading("3.3.7 Risk Levels and Suggestion Rules", 3)
    P(
        "The risk probability p is converted into a status with a threshold of 0.5 (*At Risk* if p ≥ 0.5, "
        "otherwise *Healthy*), and into one of four risk levels (Table {tab:risk}). A rule engine then produces "
        "suggestions from clinical reference ranges (Table {tab:rules})."
    )
    R.table(
        "Risk Level Thresholds",
        ["Risk probability p", "Risk level", "Status"],
        [["p < 0.25", "Low", "Healthy"], ["0.25 ≤ p < 0.50", "Moderate", "Healthy"],
         ["0.50 ≤ p < 0.75", "High", "At Risk"], ["p ≥ 0.75", "Very High", "At Risk"]],
        widths=(2.0, 1.6, 1.6), label="risk",
    )
    R.table(
        "Rules of the Suggestion Engine",
        ["Condition", "Suggestion given"],
        [
            ["Ejection fraction < 40%", "Reduced pumping function; arrange an echocardiogram review"],
            ["Serum creatinine > 1.5 mg/dL", "Possible reduced kidney function; kidney tests and medication review"],
            ["Serum sodium < 135 mEq/L", "Low sodium; discuss fluid intake and diuretics"],
            ["CPK > 582 mcg/L", "Possible muscle or heart stress; follow-up blood test"],
            ["Platelets outside 150,000–450,000", "Blood work-up advised"],
            ["High blood pressure = yes", "Reduce salt, monitor BP, take medication consistently"],
            ["Diabetes = yes", "Maintain blood sugar control and monitor HbA1c"],
            ["Anaemia = yes", "Iron-rich foods and a haemoglobin check-up"],
            ["Smoking = yes", "Quit smoking"],
            ["Status = At Risk", "Consult a cardiologist soon; watch for warning signs"],
            ["Status = Healthy", "Maintain a heart-healthy lifestyle and routine check-ups"],
        ],
        widths=(2.3, 3.9), font_size=10, label="rules",
    )

    R.heading("3.3.8 Evaluation Metrics", 3)
    P(
        "Models are compared using the confusion matrix counts (TP, TN, FP, FN) on the held-out test set. "
        "Because missing a high-risk patient (a false negative) is costly, recall and F1-score are given more "
        "weight than accuracy alone:"
    )
    R.equation(EQ / "precision.png")
    R.equation(EQ / "recall.png")
    R.equation(EQ / "f1.png", height=Inches(0.46))
    R.equation(EQ / "accuracy.png")
    P(
        "The ROC-AUC measures how well the predicted probabilities rank death-event patients above survivors at "
        "all thresholds. It is independent of the 0.5 threshold."
    )
