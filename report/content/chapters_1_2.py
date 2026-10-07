"""Chapter 1: Introduction and Chapter 2: Background Study and Literature Review."""

from docx.shared import Inches

from .common import GEN, ORIG, fit


def chapter1(R, cite):
    P = lambda t, **k: R.para(cite(t), **k)  # noqa: E731
    R.new_section("decimal", 1)
    R.chapter(1, "Introduction", first=True)

    R.heading("1.1 Introduction", 2)
    P(
        "Heart failure (HF) is a chronic, progressive condition in which the heart cannot pump enough blood to "
        "meet the body's needs. It affects tens of millions of people worldwide and remains a major cause of "
        "hospitalization, poor quality of life and death [@savarese]. Many deaths could be delayed if high-risk "
        "patients were identified early and followed up more closely, but such identification usually depends on "
        "a clinician manually interpreting several isolated laboratory values and clinical signs."
    )
    P(
        "Routine clinical records already contain strong signals of risk. Studies on patients admitted with heart "
        "failure have shown that age, ejection fraction, serum creatinine, serum sodium and comorbidities such as "
        "anaemia and high blood pressure are associated with survival [@ahmad], and that machine learning models "
        "can predict a patient's outcome from these attributes [@chicco]. The Heart Failure Prediction (HFP) "
        "system developed in this project turns this idea into a usable tool: a web application where a user "
        "enters twelve clinical values and immediately receives a risk prediction, an explanation of the factors "
        "behind it, health suggestions and a printable PDF report."
    )
    P(
        "The prediction engine is an XGBoost classifier selected after comparing six machine learning algorithms. "
        "It is served by a FastAPI backend and accessed through a React frontend, with an SQLite database storing "
        "user accounts and prediction history."
    )

    R.heading("1.2 Problem Statement", 2)
    P(
        "In Nepal, as in many low-resource settings, heart failure care is largely reactive. Patient information is "
        "collected on paper or in fragmented hospital systems, and risk assessment depends on the experience of "
        "the individual clinician. There is no simple, data-driven tool that combines a patient's routine clinical "
        "values into a single, explainable risk estimate. As a result:"
    )
    R.bullets([
        "High-risk patients may not be identified until their symptoms worsen.",
        "Assessments of the same patient can differ between clinicians, because they are subjective.",
        "Patients have no easy way to understand which of their clinical values contribute most to their risk.",
        "Clinicians cannot easily keep a structured record of previous risk assessments.",
    ])
    P(
        "This project addresses these problems by building an automated, explainable heart failure risk "
        "prediction system that works from attributes already recorded in routine care."
    )

    R.heading("1.3 Objectives", 2)
    P("The main objective of this project is to develop a machine learning-based web application that predicts "
      "the risk of heart failure from clinical data to support early detection and decision-making. The specific "
      "objectives are:")
    R.bullets([
        "To train and compare machine learning models that predict heart-failure risk from twelve clinical "
        "attributes, and deploy the most suitable model.",
        "To explain each prediction by identifying the clinical factors that increased or decreased the risk.",
        "To provide a secure web application with registration, prediction, history, rule-based suggestions and "
        "downloadable PDF reports.",
    ])

    R.heading("1.4 Scope and Limitation", 2)
    R.heading("1.4.1 Scope", 3)
    R.bullets([
        "**Decision support:** the system provides a risk estimate that can help clinicians and patients decide "
        "when closer follow-up is needed.",
        "**Data handling:** the system validates clinical input and stores each user's health data and "
        "predictions securely for later review.",
        "**Model development:** the project covers data preparation, training and comparison of six classifiers, "
        "evaluation on held-out data and export of the selected model.",
        "**Explainability:** each prediction lists its five most influential factors using SHAP values, and the "
        "system gives rule-based suggestions for abnormal clinical values.",
        "**Reporting:** users can download a PDF report of the prediction and view their prediction history.",
    ])
    R.heading("1.4.2 Limitation", 3)
    R.bullets([
        "**Small source dataset:** the model is derived from 299 real patients; the 2000-record training set "
        "is a synthetic expansion of these patients and cannot add genuinely new clinical information.",
        "**No external validation:** the data comes from a single hospital in Pakistan, and the model has not "
        "been validated on patients from Nepali hospitals.",
        "**Limited risk factors:** only twelve attributes are used; important factors such as ECG findings, "
        "natriuretic peptides and medication history are not considered.",
        "**Follow-up time dependence:** the follow-up period is the strongest predictor in the dataset, but it "
        "is partly a consequence of the outcome rather than a cause, which limits clinical interpretation.",
        "**Not a diagnostic device:** predictions support but do not replace professional medical judgement, "
        "and the system is not integrated with live hospital systems.",
    ])

    R.heading("1.5 Development Methodology", 2)
    P(
        "The project followed the Agile development methodology. Machine learning projects suit an "
        "iterative approach because the dataset, model performance and user interface requirements change as "
        "the work progresses. Development was divided into short iterations (sprints). Each sprint was planned, "
        "designed, developed, tested and reviewed with the supervisor before the next one started, as shown in "
        "Figure {fig:agile}."
    )
    R.figure(ORIG / "agile.png", "Agile Methodology", width=Inches(4.6), label="agile")
    P("The phases of each iteration were applied to the project as follows:")
    R.bullets([
        "**Plan:** define the goals of the sprint, such as preparing the dataset, adding the prediction API or "
        "building the result page, and prioritize the related tasks.",
        "**Design:** prepare UML diagrams, the database schema, the API contract and the user interface layout "
        "for the features of the sprint.",
        "**Develop:** implement the features, for example the training script, the FastAPI endpoints or the "
        "React pages.",
        "**Test:** run automated unit and integration tests and manual checks of the user interface, and fix "
        "the defects found.",
        "**Deploy:** run the updated backend and frontend locally so the supervisor and team members can try "
        "the new features.",
        "**Review:** collect feedback, compare the model metrics with the previous iteration and decide on "
        "improvements.",
        "**Launch:** deliver the final, fully tested system for the final defense and demonstration.",
    ])
    P(
        "The main iterations were: (1) requirement study and dataset analysis, (2) data preparation and model "
        "comparison, (3) backend API with authentication and prediction, (4) frontend pages and PDF report, and "
        "(5) explainability, suggestions, testing and documentation."
    )

    R.heading("1.6 Report Organization", 2)
    P("This report is organized into five chapters:")
    R.bullets([
        "Chapter 1: Introduction presents the problem, objectives, scope, limitations and the development "
        "methodology of the project.",
        "Chapter 2: Background Study and Literature Review explains the clinical and machine learning "
        "concepts used in the project and reviews related research.",
        "Chapter 3: System Analysis and Design describes the requirements, feasibility analysis, object, "
        "dynamic and process models, the refined design, component and deployment diagrams, and the algorithms "
        "used.",
        "Chapter 4: Implementation and Testing describes the tools and the implementation of each module, "
        "the unit and system test cases, and the analysis of the results.",
        "Chapter 5: Conclusion and Future Recommendations summarizes the work and suggests future "
        "improvements.",
    ])
    P("The report ends with the references and the appendices containing screenshots of the system.")


