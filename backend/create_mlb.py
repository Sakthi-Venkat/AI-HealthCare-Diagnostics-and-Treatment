import joblib
from sklearn.preprocessing import MultiLabelBinarizer

# List of all possible symptoms
all_symptoms = ["fever","Body pain","cough", "fatigue", "headache"]

# Create MultiLabelBinarizer object
mlb = MultiLabelBinarizer()
mlb.fit([all_symptoms])

# Save the binarizer
joblib.dump(mlb, "mlb.pkl")

print("mlb.pkl file created successfully ✅")
