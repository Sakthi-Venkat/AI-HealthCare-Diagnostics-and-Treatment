import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MultiLabelBinarizer
import joblib

# Load dataset
df = pd.read_csv("symptom_illness_dataset.csv")  # Use a real dataset here
X = df["Symptoms"].str.split(",")
y = df["Disease"]

# Vectorize symptoms
mlb = MultiLabelBinarizer()
X_bin = mlb.fit_transform(X)

# Train model
model = RandomForestClassifier()
model.fit(X_bin, y)

# Save model and encoder
joblib.dump(model, "symptom_model.pkl")
joblib.dump(mlb, "mlb.pkl")