def chapter2(R, cite):
    P = lambda t, **k: R.para(cite(t), **k)  # noqa: E731
    R.chapter(2, "Background Study and Literature Review")

    R.heading("2.1 Background Study", 2)
    R.heading("2.1.1 Clinical Attributes Used for Prediction", 3)
    P(
        "The system uses the twelve attributes of the Heart Failure Clinical Records dataset [@uci], collected by "
        "Ahmad et al. from 299 heart failure patients at the Faisalabad Institute of Cardiology and the Allied "
        "Hospital in Faisalabad, Pakistan, between April and December 2015 [@ahmad]. All patients had left "
        "ventricular systolic dysfunction and were aged 40 to 95 years; 194 were men and 105 were women. The "
        "target attribute, DEATH_EVENT, records whether the patient died during the follow-up period (96 "
        "patients, 32.1%). Table {tab:attributes} describes the attributes as they are used in the HFP input form."
    )
    R.table(
        "Clinical Attributes of the Heart Failure Clinical Records Dataset",
        ["Attribute", "Meaning in the System", "Unit / Values", "Range (mean)"],
        [
            ["age", "Age of the patient", "years", "40–95 (60.8)"],
            ["sex", "Biological sex", "1 = male, 0 = female", "65% male"],
            ["anaemia", "Decrease of red blood cells or haemoglobin", "0 / 1", "43% yes"],
            ["creatinine_phosphokinase", "Level of the CPK enzyme in the blood", "mcg/L", "23–7861 (582)"],
            ["diabetes", "Patient has diabetes", "0 / 1", "42% yes"],
            ["ejection_fraction", "Percentage of blood leaving the heart at each contraction", "%", "14–80 (38.1)"],
            ["high_blood_pressure", "Patient has hypertension", "0 / 1", "35% yes"],
            ["platelets", "Platelets in the blood", "kiloplatelets/mL", "25,100–850,000 (263,358)"],
            ["serum_creatinine", "Level of serum creatinine (kidney function)", "mg/dL", "0.5–9.4 (1.39)"],
            ["serum_sodium", "Level of serum sodium", "mEq/L", "113–148 (136.6)"],
            ["smoking", "Patient smokes", "0 / 1", "32% yes"],
            ["time", "Follow-up period", "days", "4–285 (130.3)"],
            ["DEATH_EVENT", "Patient died during follow-up (target)", "0 / 1", "32.1% yes"],
        ],
        widths=(1.55, 2.35, 1.1, 1.3), font_size=10, label="attributes",
    )
    P(
        "Several attributes have direct clinical meaning for heart failure. A low ejection fraction "
        "(below 40%) indicates reduced pumping function of the left ventricle. An elevated serum creatinine "
        "reflects impaired kidney function, which commonly accompanies and worsens heart failure. Low serum "
        "sodium (hyponatraemia) is associated with fluid overload and poor outcomes. These clinical reference "
        "ranges are also used by the rule-based suggestion module described in Section 3.3.7."
    )
    P(
        "Figure {fig:classdist} shows the class distribution of the original and the expanded datasets. Both are imbalanced, "
        "with about two survivors for every death event, so the models must be evaluated with precision, recall "
        "and F1-score rather than accuracy alone. Figure {fig:corr} shows the correlation between the attributes: the "
        "death event is most strongly (negatively) correlated with follow-up time, and positively correlated "
        "with serum creatinine and age, while ejection fraction and serum sodium are negatively correlated with it."
    )
    R.figure(GEN / "class_distribution.png", "Class Distribution of the Original and Expanded Datasets",
             width=fit(GEN / "class_distribution.png", 6.0), label="classdist")
    R.figure(GEN / "correlation.png", "Correlation Matrix of the Clinical Attributes",
             width=fit(GEN / "correlation.png", 5.6), label="corr")

    R.heading("2.1.2 Heart Failure Prediction as a Classification Problem", 3)
    P(
        "Predicting whether a patient will experience a death event is a supervised binary classification "
        "problem: each patient is described by a feature vector of twelve attributes and labelled 1 (death "
        "event) or 0 (survived). A classifier learns a function that maps the feature vector to the probability "
        "of class 1. In the HFP system, this probability is shown to the user as the *risk probability*, and a "
        "threshold of 0.5 converts it into the status *At Risk* or *Healthy*."
    )
    P(
        "Because the source dataset is small, two practical issues shape the design. First, class "
        "imbalance biases models towards the majority class. The project handles this by weighting the "
        "positive class during training and by selecting models on F1-score. Second, evaluation leakage "
        "can make results look better than they are. The expanded dataset contains several synthetic copies of "
        "each real patient, so a random split would place copies of the same patient in both the training and "
        "test sets. The project prevents this by splitting the data by patient group (Section 3.3.1)."
    )

    R.heading("2.1.3 Ensemble Learning and Gradient Boosting", 3)
    P(
        "Tree-based ensemble methods combine many decision trees into a stronger model. Bagging methods "
        "such as Random Forest train trees independently on bootstrap samples and average their predictions, "
        "which reduces variance [@breiman]. Boosting methods build trees sequentially, each one correcting "
        "the errors of the previous ones. Gradient boosting formalizes this as gradient descent on a loss "
        "function [@friedman], and XGBoost adds regularization, efficient split finding and parallel "
        "computation to this framework [@chen]. These properties make boosted trees accurate on small, tabular "
        "clinical datasets such as the one used in this project."
    )

    R.heading("2.1.4 Explainable Machine Learning", 3)
    P(
        "A risk score is more useful in a clinical setting when it comes with an explanation. SHAP "
        "(SHapley Additive exPlanations) attributes a model's output to its input features using Shapley "
        "values from cooperative game theory, so that the contributions of all features add up to the "
        "prediction [@lundberg2017]. For tree ensembles, TreeSHAP computes these values exactly and efficiently "
        "[@lundberg2020]. The HFP system uses XGBoost's built-in TreeSHAP implementation to show each patient "
        "the five factors that most increased or decreased their predicted risk."
    )

    R.heading("2.1.5 Web Application Architecture", 3)
    P(
        "The HFP system follows a client-server architecture. The React frontend is a single page application "
        "(SPA) that runs in the browser and communicates with the backend through a REST API that exchanges "
        "JSON. The FastAPI backend validates every request against typed schemas, authenticates users with "
        "signed JSON Web Tokens (JWT) and runs the trained model. Passwords are stored only as salted PBKDF2 "
        "hashes. This separation allows the model, the API and the user interface to be developed and tested "
        "independently."
    )

    R.heading("2.2 Literature Review", 2)
    P(
        "Early computational approaches to cardiac diagnosis were based on statistical models. Detrano et al. "
        "developed a probability algorithm for diagnosing coronary artery disease and validated it on patient "
        "groups from Cleveland, Hungary, Switzerland and Long Beach [@detrano]. The study showed that "
        "statistical models built from routine clinical attributes could estimate disease probability across "
        "different populations. Its data later became one of the most widely used benchmark datasets for heart "
        "disease prediction research."
    )
    P(
        "With the growth of machine learning, researchers began to apply non-linear classifiers to cardiac "
        "data. Gudadhe et al. proposed a decision support system for heart disease based on Support Vector "
        "Machines and Artificial Neural Networks, showing that these models can capture complex patterns in "
        "patient attributes [@gudadhe]. Jabbar et al. combined associative classification with a genetic "
        "algorithm to discover compact, accurate rules for heart disease prediction [@jabbar]. Mohan et al. "
        "proposed a hybrid random forest with a linear model (HRFLM) and showed that combining different "
        "techniques improved prediction accuracy over individual classifiers [@mohan]. Together, these studies "
        "suggest that ensemble and hybrid tree-based models are well suited to tabular cardiac data, which "
        "motivated the comparison of tree ensembles in this project."
    )
    P(
        "Closest to this project, Ahmad et al. collected the heart failure dataset used here and applied "
        "survival analysis to it. They found that age, renal dysfunction (serum creatinine), blood pressure, "
        "ejection fraction and anaemia were significant risk factors for mortality [@ahmad]. Chicco and Jurman "
        "then applied several machine learning classifiers to the same dataset and found that Random Forest "
        "performed best. They also showed that a model using only serum creatinine and ejection fraction could "
        "predict survival nearly as well as one using all features [@chicco]. The feature importance obtained "
        "in this project (Section 4.3) agrees with this finding: after follow-up time, serum creatinine and "
        "ejection fraction are the most important features of the XGBoost model."
    )
    P(
        "Deep learning has extended disease prediction to other data types. Lakshmanaprabu et al. developed an "
        "optimal deep learning model for classifying lung cancer from CT images, showing the strength of deep "
        "networks on medical images [@lakshman]. Alaa and van der Schaar proposed an interpretable deep learning "
        "model that forecasts individual disease trajectories over time and explains its predictions to "
        "clinicians [@alaa]. Their emphasis on interpretability is shared by the SHAP-based explanations used in "
        "this project [@lundberg2017, lundberg2020]. However, deep learning offers little advantage on a small "
        "tabular dataset such as the one used here, where tree ensembles remain the stronger choice."
    )
    R.table(
        "Summary of Reviewed Literature",
        ["Ref.", "Approach", "Data", "Relevance to HFP"],
        [
            [cite("[@detrano]"), "Statistical probability algorithm", "Coronary artery disease patients, four centres", "Clinical attributes can estimate cardiac risk"],
            [cite("[@gudadhe]"), "SVM and ANN decision support", "Heart disease records", "Non-linear classifiers for cardiac data"],
            [cite("[@jabbar]"), "Associative classification + genetic algorithm", "Heart disease records", "Rule-based, interpretable prediction"],
            [cite("[@mohan]"), "Hybrid random forest with linear model", "Heart disease records", "Hybrid and ensemble models improve accuracy"],
            [cite("[@ahmad]"), "Survival analysis", "299 heart failure patients", "Source of the dataset; key risk factors"],
            [cite("[@chicco]"), "Machine learning classifiers, feature ranking", "Same 299 patients", "Serum creatinine and EF are most predictive"],
            [cite("[@lakshman]"), "Optimal deep learning", "Lung CT images", "Deep learning for medical imaging"],
            [cite("[@alaa]"), "Interpretable deep learning", "Longitudinal patient data", "Interpretable, individualized prediction"],
        ],
        widths=(0.5, 1.9, 1.8, 2.1), font_size=10, label="lit",
    )
    P(
        "In current practice, heart failure risk is assessed manually. "
        "Clinicians interpret isolated test results using general clinical guidelines, and patient records are "
        "often incomplete or spread across paper files and local hospital systems. Assessments are subjective, "
        "usually happen after symptoms worsen, and do not give patients an explanation of their risk. The HFP "
        "system addresses these gaps. It standardizes data entry, produces a consistent, data-driven risk "
        "estimate, explains the main contributing factors, and keeps a history of previous assessments."
    )
