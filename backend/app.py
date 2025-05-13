from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import logging

# Logging
logging.basicConfig(level=logging.INFO)

# Load model and encoder
model = joblib.load("backend/symptom_model.pkl")
mlb = joblib.load("backend/mlb.pkl")

# FastAPI app
app = FastAPI()

# Input schema
class SymptomRequest(BaseModel):
    symptoms: list[str]

# Medical advice dictionary
medical_advice = {
   "Bacterial Infection": "Antibiotics may be needed. Consult a doctor.",
    "Viral Infection": "Rest and hydration. Use OTC fever reducers if needed.",
    "migraine": "Avoid triggers, use pain relievers, and rest in a dark room.",
    "dengue": "Emergency! Hydrate and seek immediate medical care.",
    "cold": "Rest, fluids, and OTC cold medicine.",
    "Heart disease": "EMERGENCY! Call for medical help immediately.",
    "food poisoning": "Hydrate and monitor. Seek help if severe.",
    "Respiratory Infection": "Consider cough syrup. See doctor if worsens.",
    "Tension Headache": "Rest, hydration, and OTC pain relievers."
}

@app.get("/")
def read_root():
    return {"message": "Backend is running."}

@app.post("/predict")
def predict(request: SymptomRequest):
    logging.info(f"Symptoms received: {request.symptoms}")
    try:
        # Transform input
        input_vector = mlb.transform([request.symptoms])
        prediction = model.predict(input_vector)[0]
        
        # Get advice
        advice = medical_advice.get(prediction, "No specific advice available. Consult a doctor.")

        return {
            "disease": prediction,
            "advice": advice
        }
    except Exception as e:
        logging.error(f"Prediction error: {e}")
        return {"error": str(e)}




