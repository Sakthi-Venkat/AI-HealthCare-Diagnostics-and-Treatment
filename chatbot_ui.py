import gradio as gr
import requests
from translate import translate_text

API_URL = "http://127.0.0.1:8000/predict"

# Supported languages (code: label)
LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "ta": "Tamil",
    "hi": "Hindi",
    "zh": "Chinese",
    "ar": "Arabic",
    "ru": "Russian",
    "ja": "Japanese"
}

def get_prediction(symptoms, lang_code):
    try:
        # Translate symptoms to English
        symptoms_en = translate_text(symptoms, source_lang=lang_code, target_lang="en")

        # Clean input
        symptoms_list = [s.strip() for s in symptoms_en.split(",") if s.strip()]

        # Request prediction
        response = requests.post(API_URL, json={"symptoms": symptoms_list})
        response.raise_for_status()
        result = response.json()

        # Format result in English
        output_en = f"🧠 Predicted Disease: {result['disease']}\n💡 Medical Advice: {result['advice']}"

        # Translate result back to user's language
        output_translated = translate_text(output_en, source_lang="en", target_lang=lang_code)
        return output_translated

    except Exception as e:
        return f"⚠️ Error: {str(e)}"

iface = gr.Interface(
    fn=get_prediction,
    inputs=[
        gr.Textbox(label="Enter your symptoms", placeholder="e.g. fever, cough"),
        gr.Dropdown(label="Select your language", choices=[(v, k) for k, v in LANGUAGES.items()], value="English")
    ],
    outputs=gr.Textbox(label="Predicted Disease & Advice (in your language)"),
    title="🌍 Multilingual AI Healthcare Chatbot",
    description="Enter symptoms and choose your language. The chatbot will respond in that language."
)

if __name__ == "__main__":
    iface.launch()








