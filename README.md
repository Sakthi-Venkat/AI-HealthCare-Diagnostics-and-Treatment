# 🩺 Health AI Dashboard with Chatbot

An AI-powered Health Dashboard built with **Streamlit** that allows users to:
- Chat with an intelligent healthcare assistant 🤖
- Predict diseases based on symptoms 💡
- Get medication guidance 💊
- Start video consultations 📞
- Upload medical documents 📄
- Simulate emergency calls 🚨

---

## 📌 Features

- **User Authentication** (Sign up/Login)
- **AI Health Chatbot** (LLM-powered)
- **Multilingual Symptom Translation** using Google Translate
- **Disease Prediction API Integration**
- **Medical Advice & Medications**
- **Video Call Integration via Jitsi**
- **Secure Document Upload & Viewing**
- **Simulated Dial Pad for Emergency Calling**

---

## 🛠️ Tech Stack

| Component     | Technology                 |
|--------------|----------------------------|
| Frontend     | Streamlit                  |
| Chatbot UI   | Gradio (integrated)        |
| Backend API  | FastAPI (runs on port 8000)|
| Translation  | Googletrans                |
| NLP          | spaCy + SciSpacy           |
| Storage      | JSON (for user auth)       |

---

## ⚙️ Installation

### 1. Clone the Repository

git clone https://github.com/your-username/health-ai-dashboard.git
cd health-ai-dashboard

2. Create Virtual Environment :
python -m venv .venv
# Activate:
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

3. Install Requirements :
pip install -r requirements.txt

🚀 Running the Application :
1. Start the Backend (FastAPI)
cd backend
uvicorn app:app --reload --port 8000

2. Start the Streamlit Frontend :
cd frontend
streamlit run app.py
Then open in your browser: http://localhost:8501

💬 Chatbot Setup
The chatbot is embedded in the Streamlit app and communicates with the FastAPI backend at /predict.

Ensure backend/app.py exposes a /predict endpoint that accepts:

json:
{
  "symptoms": ["headache", "fever"]
}
And returns:

json:
{
  "disease": "Viral Infection",
  "advice": "Drink fluids and rest"
}
You may also include natural language input with spaCy/SciSpacy support.

📁 Project Structure :

health-ai-dashboard/
├── backend/
│   └── app.py                # FastAPI disease predictor
├── frontend/
│   ├── app.py                # Streamlit UI
│   └── users.json            # Stores user accounts
├── requirements.txt
└── README.md
🧪 Sample Users
Use the signup screen or manually add users in users.json:

json file:

{
  "Nikil": "vk@18",
}

🧠 Future Enhancements :

=> Real-time symptom parser using NLP

=> Chat history saving

=> Firebase / DB integration for secure user auth

=> Appointment booking with doctors


