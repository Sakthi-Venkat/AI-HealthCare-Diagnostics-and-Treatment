import streamlit as st
import requests
import json
import base64
from deep_translator import GoogleTranslator
import os
from datetime import datetime, timedelta
import pandas as pd
import uuid

# --- Constants ---
API_URL = "http://localhost:8000/predict"
USER_DB = "users.json"
DOCTOR_DB = "doctors.json"
APPOINTMENT_DB = "appointments.json"
CHAT_DB = "doctor_chats.json"

# --- Page Configuration ---
st.set_page_config(
    page_title="Health AI Dashboard",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subheader {
        font-size: 1.8rem;
        color: #3498db;
        margin-bottom: 1rem;
    }
    .card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .sidebar .sidebar-content {
        background-color: #f1f8ff;
    }
    .stButton>button {
        background-color: #3498db;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #2980b9;
    }
    .danger-button>button {
        background-color: #e74c3c !important;
    }
    .success-button>button {
        background-color: #2ecc71 !important;
    }
    .chat-message {
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .chat-outgoing {
        background-color: #e3f2fd;
        margin-left: 20%;
        border-radius: 10px 10px 0px 10px;
    }
    .chat-incoming {
        background-color: #f1f1f1;
        margin-right: 20%;
        border-radius: 10px 10px 10px 0px;
    }
    .chat-time {
        font-size: 0.7rem;
        color: #7f8c8d;
        text-align: right;
    }
    .language-selector {
        padding: 5px;
        background-color: #f8f9fa;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)


# --- File Operations ---
def load_json_file(filename, default=None):
    """Load data from JSON file"""
    if default is None:
        default = {}
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # Create empty file if it doesn't exist
        if not os.path.exists(filename):
            with open(filename, "w") as f:
                json.dump(default, f)
        return default

def save_json_file(filename, data):
    """Save data to JSON file"""
    with open(filename, "w") as f:
        json.dump(data, f)


# --- User Authentication Functions ---
def load_users():
    """Load user database from JSON file"""
    return load_json_file(USER_DB)

def save_user(username, password):
    """Save new user to database"""
    users = load_users()
    users[username] = {
        "password": password,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "language": "en"  # Default language
    }
    save_json_file(USER_DB, users)

def login_user(username, password):
    """Validate user credentials"""
    users = load_users()
    if username in users:
        return users[username].get("password") == password if isinstance(users[username], dict) else users[username] == password
    return False

def update_user_language(username, language_code):
    """Update user's preferred language"""
    users = load_users()
    if username in users and isinstance(users[username], dict):
        users[username]["language"] = language_code
        save_json_file(USER_DB, users)

def get_user_language(username):
    """Get user's preferred language"""
    users = load_users()
    if username in users and isinstance(users[username], dict):
        return users[username].get("language", "en")
    return "en"


# --- Doctor Management Functions ---
def load_doctors():
    """Load doctors database"""
    # Define some sample doctors if file doesn't exist
    default_doctors = {
        "dr_smith": {
            "name": "Dr. Aishwarya Sakthi",
            "specialty": "General Practitioner",
            "languages": ["English", "Tamil"],
            "availability": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "image": "https://picsum.photos/seed/doctor1/100/100",
            "bio": "Board-certified general practitioner with 15 years of experience in family medicine."
        },
        "dr_patel": {
            "name": "Dr. M.G.Ramachandran",
            "specialty": "Cardiologist",
            "languages": ["English", "Hindi", "Malayalam"],
            "availability": ["Monday", "Wednesday", "Friday"],
            "image": "https://picsum.photos/seed/doctor2/100/100",
            "bio": "Cardiologist with expertise in preventive care and management of heart conditions."
        },
        "dr_garcia": {
            "name": "Dr. Abinaya Raju",
            "specialty": "Pediatrician",
            "languages": ["English", "Tamil", "Kannada"],
            "availability": ["Tuesday", "Thursday", "Saturday"],
            "image": "https://picsum.photos/seed/doctor3/100/100",
            "bio": "Pediatrician specializing in infant and adolescent care with a focus on developmental health."
        },
        "dr_chen": {
            "name": "Dr. Arjun Kumar.M",
            "specialty": "Dermatologist",
            "languages": ["English", "Hindi", "Cantonese"],
            "availability": ["Monday", "Tuesday", "Thursday"],
            "image": "https://picsum.photos/seed/doctor4/100/100",
            "bio": "Dermatologist with expertise in skin conditions and cosmetic procedures."
        },
        "dr_kumar": {
            "name": "Dr. Kalaivani.J",
            "specialty": "Psychiatrist",
            "languages": ["English", "Hindi", "Tamil"],
            "availability": ["Wednesday", "Thursday", "Friday"],
            "image": "https://picsum.photos/seed/doctor5/100/100",
            "bio": "Psychiatrist specializing in anxiety, depression, and stress management."
        }
    }
    return load_json_file(DOCTOR_DB, default_doctors)

# --- Appointment Management Functions ---
def load_appointments():
    """Load appointments database"""
    return load_json_file(APPOINTMENT_DB)

def save_appointment(username, doctor_id, date, time, reason):
    """Save new appointment"""
    appointments = load_appointments()
    
    # Create user's appointments list if it doesn't exist
    if username not in appointments:
        appointments[username] = []
    
    # Generate unique appointment ID
    appointment_id = str(uuid.uuid4())
    
    # Add new appointment
    appointments[username].append({
        "id": appointment_id,
        "doctor_id": doctor_id,
        "date": date,
        "time": time,
        "reason": reason,
        "status": "Scheduled",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    save_json_file(APPOINTMENT_DB, appointments)
    return appointment_id

def get_user_appointments(username):
    """Get appointments for a specific user"""
    appointments = load_appointments()
    return appointments.get(username, [])

def cancel_appointment(username, appointment_id):
    """Cancel a specific appointment"""
    appointments = load_appointments()
    
    if username in appointments:
        for appointment in appointments[username]:
            if appointment.get("id") == appointment_id:
                appointment["status"] = "Cancelled"
                save_json_file(APPOINTMENT_DB, appointments)
                return True
    
    return False

# --- Doctor Chat Functions ---
def load_doctor_chats():
    """Load doctor chats database"""
    return load_json_file(CHAT_DB)

def get_user_doctor_chats(username, doctor_id):
    """Get chat history between user and doctor"""
    chats = load_doctor_chats()
    
    chat_key = f"{username}_{doctor_id}"
    return chats.get(chat_key, [])

def save_doctor_chat_message(username, doctor_id, message, is_from_user=True):
    """Save a new chat message"""
    chats = load_doctor_chats()
    
    chat_key = f"{username}_{doctor_id}"
    if chat_key not in chats:
        chats[chat_key] = []
    
    chats[chat_key].append({
        "message": message,
        "from_user": is_from_user,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    save_json_file(CHAT_DB, chats)


# --- Language Support ---
# Dictionary of language codes and names
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

def translate_text(text, target_lang="en", source_lang="en"):
    """Translate text to target language"""
    if target_lang == source_lang or not text:
        return text
    
    try:
        return GoogleTranslator(source=source_lang, target=target_lang).translate(text)
    except Exception:
        # Return original text if translation fails
        return text


# --- Authentication Pages ---
def login_page():
    """Display login form"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 class="subheader">🔐 Login</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            login_clicked = st.button("🔑 Login", use_container_width=True)
        
    with col2:
        st.markdown("""
        ### Welcome Back!
        Please enter your credentials to access your health dashboard.
        
        Need assistance? Contact our support team.
        """)
    
    if login_clicked:
        if login_user(username, password):
            st.session_state.user = username
            st.session_state.user_language = get_user_language(username)
            st.success(f"Welcome back, {username}! Redirecting to dashboard...")
            st.rerun()
        else:
            st.error("❌ Invalid username or password. Please try again.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def signup_page():
    """Display signup form"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 class="subheader">📝 Create Account</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        username = st.text_input("Choose Username", key="signup_username")
        password = st.text_input("Create Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
        
        signup_clicked = st.button("✅ Create Account", use_container_width=True)
    
    with col2:
        st.markdown("""
        ### Join Health AI
        Creating an account gives you access to:
        - Personalized health recommendations
        - Secure document storage
        - Video consultations with healthcare providers
        - Emergency services access
        - Doctor appointment booking
        - Doctor chat messaging
        """)
    
    if signup_clicked:
        if username.strip() == "":
            st.warning("⚠️ Username cannot be empty.")
        elif password.strip() == "":
            st.warning("⚠️ Password cannot be empty.")
        elif password != confirm_password:
            st.warning("⚠️ Passwords do not match.")
        elif username in load_users():
            st.warning("⚠️ Username already exists. Please choose another.")
        else:
            save_user(username, password)
            st.success("✅ Account created successfully! Please log in.")
    
    st.markdown('</div>', unsafe_allow_html=True)


# --- Feature Pages ---
def chatbot():
    """Multilingual Health Chatbot"""
    current_lang = st.session_state.user_language
    
    # Translate the page content
    title = translate_text("💬 Multilingual Health Chatbot", current_lang)
    description = translate_text("Tell us how you're feeling, and our AI will help identify possible conditions and provide guidance in your preferred language.", current_lang)
    placeholder = translate_text("e.g. Fever, Cough, Headache, Fatigue", current_lang)
    btn_text = translate_text("🔍 Get Diagnosis", current_lang)
    symptoms_label = translate_text("Describe your symptoms", current_lang)
    lang_label = translate_text("Choose your language", current_lang)
    
    st.markdown(f'<h2 class="subheader">{title}</h2>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(description)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        symptoms_input = st.text_area(
            symptoms_label,
            placeholder=placeholder,
            height=150
        )
    
    with col2:
        selected_lang_label = st.selectbox(lang_label, list(LANGUAGES.values()), 
                                          index=list(LANGUAGES.keys()).index(current_lang))
        # Map selected language label back to its code
        lang_code = [k for k, v in LANGUAGES.items() if v == selected_lang_label][0]
        
        # Update user's preferred language if changed
        if lang_code != current_lang:
            update_user_language(st.session_state.user, lang_code)
            st.session_state.user_language = lang_code
    
    diagnosis_clicked = st.button(btn_text, use_container_width=True)
    
    if diagnosis_clicked and symptoms_input:
        with st.spinner(translate_text("Analyzing your symptoms...", lang_code)):
            try:
                # Translate input to English
                translated_input = GoogleTranslator(source=lang_code, target="en").translate(symptoms_input)
                symptoms_list = [s.strip() for s in translated_input.split(",") if s.strip()]
                
                # API call to FastAPI backend
                response = requests.post(API_URL, json={"symptoms": symptoms_list})
                response.raise_for_status()
                result = response.json()
                
                # Create a nicely formatted result
                result_en = f"🔍 **Possible Condition**: {result['disease']}\n\n💡 **Recommendations**: {result['advice']}"
                
                # Translate output to user's language
                result_translated = GoogleTranslator(source="en", target=lang_code).translate(result_en)
                
                st.markdown('<div style="background-color:#e3f2fd; padding:15px; border-radius:5px; border-left:5px solid #3498db;">', unsafe_allow_html=True)
                st.markdown(result_translated)
                st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"⚠️ {translate_text('Error', lang_code)}: {str(e)}")
    elif diagnosis_clicked and not symptoms_input:
        st.warning(f"⚠️ {translate_text('Please describe your symptoms first.', lang_code)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def medication_guide():
    """Medication Reference Guide"""
    current_lang = st.session_state.user_language
    
    # Translate the page content
    title = translate_text("💊 Medication Guide", current_lang)
    description = translate_text("Browse common medications for various conditions. **Note**: Always consult with a healthcare professional before taking any medication.", current_lang)
    select_condition = translate_text("Select Condition", current_lang)
    recommended_meds = translate_text("Recommended Medications:", current_lang)
    disclaimer = translate_text("⚠️ This information is for educational purposes only and is not a substitute for professional medical advice.", current_lang)
    
    st.markdown(f'<h2 class="subheader">{title}</h2>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(description)
    
    # Dictionary of diseases and their medications
    meds = {
        "Bacterial Infection": {
            "medications": ["Amoxicillin", "Azithromycin"],
            "description": "Antibiotics that fight bacteria in your body. Complete the full course even if you feel better."
        },
        "Viral Infection": {
            "medications": ["Paracetamol", "Rest & fluids"],
            "description": "Most viral infections resolve with rest, fluids and symptom management. Antibiotics are not effective."
        },
        "Migraine": {
            "medications": ["Ibuprofen", "Sumatriptan"],
            "description": "Pain relievers and triptans can help relieve migraine symptoms. Rest in a dark, quiet room."
        },
        "Dengue": {
            "medications": ["ORS", "Paracetamol (no NSAIDs!)"],
            "description": "Important: Avoid aspirin and NSAIDs as they can increase bleeding risk. Focus on hydration."
        },
        "Common Cold": {
            "medications": ["Antihistamines", "Cough syrup"],
            "description": "Symptom management is key. Get plenty of rest and stay hydrated."
        },
        "Heart Disease": {
            "medications": ["Nitroglycerin", "Aspirin (emergency)"],
            "description": "Emergency medications only. Seek immediate medical attention for chest pain."
        },
        "Food Poisoning": {
            "medications": ["ORS", "Loperamide"],
            "description": "Focus on rehydration. Severe symptoms require medical attention."
        },
        "Respiratory Infection": {
            "medications": ["Cough syrup", "Steam inhalation"],
            "description": "Manage symptoms and get plenty of rest. Seek medical care if breathing becomes difficult."
        },
        "Tension Headache": {
            "medications": ["Ibuprofen", "Paracetamol"],
            "description": "Pain relievers can help. Consider stress management techniques."
        }
    }
    
    # Translate diseases and descriptions
    translated_meds = {}
    for disease, info in meds.items():
        translated_disease = translate_text(disease, current_lang)
        translated_description = translate_text(info["description"], current_lang)
        translated_medications = [translate_text(med, current_lang) for med in info["medications"]]
        
        translated_meds[translated_disease] = {
            "medications": translated_medications,
            "description": translated_description,
            "original_disease": disease  # Keep original for reference
        }
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        disease = st.selectbox(select_condition, list(translated_meds.keys()))
    
    with col2:
        if disease:
            st.markdown(f"### {disease}")
            st.markdown(translated_meds[disease]["description"])
            
            st.markdown(f"#### {recommended_meds}")
            for med in translated_meds[disease]["medications"]:
                st.markdown(f"- **{med}**")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Additional disclaimer
    st.info(disclaimer)

def video_call():
    """Video Consultation Interface"""
    current_lang = st.session_state.user_language
    
    # Translate the page content
    title = translate_text("📞 Video Consultation", current_lang)
    subtitle = translate_text("Start a Secure Video Call", current_lang)
    description = translate_text("""
    Connect with healthcare providers or family members through our secure video call service.
    
    **How it works:**
    1. Click the button below to generate a secure meeting link
    2. Share the link with your doctor or family member
    3. Join the call from any device with a browser
    """, current_lang)
    meeting_link_text = translate_text("Your Secure Meeting Link:", current_lang)
    start_call_text = translate_text("🔗 Start Video Call Now", current_lang)
    image_caption = translate_text("Telemedicine connects you with healthcare professionals remotely", current_lang)
    
    st.markdown(f'<h2 class="subheader">{title}</h2>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"### {subtitle}")
        st.markdown(description)
        
        call_link = f"https://meet.jit.si/healthroom_{st.session_state.user}_{datetime.now().strftime('%Y%m%d')}"
        
        st.markdown(f"#### {meeting_link_text}")
        st.code(call_link)
        
        st.markdown(f"[{start_call_text}]({call_link})", unsafe_allow_html=True)
    
    with col2:
        st.image("https://picsum.photos/seed/telemedicine/400/300", caption=image_caption)
    
    st.markdown('</div>', unsafe_allow_html=True)

def upload_documents():
    """Medical Document Upload and Viewer"""
    current_lang = st.session_state.user_language
    
    # Translate the page content
    title = translate_text("📄 Medical Documents", current_lang)
    subtitle = translate_text("Upload Documents", current_lang)
    description = translate_text("""
    Securely store and view your medical records, prescriptions, and test results.
    
    **Supported formats:**
    - PDF documents
    - Images (JPG, PNG)
    
    Your files are stored securely and only accessible to you.
    """, current_lang)
    choose_file = translate_text("Choose a file", current_lang)
    doc_preview = translate_text("Document Preview", current_lang)
    file_details_text = translate_text("File Details", current_lang)
    viewer_text = translate_text("Your uploaded documents will appear here for preview.", current_lang)
    
    st.markdown(f'<h2 class="subheader">{title}</h2>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"### {subtitle}")
        st.markdown(description)
        
        uploaded_file = st.file_uploader(choose_file, type=["pdf", "png", "jpg", "jpeg"])
    
    with col2:
        if uploaded_file:
            file_details = {
                translate_text("Filename", current_lang): uploaded_file.name,
                translate_text("File Type", current_lang): uploaded_file.type,
                translate_text("Size", current_lang): f"{round(uploaded_file.size / 1024, 2)} KB"
            }
            
            st.markdown(f"### {doc_preview}")
            
            # Create expandable section for file details
            with st.expander(file_details_text):
                for key, value in file_details.items():
                    st.markdown(f"**{key}:** {value}")
            
            # Display the document
            if uploaded_file.type == "application/pdf":
                base64_pdf = base64.b64encode(uploaded_file.read()).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="500" style="border: none;"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
            else:
                st.image(uploaded_file, caption=doc_preview, use_column_width=True)
        else:
            st.markdown(f"""
            ### {doc_preview}
            
            {viewer_text}
            """)
    
    st.markdown('</div>', unsafe_allow_html=True)

def emergency_call():
    """Emergency Contact Interface"""
    current_lang = st.session_state.user_language
    
    # Translate the page content
    title = translate_text("🚨 Emergency Services", current_lang)
    contacts_title = translate_text("Emergency Contacts", current_lang)
    dialpad_title = translate_text("Emergency Dial Pad", current_lang)
    firstaid_title = translate_text("First Aid Tips", current_lang)
    call_ambulance = translate_text("📞 Call Ambulance (108)", current_lang)
    calling_emergency = translate_text("🚑 Calling Emergency Services: 108", current_lang)
    number_to_dial = translate_text("Number to dial", current_lang)
    call_button = translate_text("📞 Call", current_lang)
    clear_button = translate_text("🔄 Clear", current_lang)
    calling_text = translate_text("📞 Calling:", current_lang)
    
    emergency_contacts = translate_text("""
    **Common Emergency Numbers:**
    - 📞 Ambulance: 108
    - 🚓 Police: 100
    - 🚒 Fire: 101
    - 🏥 Medical Helpline: 104
    """, current_lang)
    
    firstaid_tips = translate_text("""
    **While waiting for help:**
    
    - **Bleeding**: Apply direct pressure to wound
    - **Burns**: Cool with running water for 10 mins
    - **Heart Attack**: Chew aspirin if available
    - **Choking**: Perform abdominal thrusts
    - **Stroke**: Remember FAST (Face, Arms, Speech, Time)
    """, current_lang)
    
    st.markdown(f'<h2 class="subheader">{title}</h2>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown(f"### {contacts_title}")
        st.markdown(emergency_contacts)
        
        # Emergency call button
        st.markdown('<div class="danger-button">', unsafe_allow_html=True)
        if st.button(call_ambulance, use_container_width=True):
            st.markdown(f"[{calling_emergency}](tel:108)", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"### {dialpad_title}")
        
        # Initialize dialed number in session state
        if "dialed_number" not in st.session_state:
            st.session_state.dialed_number = ""
        
        # Display dialed number
        st.text_input(number_to_dial, value=st.session_state.dialed_number, key="display_number", disabled=True)
        
        # Create dial pad
        buttons = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '0', '#']
        
        # Create a 3x4 grid for the dial pad
        for i in range(0, 12, 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(buttons):
                    digit = buttons[i + j]
                    if cols[j].button(digit, key=f"btn_{digit}"):
                        st.session_state.dialed_number += digit
        
        # Control buttons
        col_call, col_clear = st.columns(2)
        with col_call:
            if st.button(call_button, use_container_width=True):
                if st.session_state.dialed_number:
                    st.markdown(f"[{calling_text} {st.session_state.dialed_number}](tel:{st.session_state.dialed_number})", unsafe_allow_html=True)
        
        with col_clear:
            if st.button(clear_button, use_container_width=True):
                st.session_state.dialed_number = ""
                st.rerun()
    
    with col3:
        st.markdown(f"### {firstaid_title}")
        st.markdown(firstaid_tips)
    
    st.markdown('</div>', unsafe_allow_html=True)

def appointment_booking():
    """Doctor Appointment Booking Interface"""
    current_lang = st.session_state.user_language
    
    # Translate the page content
    title = translate_text("🗓️ Book Appointment", current_lang)
    view_appointments_title = translate_text("My Appointments", current_lang)
    book_appointment_title = translate_text("Book New Appointment", current_lang)
    select_doctor = translate_text("Select Doctor", current_lang)
    select_date = translate_text("Select Date", current_lang)
    select_time = translate_text("Select Time", current_lang)
    reason_label = translate_text("Reason for Visit", current_lang)
    book_button = translate_text("📅 Book Appointment", current_lang)
    cancel_button = translate_text("❌ Cancel Appointment", current_lang)
    no_appointments = translate_text("You have no scheduled appointments.", current_lang)
    appointment_booked = translate_text("✅ Appointment booked successfully!", current_lang)
    appointment_canceled = translate_text("Appointment cancelled successfully.", current_lang)
    specialty_label = translate_text("Speciality", current_lang)
    languages_spoken = translate_text("Languages Spoken", current_lang)
    availability = translate_text("Availability", current_lang)
    
    st.markdown(f'<h2 class="subheader">{title}</h2>', unsafe_allow_html=True)
    
    # Create tabs for viewing and booking appointments
    tab1, tab2 = st.tabs([view_appointments_title, book_appointment_title])
    
    # Tab 1: View Appointments
    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        # Get user's appointments
        user_appointments = get_user_appointments(st.session_state.user)
        doctors = load_doctors()
        
        if not user_appointments:
            st.info(no_appointments)
        else:
            # Sort appointments by date
            user_appointments.sort(key=lambda x: (x["date"], x["time"]))
            
            # Display appointments
            for appointment in user_appointments:
                if appointment["status"] != "Cancelled":  # Only show active appointments
                    doctor_id = appointment["doctor_id"]
                    doctor_info = doctors.get(doctor_id, {"name": "Unknown Doctor"})
                    
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.markdown(f"### {translate_text(doctor_info['name'], current_lang)}")
                        st.markdown(f"**{translate_text('Date', current_lang)}:** {appointment['date']}")
                        st.markdown(f"**{translate_text('Time', current_lang)}:** {appointment['time']}")
                        if "specialty" in doctor_info:
                            st.markdown(f"**{specialty_label}:** {translate_text(doctor_info['specialty'], current_lang)}")
                    
                    with col2:
                        st.markdown(f"**{translate_text('Reason', current_lang)}:** {appointment['reason']}")
                        st.markdown(f"**{translate_text('Status', current_lang)}:** {translate_text(appointment['status'], current_lang)}")
                    
                    with col3:
                        # Cancel appointment button
                        if st.button(cancel_button, key=f"cancel_{appointment['id']}", use_container_width=True):
                            if cancel_appointment(st.session_state.user, appointment['id']):
                                st.success(appointment_canceled)
                                st.rerun()
                    
                    st.markdown("---")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 2: Book Appointment
    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        doctors = load_doctors()
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Doctor selection
            doctor_names = {doctor_id: translate_text(info["name"], current_lang) for doctor_id, info in doctors.items()}
            selected_doctor_name = st.selectbox(select_doctor, list(doctor_names.values()))
            
            # Map back to doctor ID
            selected_doctor_id = [did for did, name in doctor_names.items() if name == selected_doctor_name][0]
            selected_doctor = doctors[selected_doctor_id]
            
            # Appointment date and time
            today = datetime.now().date()
            min_date = today + timedelta(days=1)  # Start from tomorrow
            max_date = today + timedelta(days=30)  # Allow booking up to 30 days ahead
            
            # Get available dates based on doctor's availability
            day_map = {
                0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 
                4: "Friday", 5: "Saturday", 6: "Sunday"
            }
            available_dates = []
            for i in range(1, 31):
                check_date = today + timedelta(days=i)
                day_name = day_map[check_date.weekday()]
                if day_name in selected_doctor["availability"]:
                    available_dates.append(check_date)
            
            selected_date = st.date_input(select_date, min_value=min_date, max_value=max_date, value=available_dates[0] if available_dates else min_date)
            
            # Convert selected date to string format
            formatted_date = selected_date.strftime("%Y-%m-%d")
            
            # Time selection
            time_slots = ["09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", 
                          "02:00 PM", "03:00 PM", "04:00 PM", "05:00 PM"]
            selected_time = st.selectbox(select_time, time_slots)
            
            # Reason for visit
            visit_reason = st.text_area(reason_label, placeholder=translate_text("Please describe your symptoms or reason for the appointment", current_lang))
        
        with col2:
            # Display doctor information
            if "image" in selected_doctor:
                st.image(selected_doctor["image"], width=150)
            
            st.markdown(f"### {translate_text(selected_doctor['name'], current_lang)}")
            
            if "specialty" in selected_doctor:
                st.markdown(f"**{specialty_label}:** {translate_text(selected_doctor['specialty'], current_lang)}")
            
            if "languages" in selected_doctor:
                languages_list = [translate_text(lang, current_lang) for lang in selected_doctor["languages"]]
                st.markdown(f"**{languages_spoken}:** {', '.join(languages_list)}")
            
            if "availability" in selected_doctor:
                availability_list = [translate_text(day, current_lang) for day in selected_doctor["availability"]]
                st.markdown(f"**{availability}:** {', '.join(availability_list)}")
            
            if "bio" in selected_doctor:
                st.markdown(f"**{translate_text('Bio', current_lang)}:** {translate_text(selected_doctor['bio'], current_lang)}")
        
        # Book appointment button
        book_clicked = st.button(book_button, use_container_width=True)
        
        if book_clicked:
            if not visit_reason:
                st.warning(translate_text("Please provide a reason for your visit.", current_lang))
            else:
                # Save the appointment
                save_appointment(st.session_state.user, selected_doctor_id, formatted_date, selected_time, visit_reason)
                st.success(appointment_booked)
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

def doctor_chat():
    """Doctor Chat Messaging Interface"""
    current_lang = st.session_state.user_language
    
    # Translate the page content
    title = translate_text("💬 Chat with Doctor", current_lang)
    select_doctor = translate_text("Select Doctor to Chat With", current_lang)
    message_placeholder = translate_text("Type your message here...", current_lang)
    send_button = translate_text("Send Message", current_lang)
    no_messages = translate_text("No messages yet. Start the conversation by sending a message.", current_lang)
    
    st.markdown(f'<h2 class="subheader">{title}</h2>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    # Load doctors
    doctors = load_doctors()
    
    # Doctor selection
    doctor_names = {doctor_id: info["name"] for doctor_id, info in doctors.items()}
    selected_doctor_name = st.selectbox(select_doctor, list(doctor_names.values()))
    
    # Map back to doctor ID
    selected_doctor_id = [did for did, name in doctor_names.items() if name == selected_doctor_name][0]
    selected_doctor = doctors[selected_doctor_id]
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Display chat history container
        st.markdown("### Chat History")
        chat_container = st.container(height=400)
        
        # Message input
        message_input = st.text_area(translate_text("Message", current_lang), placeholder=message_placeholder, key="message_input")
        
        # Send button
        if st.button(send_button, use_container_width=True):
            if message_input:
                # Save user message
                save_doctor_chat_message(st.session_state.user, selected_doctor_id, message_input)
                
                # Generate simple AI response for demo purposes
                responses = [
                    "Thank you for your message. I'll review it and get back to you soon.",
                    "I've received your message. Let me check your medical history and respond shortly.",
                    "Thank you for reaching out. Based on what you've described, I recommend scheduling an appointment.",
                    "I understand your concern. Can you provide more details about when these symptoms started?",
                    "Thanks for your message. This might require further examination, please consider booking an appointment."
                ]
                import random
                ai_response = random.choice(responses)
                
                # Save doctor's response with a slight delay to simulate real conversation
                save_doctor_chat_message(st.session_state.user, selected_doctor_id, ai_response, is_from_user=False)
                
                # Clear input
                st.session_state.message_input = ""
                st.rerun()
    
    with col2:
        # Display doctor information
        if "image" in selected_doctor:
            st.image(selected_doctor["image"], width=150)
        
        st.markdown(f"### {translate_text(selected_doctor['name'], current_lang)}")
        
        if "specialty" in selected_doctor:
            st.markdown(f"**{translate_text('Specialty', current_lang)}:** {translate_text(selected_doctor['specialty'], current_lang)}")
        
        # Add quick actions
        st.markdown("### Quick Actions")
        if st.button(translate_text("Book Appointment", current_lang), key="book_from_chat"):
            st.session_state.selected_page = "🗓️ Book Appointment"
            st.rerun()
        
        if st.button(translate_text("Start Video Call", current_lang), key="video_from_chat"):
            call_link = f"https://meet.jit.si/healthroom_{st.session_state.user}_{selected_doctor_id}"
            st.markdown(f"[{translate_text('Join Video Call', current_lang)}]({call_link})", unsafe_allow_html=True)
    
    # Display chat history in the container
    with chat_container:
        chat_history = get_user_doctor_chats(st.session_state.user, selected_doctor_id)
        
        if not chat_history:
            st.info(no_messages)
        else:
            for message in chat_history:
                message_text = message["message"]
                timestamp = message["timestamp"]
                
                # Apply translation if needed
                if current_lang != "en":
                    message_text = translate_text(message_text, current_lang)
                
                # Format based on message sender
                if message["from_user"]:
                    st.markdown(f'<div class="chat-message chat-outgoing">{message_text}<div class="chat-time">{timestamp}</div></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-message chat-incoming">{message_text}<div class="chat-time">{timestamp}</div></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


# --- Main Application ---
def main():
    """Main application controller"""
    # Initialize session state
    if "user" not in st.session_state:
        st.session_state.user = None
    
    if "user_language" not in st.session_state:
        st.session_state.user_language = "en"
    
    if "selected_page" not in st.session_state:
        st.session_state.selected_page = "💬 Health Chatbot"
    
    # Sidebar navigation when logged in
    if st.session_state.user:
        current_lang = st.session_state.user_language
        
        with st.sidebar:
            st.markdown(f"## 👤 {translate_text('Welcome', current_lang)}, {st.session_state.user}")
            st.markdown("---")
            
            # Language selector in sidebar
            st.markdown(f"### 🌐 {translate_text('Language', current_lang)}")
            selected_lang_label = st.selectbox(
                translate_text("Select Language", current_lang),
                list(LANGUAGES.values()),
                index=list(LANGUAGES.keys()).index(current_lang),
                key="sidebar_language"
            )
            
            # Update language if changed
            new_lang_code = [k for k, v in LANGUAGES.items() if v == selected_lang_label][0]
            if new_lang_code != current_lang:
                update_user_language(st.session_state.user, new_lang_code)
                st.session_state.user_language = new_lang_code
                st.rerun()
            
            st.markdown("---")
            
            # Navigation menu with translated options
            nav_options = {
                "💬 Health Chatbot": translate_text("Health Chatbot", current_lang),
                "💊 Medications": translate_text("Medications", current_lang),
                "🗓️ Book Appointment": translate_text("Book Appointment", current_lang),
                "💬 Chat with Doctor": translate_text("Chat with Doctor", current_lang),
                "📞 Video Call": translate_text("Video Call", current_lang),
                "📄 Upload Documents": translate_text("Upload Documents", current_lang),
                "🚨 Emergency Services": translate_text("Emergency Services", current_lang)
            }
            
            # Create the radio buttons with translated labels but keep original keys
            translated_options = [f"{k.split()[0]} {v}" for k, v in nav_options.items()]
            selected_translated = st.radio(translate_text("Dashboard", current_lang), translated_options)
            
            # Map back to original key
            for orig_key, translated_value in nav_options.items():
                if selected_translated.endswith(translated_value):
                    st.session_state.selected_page = orig_key
                    break
            
            st.markdown("---")
            logout_text = translate_text("Logout", current_lang)
            st.markdown('<div class="danger-button">', unsafe_allow_html=True)
            if st.button(f"🔒 {logout_text}", use_container_width=True):
                del st.session_state.user
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
            # App info
            st.markdown("---")
            app_info = translate_text("""
            **Health AI Dashboard**  
            Version 2.0  
            © 2025 Health AI Inc.
            """, current_lang)
            st.markdown(app_info)
        
        # Main content area
        header_text = translate_text("Health AI Dashboard", current_lang)
        st.markdown(f'<h1 class="main-header">🌡️ {header_text}</h1>', unsafe_allow_html=True)
        
        # Display selected page content
        if st.session_state.selected_page == "💬 Health Chatbot":
            chatbot()
        elif st.session_state.selected_page == "💊 Medications":
            medication_guide()
        elif st.session_state.selected_page == "🗓️ Book Appointment":
            appointment_booking()
        elif st.session_state.selected_page == "💬 Chat with Doctor":
            doctor_chat()
        elif st.session_state.selected_page == "📞 Video Call":
            video_call()
        elif st.session_state.selected_page == "📄 Upload Documents":
            upload_documents()
        elif st.session_state.selected_page == "🚨 Emergency Services":
            emergency_call()
    
    # Authentication pages when not logged in
    else:
        st.markdown('<h1 class="main-header">🌡️ Health AI Dashboard</h1>', unsafe_allow_html=True)
        
        # App introduction
        st.markdown("""
        Welcome to the Health AI Dashboard - your personal healthcare assistant. 
        Log in or create an account to access all features.
        """)
        
        # Login/signup tabs
        auth_choice = st.sidebar.radio("Authentication", ["Login", "Sign Up"])
        
        if auth_choice == "Login":
            login_page()
            
            # Link to sign up
            st.markdown("---")
            st.markdown("Don't have an account? Select 'Sign Up' from the sidebar.")
        else:
            signup_page()
            
            # Link to login
            st.markdown("---")
            st.markdown("Already have an account? Select 'Login' from the sidebar.")


if __name__ == "__main__":
    main()
