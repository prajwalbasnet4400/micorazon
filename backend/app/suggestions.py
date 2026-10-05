"""Rule-based lifestyle and follow-up suggestions shown alongside a prediction.

Thresholds follow commonly cited clinical reference ranges. Suggestions are general
guidance to discuss with a clinician, not a substitute for medical advice.
"""


def build_suggestions(inputs: dict, status: str) -> list[str]:
    tips: list[str] = []

    if inputs["ejection_fraction"] < 40:
        tips.append(
            "Ejection fraction is below 40%, suggesting reduced heart pumping function. "
            "Arrange an echocardiogram review with a cardiologist."
        )
    if inputs["serum_creatinine"] > 1.5:
        tips.append(
            "Serum creatinine is elevated (> 1.5 mg/dL), which may indicate reduced kidney function. "
            "Kidney function tests and medication review are recommended."
        )
    if inputs["serum_sodium"] < 135:
        tips.append(
            "Serum sodium is low (< 135 mEq/L). Discuss fluid intake and diuretic use with your doctor."
        )
    if inputs["creatinine_phosphokinase"] > 582:
        tips.append(
            "Creatinine phosphokinase is above the normal range, which can reflect muscle or heart stress. "
            "Consider a follow-up blood test."
        )
    if not 150_000 <= inputs["platelets"] <= 450_000:
        tips.append("Platelet count is outside the normal range (150,000-450,000). A blood work-up is advised.")
    if inputs["high_blood_pressure"]:
        tips.append(
            "Keep blood pressure under control: reduce salt intake, monitor BP regularly and take "
            "prescribed medication consistently."
        )
    if inputs["diabetes"]:
        tips.append("Maintain good blood sugar control through diet, activity and regular HbA1c monitoring.")
    if inputs["anaemia"]:
        tips.append("Anaemia was reported. Iron-rich foods and a haemoglobin check-up are recommended.")
    if inputs["smoking"]:
        tips.append("Quitting smoking is one of the most effective ways to reduce heart failure risk.")

    if status == "At Risk":
        tips.append(
            "Your predicted risk is high. Please consult a cardiologist soon for a full clinical evaluation."
        )
        tips.append(
            "Watch for warning signs such as breathlessness, swelling of the legs, rapid weight gain or chest "
            "pain, and seek immediate care if they occur."
        )
    else:
        tips.append("Keep up a heart-healthy lifestyle: balanced diet, regular exercise and routine check-ups.")

    return tips
