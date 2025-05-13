import joblib
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import MultiLabelBinarizer
import os

# Sample training data
X = [
    ["fever", "severe body pain", "sore throat"],
    ["headache", "fatigue", "nausea"],
    ["rash", "high fever", "joint pain", "muscle pain"],
    ["sneezing", "cough", "runny nose"],
    ["chest pain", "shortness of breath", "fatigue"],
    ["abdominal pain", "diarrhea", "nausea"],
    ["fever"],  # Single symptom case
    ["cough"],  # Single symptom case
    ["headache"]  # Single symptom case
]

y = [
    "Bacterial Infection",
    "migraine",
    "dengue",
    "cold",
    "Heart disease",
    "food poisoning",
    "Viral Infection",  # For single fever
    "Respiratory Infection",  # For single cough
    "Tension Headache"  # For single headache
]

# Train
mlb = MultiLabelBinarizer()
X_encoded = mlb.fit_transform(X)
model = MultinomialNB()
model.fit(X_encoded, y)

# Ensure output path exists
os.makedirs("backend", exist_ok=True)

# Save model and encoder
joblib.dump(model, "backend/symptom_model.pkl")
joblib.dump(mlb, "backend/mlb.pkl")




