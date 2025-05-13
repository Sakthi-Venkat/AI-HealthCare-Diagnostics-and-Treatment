import requests
from langchain.tools import tool

@tool
def symptom_checker(symptoms: str) -> str:
    symptom_list = symptoms.split(", ")
    response = requests.post("http://localhost:8000/predict", json={"symptoms": symptom_list})
    result = response.json()
    return f"The predicted disease is: {result['disease']}"
