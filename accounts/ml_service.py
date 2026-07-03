"""
ML service: wraps the trained RandomForest diabetes model.
The model is loaded once at import time; predict_diabetes_risk() is
called per request. Falls back to rule-based scoring on any error.
"""

import logging
import os

import joblib
import numpy as np
import pandas as pd
from django.conf import settings

logger = logging.getLogger(__name__)

_MODEL_PATH = os.path.join(settings.BASE_DIR, "ml", "diabet_detector_model.pkl")

# Load once at startup. If this fails the module still imports cleanly —
# predict_diabetes_risk() will detect _model is None and fall back.
_model = None
try:
    _model = joblib.load(_MODEL_PATH)
except Exception as exc:
    logger.error("Failed to load diabetes ML model from %s: %s", _MODEL_PATH, exc)

# Pima diabetes dataset medians for features we don't collect.
# These are population-level defaults; predictions will improve once
# we add per-user collection of these fields.
_PIMA_MEDIANS = {
    "Pregnancies": 3,
    "SkinThickness": 23,
    "Insulin": 30,
    "DiabetesPedigreeFunction": 0.47,
}

# Column names the model was trained on (Uzbek, from train_model.py).
_FEATURE_COLS = [
    "Homiladorlik_soni",   # Pregnancies
    "Glyukoza",            # Glucose
    "Qon_bosimi",          # BloodPressure (diastolic)
    "Teri_qalinligi",      # SkinThickness
    "Insulin",             # Insulin
    "BMI_Vazn",            # BMI
    "Diabet_Pedigree",     # DiabetesPedigreeFunction
    "Yoshi",               # Age
]


def predict_diabetes_risk(profile):
    """
    Returns {'risk_class': 0|1, 'risk_percent': float} or None if
    critical inputs are missing. Falls back to rule-based score on failure.

    BloodPressure maps to bp_diastolic to match the Pima dataset convention
    (the dataset's "BloodPressure" column is diastolic mmHg).
    """
    if profile.blood_glucose is None:
        return None

    if _model is None:
        return _rule_based_fallback(profile)

    try:
        age = _resolve_age(profile)

        # Pima dataset uses mg/dL; our profile stores mmol/L → convert.
        glucose_mgdl = round(profile.blood_glucose * 18.0182, 1)

        features = {
            "Homiladorlik_soni": _PIMA_MEDIANS["Pregnancies"],
            "Glyukoza": glucose_mgdl,
            "Qon_bosimi": profile.bp_diastolic if profile.bp_diastolic is not None else 72,
            "Teri_qalinligi": _PIMA_MEDIANS["SkinThickness"],
            "Insulin": _PIMA_MEDIANS["Insulin"],
            "BMI_Vazn": profile.bmi if profile.bmi is not None else 27.3,
            "Diabet_Pedigree": _PIMA_MEDIANS["DiabetesPedigreeFunction"],
            "Yoshi": age if age is not None else 33,
        }

        X = pd.DataFrame([features], columns=_FEATURE_COLS)

        risk_class = int(_model.predict(X)[0])
        proba = _model.predict_proba(X)[0]
        risk_percent = round(float(proba[1]) * 100, 1)

        return {"risk_class": risk_class, "risk_percent": risk_percent}

    except Exception as exc:
        logger.error("ML prediction failed: %s", exc)
        return _rule_based_fallback(profile)


def _resolve_age(profile):
    """Return age from profile.age or computed from birth_date."""
    if profile.age is not None:
        return profile.age
    if profile.birth_date is not None:
        from datetime import date
        today = date.today()
        bd = profile.birth_date
        return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
    return None


def _rule_based_fallback(profile):
    """Wrap the existing rule-based score in the same dict shape."""
    score = profile.calculate_risk_score()
    return {"risk_class": 1 if score >= 50 else 0, "risk_percent": float(score)}
