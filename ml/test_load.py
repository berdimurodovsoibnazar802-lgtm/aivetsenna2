import sys
import os

# Run from repo root or ml/ — resolve .pkl paths relative to this file
ML_DIR = os.path.dirname(os.path.abspath(__file__))

import joblib
import numpy as np

print("Loading models...")

diabetes_model = joblib.load(os.path.join(ML_DIR, "diabet_detector_model.pkl"))
print("  [OK] diabet_detector_model.pkl loaded")

insurance_model = joblib.load(os.path.join(ML_DIR, "insurance_price_model.pkl"))
print("  [OK] insurance_price_model.pkl loaded")

# Test patient from avatar_agent.py
# [Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age]
sample = np.array([[2, 168, 85, 25, 0, 38.2, 0.78, 45]])

predicted_class = diabetes_model.predict(sample)[0]
proba = diabetes_model.predict_proba(sample)[0]
risk_pct = proba[1] * 100  # probability of class 1 (diabetic)

print("\n--- Diabetes Model Prediction ---")
print(f"  Predicted class : {predicted_class}  (0=No diabetes, 1=Diabetes)")
print(f"  Risk probability: {risk_pct:.1f}%")
print(f"  Class probabilities: No={proba[0]*100:.1f}%  Yes={proba[1]*100:.1f}%")
print("\nAll models loaded and predicted successfully.")
