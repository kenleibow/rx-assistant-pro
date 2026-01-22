import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import requests
from fpdf import FPDF
import difflib

# ==========================================
# 🔐 REGISTRATION & LOGGING SECTION
# ==========================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Rx Assistant - Registration")
    st.write("Please provide your details to access the tool.")
    
    with st.form("login_form"):
        user_name = st.text_input("Full Name")
        user_email = st.text_input("Email Address")
        submit = st.form_submit_button("Enter App")

        if submit:
            if not user_name or not user_email:
                st.error("⚠️ Please fill in BOTH Name and Email.")
            else:
                try:
                    # --- DIRECT KEYS ---
                    # --- DIRECT KEYS ---
                    creds_dict = {
                        "type": "service_account",
                        "project_id": "rx-assistant-485114",
                        "private_key_id": "46df0a9935ebff7804b0bc7ffbc2c4bd9919b1fb",
                        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCTsoglvTxDMEfA\nZ3hRnQvB7Z08avEgjq3jl5C7Vm0I5LfnJxVMQFN65+EMPNSKDxq/aqErXYBE6pRF\noDAO7bvnq1jCUtIJ1hozwiU0ITcvBWs5ph3jFviXRNyJ/cOsUUOaIBk1N3oQbC0v\nZC2Pq3ThgVIAACz16J3iW4ng/KtBMm+rXelsPPDkgO6OrQroYihm8YJk4dCAC0JL\nMnJ2LJEj8SeNx51Z8U3kG1XqqN54Fuwp+nEYDcwkRLoUDRcU8p6vBMQl+HgikS4Q\nFGW8qmvesEZWQko6aTNfGXVCEyXHjYQSZEcJs5ETYzFQvLqftgFaZxdFDSJ15hoG\ntN2+W9MtAgMBAAECggEAG2zbCZDwM/Su2hwMdDEiagXufLXJ5PcBdIGkExk7AVwB\nBwfTlVdbePa+K+jOuX0RBSquVzBTPVjGpAAY9GiyC9ReFKVO0ZtDPcmm4V1qkw1h\nSfDd21lcWzBi+C+aCjEDycZ8j8xnms2PfV2PdT5L44TBHnVp49aoHIxNV6zrOt1z\nlhhO8SLOUGOecTDNnNhgZM7DcjVUsyLEEeNec+nXfvB7UfFI8S+ktK8d4C5QFpH7\nRMcJj6ibx9wj9t1RQNvQlxPvna69YnyaklBVbjyH1LWc3TVQye2agjw95yaIllhc\nrZnnQijG5L4/uwooThBb1BW4UpQXc6IO30ea+U/ZSQKBgQDOVec5te6k91U5+oWk\nPb+3JfPtRZpaW2UdTvGYzLpxBF9BiYC3gCznPvV6It+IpzRhZHW6Jb5C2goDSD2U\CX6tmWLRPbq9Vyr1+hCovY+ECgh22SKhSekFTJsMyq7CNSkjXy7H+IkwVmiu3TeG\nhTlyHKY7ccwHzxsoZ1cGLUz+aQKBgQC3P24SM5hEhykG2gr+xiaS3dTCxwuyyC2O\n5XNuT7EsljzubX1LtetCBMoVwEhu0LBaISG67HAaLi8VoRBBQRWX8azaLnAp36m+\n1SUXiryODUQp6HAxhnEI8NMb8VEHvocr/P+dLf7YwyOoY9cB+qI3pVjjGPy+tMrc\nDYkuxTzeJQKBgQC4GtYSHE8vSrD05p/QCHjDhk277FrpPJtgJ0xStnm01d3YsEP1\nd5yZSQfnTq59VBPcwrJ4wayeIcbFXvPy3vX1F+OgJ6AzyU8/4zxyE5G2ku0yflPz\n7erJG61NIJwGFUD7mrY3H3/pbXBCdohQsxaqxv1cFRGj9huZVXvEuy7z4QKBgQCA\n0xXVs/HzEzYTfAxIyhLqIwtlFzuxJytoDwTUYzACUWhqkgyIwk6ureFH41LInOut\noScuWvQAY8F0KjPcPB4rIJrNE+KEfZm+7+dQopcmIktuTts45fPnPi6bsU2u7RHo\nKcelv2UvDBiwU+gemw2ZoyNXHATrKPyIMPflKoI9BQKBgEsHamqyMa+/ZibbRm8I\nQmA8dOu1TEMfda8dJojuAfBVhF3b1MCBWzzIIdtyjHumcOJE5Op5ebhh4fexqH21\nz4qBL7hkEXsBPDXYMeWpJq6Nofpw5nKdoIu6gPFsZ056RzDNiUI7yi09lcz9LvBv\nl23eFaGsDK6MIMmUjYHUwp9H\n-----END PRIVATE KEY-----\n",
                        "client_email": "rx-logger@rx-assistant-485114.iam.gserviceaccount.com",
                        "client_id": "101979612558880555948",
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/rx-logger%40rx-assistant-485114.iam.gserviceaccount.com"
                    }

                    # --- CONNECT & WRITE (WITH UPDATED SCOPES) ---
                    # We added the Google Drive scope here to fix the 403 error
                    scopes = [
                        "https://www.googleapis.com/auth/spreadsheets",
                        "https://www.googleapis.com/auth/drive"
                    ]
                    
                    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
                    client = gspread.authorize(creds)
                    
                    sheet = client.open("Rx_Login_Tracker").sheet1
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    sheet.append_row([current_time, user_name, user_email])
                    
                    # --- UNLOCK ---
                    st.session_state.logged_in = True
                    st.success(f"Welcome, {user_name}!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"🚨 Connection Error: {e}")

    st.stop()
# --- CONFIGURATION ---
st.set_page_config(page_title="Rx Field Assistant", page_icon="🛡️", layout="wide")

# =========================================================
#  CALLBACKS (MUST BE AT THE TOP)
# =========================================================
# This function runs BEFORE the app redraws, preventing the "Widget Instantiated" error
def fix_spelling_callback():
    # Get the word we saved in the temp state
    if "suggestion" in st.session_state:
        st.session_state.single_input = st.session_state.suggestion

def clear_single(): st.session_state.single_input = ""
def clear_multi(): st.session_state.multi_input = ""

# --- CSS STYLING ---
st.markdown("""
    <style>
    .risk-high { background-color: #ffcccc; padding: 10px; border-radius: 5px; color: #8a0000; border-left: 5px solid #cc0000; }
    .risk-med { background-color: #fff4cc; padding: 10px; border-radius: 5px; color: #664d00; border-left: 5px solid #ffcc00; }
    .risk-safe { background-color: #e6fffa; padding: 10px; border-radius: 5px; color: #004d40; border-left: 5px solid #00bfa5; }
    
    div.stButton > button { width: 100%; }
    .footer-link { text-align: center; margin-top: 20px; font-size: 14px; color: #888; }
    .footer-link a { color: #0066cc; text-decoration: none; font-weight: bold; }

    /* --- FLOATING BMI LABEL --- */
    /* This forces a label to appear in the top left, regardless of sidebar state */
    .bmi-pointer {
        position: fixed;
        top: 60px;
        left: 20px;
        z-index: 9999;
        background-color: #0066cc;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 14px;
        pointer-events: none; /* Let clicks pass through */
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }
    
    /* Hide the pointer if sidebar is OPEN (to avoid clutter) */
    section[data-testid="stSidebar"][aria-expanded="true"] + .main .bmi-pointer {
        display: none;
    }
    </style>
    
    <div class="bmi-pointer">BMI Calculator</div>
    """, unsafe_allow_html=True)

# =========================================================
#  DATA: COMMON DRUG LIST (For Spell Check)
# =========================================================
COMMON_DRUGS_LIST = [
    "Metformin", "Lisinopril", "Atorvastatin", "Levothyroxine", "Amlodipine", 
    "Metoprolol", "Omeprazole", "Losartan", "Gabapentin", "Hydrochlorothiazide", 
    "Sertraline", "Simvastatin", "Montelukast", "Escitalopram", "Furosemide", 
    "Pantoprazole", "Trazodone", "Fluticasone", "Tramadol", "Duloxetine", 
    "Prednisone", "Tamsulosin", "Rosuvastatin", "Bupropion", "Meloxicam", 
    "Aspirin", "Clopidogrel", "Plavix", "Glipizide", "Benicar", "Januvia", 
    "Humira", "Enbrel", "Eliquis", "Xarelto", "Pradaxa", "Entresto", 
    "Farxiga", "Jardiance", "Ozempic", "Wegovy", "Mounjaro", "Trulicity", 
    "Synthroid", "Crestor", "Lipitor", "Nexium", "Advair", "Symbicort", 
    "Ventolin", "ProAir", "Spiriva", "Lyrica", "Cymbalta", "Effexor", 
    "Lexapro", "Zoloft", "Prozac", "Wellbutrin", "Abilify", "Seroquel", 
    "Xanax", "Klonopin", "Valium", "Ativan", "Ambien", "Lunesta", 
    "Viagra", "Cialis", "Levitra", "Allopurinol", "Colchicine", "Warfarin", 
    "Coumadin", "Digoxin", "Amiodarone", "Flecanide", "Sotalol", "Nitroglycerin",
    "Ranolazine", "Imdur", "Bisoprolol", "Carvedilol", "Labetalol"
]

# =========================================================
#  GLOBAL STATE: BMI CALCULATOR (SIDEBAR)
# =========================================================
with st.sidebar:
    st.header("⚖️ BMI Calculator")
    st.markdown("Quick check for height/weight knockouts.")
    
    feet = st.number_input("Height (Feet)", min_value=4, max_value=8, value=5)
    inches = st.number_input("Height (Inches)", min_value=0, max_value=11, value=9)
    # Default weight 140 (Normal BMI)
    weight = st.number_input("Weight (lbs)", min_value=80, max_value=500, value=140)
    
    # Calculate BMI
    total_inches = (feet * 12) + inches
    bmi = 0.0
    bmi_category = "Normal"
    
    if total_inches > 0:
        bmi = (weight / (total_inches ** 2)) * 703
        bmi = round(bmi, 1)
        
        # Color Code BMI for UI
        if bmi < 18.5:
            st.info(f"BMI: {bmi} (Underweight)")
            bmi_category = "Underweight"
        elif 18.5 <= bmi < 25:
            st.success(f"BMI: {bmi} (Normal)")
            bmi_category = "Normal"
        elif 25 <= bmi < 30:
            st.warning(f"BMI: {bmi} (Overweight)")
            bmi_category = "Overweight"
        elif 30 <= bmi < 35:
            st.error(f"BMI: {bmi} (Obese)")
            bmi_category = "Obese"
        elif 35 <= bmi < 40:
            st.error(f"BMI: {bmi} (Severe Obesity)")
            bmi_category = "Severe Obesity"
        else:
            st.error(f"BMI: {bmi} (Morbidly Obese)")
            bmi_category = "Morbidly Obese"
    
    st.markdown("---")
    st.caption("Rx Field Assistant v9.4")

st.title("🛡️ Life Insurance Rx Assistant")

# --- PDF GENERATOR FUNCTION (FIXED ENCODING) ---
def create_pdf(title, items_list, analysis_text, fda_text_content=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Helper to clean text for PDF (Removes incompatible characters)
    def clean(text):
        return text.encode('latin-1', 'replace').decode('latin-1')
    
    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=clean(f"Rx Assistant - {title}"), ln=True, align='C')
    pdf.ln(10)
    
    # Items (Drugs or Conditions)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Items Analyzed:", ln=True, align='L')
    pdf.set_font("Arial", size=12)
    for item in items_list:
        pdf.cell(200, 10, txt=clean(f"- {item}"), ln=True, align='L')
    pdf.ln(5)
    
    # Analysis Body
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Underwriting Analysis:", ln=True, align='L')
    pdf.set_font("Arial", size=12)
    
    # Handle analysis text (could be list or string)
    if isinstance(analysis_text, list):
        for line in analysis_text:
            pdf.multi_cell(0, 10, txt=clean(f"- {line}"))
    else:
        pdf.multi_cell(0, 10, txt=clean(analysis_text))
    
    pdf.ln(10)

    # Optional FDA Text
    if fda_text_content:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="Official FDA Indications (Excerpt):", ln=True, align='L')
        pdf.set_font("Arial", size=10) 
        pdf.multi_cell(0, 6, txt=clean(fda_text_content[:2000] + "...")) 
        
    return pdf.output(dest='S').encode('latin-1')

# =========================================================
#  LOGIC ENGINE 1: DRUGS (FDA)
# =========================================================
def analyze_single_med(indication_text, brand_name):
    text = indication_text.lower()
    name = brand_name.lower()
    
    # Specific Drug Rules
    if "metformin" in name:
        return {"risk": "Diabetes Type 2", "style": "risk-med", "questions": ["Is this for Pre-Diabetes or Type 2?", "What is your A1C?", "Any neuropathy?"], "rating": "Standard (if A1C < 7.0) to Table 2."}
    elif "lisinopril" in name or "amlodipine" in name:
        return {"risk": "Hypertension (High BP)", "style": "risk-safe", "questions": ["Is BP controlled?", "Last reading?", "Do you take >2 BP meds?"], "rating": "Preferred Best possible."}
    elif "plavix" in name or "clopidogrel" in name:
        return {"risk": "Heart Disease / Stroke", "style": "risk-high", "questions": ["History of TIA/Stroke?", "Stent placement?", "Preventative or active treatment?"], "rating": "Standard to Decline."}
    elif "abilify" in name or "aripiprazole" in name:
        return {"risk": "Bipolar / Depression / Schizophrenia", "style": "risk-high", "questions": ["Hospitalizations in last 5 years?", "Suicide attempts?", "Ability to work?"], "rating": "Complex. Mild = Standard. Bipolar = Table Rating."}
    elif "entresto" in name:
        return {"risk": "Heart Failure (CHF)", "style": "risk-high", "questions": ["What is your Ejection Fraction?", "Any hospitalizations recently?"], "rating": "Likely Decline or High Table Rating."}

    # Keyword Rules
    if "metastatic" in text: return {"risk": "FLAGGED: Cancer (Severe)", "style": "risk-high", "questions": ["Diagnosis date?", "Treatment status?"], "rating": "Likely Decline."}
    if "hiv" in text: return {"risk": "FLAGGED: HIV/AIDS", "style": "risk-high", "questions": ["Current Viral Load?", "CD4 Count?"], "rating": "Table Rating to Decline."}
    
    # Default
    return {"risk": "General / Maintenance", "style": "risk-safe", "questions": ["Why was this prescribed?", "Any symptoms?"], "rating": "Depends on condition."}

def check_med_combinations(found_categories):
    unique_cats = set(found_categories)
    insights = []
    if "Diabetes" in unique_cats and "Hypertension" in unique_cats and "Cholesterol" in unique_cats:
        insights.append("METABOLIC SYNDROME: Client has the 'Trifecta'. Look for carriers with Metabolic Syndrome credits.")
    elif "Diabetes" in unique_cats and "Cardiac" in unique_cats:
        insights.append("HIGH RISK (Diabetes + Heart): Compounded mortality risk. Expect Table 4+ or Decline.")
    return insights

def simple_category_check(text, name):
    t = text.lower(); n = name.lower()
    if "diabetes" in t or "metformin" in n: return "Diabetes"
    if "hypertension" in t or "lisinopril" in n: return "Hypertension"
    if "cholesterol" in t or "statin" in n: return "Cholesterol"
    if "heart failure" in t or "plavix" in n: return "Cardiac"
    return "Other"

# =========================================================
#  LOGIC ENGINE 2: IMPAIRMENTS
# =========================================================
IMPAIRMENT_DATA = {
    # --- CARDIOVASCULAR ---
    "Hypertension (High BP)": {"qs": ["Date of last reading?", "Is it controlled?", "Med change <12 mos?"], "rating": "Preferred (Controlled) to Table 2."},
    "Heart Attack (History of)": {"qs": ["Date of event?", "Current EF%?", "Recent stress test?"], "rating": "Postpone (0-6mos). Table 2 to 4 (After 1yr)."},
    "Atrial Fibrillation (AFib)": {"qs": ["Chronic or Paroxysmal?", "Blood thinners?", "Date last episode?"], "rating": "Standard (Infrequent) to Table 2."},
    "Stent Placement": {"qs": ["Date inserted?", "How many stents?", "Any chest pain since?"], "rating": "Table 2 (Single) to Table 4 (Multiple)."},
    "Coronary Artery Disease": {"qs": ["Date of diagnosis?", "Any bypass surgery?", "Current symptoms?"], "rating": "Table 2 to Decline."},
    "Stroke / TIA": {"qs": ["Date of event?", "Any residual weakness?", "Carotid ultrasound results?"], "rating": "Postpone (0-1yr). Table 4 to Decline."},
    "Pacemaker": {"qs": ["Date implanted?", "Underlying condition?", "Battery check date?"], "rating": "Standard (Sinus Node) to Table 2."},
    "Heart Murmur": {"qs": ["Functional or organic?", "Recent echocardiogram?", "Valve involvement?"], "rating": "Preferred (Functional) to Table 4."},
    "Aortic Stenosis": {"qs": ["Mild, Moderate or Severe?", "Valve replacement planned?", "Symptoms?"], "rating": "Mild=Std. Severe=Decline/Surgery."},
    "Peripheral Vascular Disease": {"qs": ["Do you have pain walking?", "Any surgery?", "Tobacco use?"], "rating": "Table 4 to Decline."},
    
    # --- ENDOCRINE ---
    "Diabetes Type 2": {"qs": ["Current A1C?", "Age of diagnosis?", "Insulin use?", "Neuropathy?"], "rating": "Standard (A1C<7) to Table 4 (Insulin)."},
    "Diabetes Type 1": {"qs": ["Age diagnosed?", "Insulin pump?", "Kidney issues?", "A1C average?"], "rating": "Table 4 to Table 8. Rarely Standard."},
    "Hypothyroidism": {"qs": ["Date diagnosed?", "TSH levels stable?", "Taking Synthroid?"], "rating": "Preferred Possible."},
    "Hyperthyroidism / Graves": {"qs": ["Date diagnosed?", "Treatment type (Radioactive iodine)?", "Current TSH?"], "rating": "Standard (Stable > 1yr)."},
    "Hashimoto's": {"qs": ["TSH levels?", "Any goiter or nodules?", "Medications?"], "rating": "Preferred to Standard."},
    
    # --- RESPIRATORY ---
    "Sleep Apnea": {"qs": ["CPAP use nightly?", "Compliance logs?", "Last sleep study?"], "rating": "Standard (Compliant). Table 2 to Decline (No CPAP)."},
    "COPD / Emphysema": {"qs": ["Oxygen use?", "Hospitalizations?", "Tobacco use?"], "rating": "Table 2 (Mild) to Decline (Severe/Smoker)."},
    "Asthma": {"qs": ["Inhaler frequency?", "Oral steroids (Prednisone)?", "Hospital visits?"], "rating": "Standard (Mild) to Table 3 (Severe)."},
    "Sarcoidosis": {"qs": ["Lungs only or systemic?", "Current steroid use?", "Date of last flare?"], "rating": "Standard (In remission) to Table 4."},
    
    # --- MENTAL HEALTH ---
    "Anxiety": {"qs": ["Medication count?", "Hospitalizations?", "Time off work?"], "rating": "Preferred (Mild) to Table 2 (Severe)."},
    "Depression": {"qs": ["Hospitalizations?", "Suicide attempts?", "Electro-shock therapy?"], "rating": "Standard (Mild) to Table 4/Decline (Severe)."},
    "Bipolar Disorder": {"qs": ["Type 1 or 2?", "Hospitalizations < 5 years?", "Stable on meds?"], "rating": "Table 2 minimum. Often Table 4+."},
    "ADHD / ADD": {"qs": ["Medication name?", "Any history of drug abuse?", "Stable employment?"], "rating": "Preferred to Standard."},
    "PTSD": {"qs": ["Source of trauma?", "Disability status?", "Substance abuse history?"], "rating": "Standard (Mild) to Decline."},
    
    # --- GASTROINTESTINAL ---
    "Crohn's Disease": {"qs": ["Date of last flare?", "Surgery history?", "Biologic meds (Humira)?"], "rating": "Standard (Remission > 2yr) to Table 4."},
    "Ulcerative Colitis": {"qs": ["Colonoscopy results?", "Steroid use?", "Surgery?"], "rating": "Standard (Mild) to Table 3."},
    "Hepatitis C": {"qs": ["Cured/Treated?", "Liver enzyme levels?", "Alcohol use?"], "rating": "Standard (Cured) to Decline (Untreated)."},
    "Fatty Liver": {"qs": ["Liver function tests?", "Alcohol history?", "BMI?"], "rating": "Standard (Mild) to Table 3."},
    "Gastric Bypass / Sleeve": {"qs": ["Date of surgery?", "Current weight stable?", "Complications?"], "rating": "Postpone (<6mos). Standard (After 1yr)."},
    "GERD / Reflux": {"qs": ["Medications?", "Barrett's Esophagus diagnosis?", "Endoscopy results?"], "rating": "Preferred to Standard."},
    
    # --- NEUROLOGICAL ---
    "Seizures / Epilepsy": {"qs": ["Date of last seizure?", "Type (Grand/Petit)?", "Driving restrictions?"], "rating": "Standard (>2yrs seizure free) to Table 4."},
    "Multiple Sclerosis (MS)": {"qs": ["Relapsing or Progressive?", "Can you walk unassisted?", "Date diagnosed?"], "rating": "Table 2 to Decline."},
    "Parkinson's": {"qs": ["Age onset?", "Progression speed?", "Daily living activities?"], "rating": "Table 4 to Decline."},
    
    # --- MUSCULOSKELETAL ---
    "Rheumatoid Arthritis": {"qs": ["Biologic meds?", "Deformity?", "Disability?"], "rating": "Standard to Table 3."},
    "Lupus (SLE)": {"qs": ["Organ involvement (Kidney)?", "Steroid use?", "Date diagnosed?"], "rating": "Table 2 to Decline."},
    "Fibromyalgia": {"qs": ["Disability status?", "Narcotic pain meds?", "Depression history?"], "rating": "Standard to Table 2."},
    "Gout": {"qs": ["Frequency of attacks?", "Kidney function?", "Alcohol use?"], "rating": "Standard."},
    
    # --- CANCER HISTORY ---
    "Breast Cancer History": {"qs": ["Date of last treatment?", "Stage/Grade?", "Lymph node involvement?"], "rating": "Flat Extra ($2-5/1000) or Standard > 5yrs."},
    "Prostate Cancer History": {"qs": ["Gleason score?", "Surgery or Radiation?", "Current PSA?"], "rating": "Standard (Low grade/Surgery) to Table 4."},
    "Melanoma History": {"qs": ["Clark Level / Breslow Depth?", "Date removed?", "Chemo?"], "rating": "Standard (In Situ) to Decline (Deep)."},
    "Colon Cancer History": {"qs": ["Stage?", "Date of surgery?", "Colonoscopy since?"], "rating": "Postpone (0-2yrs). Table 2 to Standard > 5yrs."},
    "Thyroid Cancer": {"qs": ["Type (Papillary)?", "Radioactive iodine?", "Date treatment ended?"], "rating": "Standard (after 1 year)."},
    "Lymphoma (Hodgkins)": {"qs": ["Stage?", "Date of last chemo?", "Recurrence?"], "rating": "Flat Extra or Table Rating (Requires 2-5yr wait)."},
    
    # --- RENAL / OTHER ---
    "Kidney Stones": {"qs": ["Single or multiple?", "Surgery required?", "Kidney function normal?"], "rating": "Preferred (Single) to Table 2."},
    "Chronic Kidney Disease": {"qs": ["What is the Stage (1-5)?", "GFR level?", "Diabetic?"], "rating": "Standard (Stage 1) to Decline (Stage 3+)."},
    "Barrett's Esophagus": {"qs": ["Biopsy results?", "Dysplasia?", "Follow up schedule?"], "rating": "Standard to Table 3."},
    "Alcohol History": {"qs": ["Date of last drink?", "AA attendance?", "DUI history?"], "rating": "Postpone (<2yrs sober). Standard (>5yrs sober)."}
}

def check_comorbidities(selected_conditions, is_smoker, current_bmi):
    warnings = []
    
    # 1. IMMEDIATE CHECKS (General Rules)
    if is_smoker:
        warnings.append("SMOKER STATUS: Rates will be Standard Smoker (Tobacco) at best.")
    
    if current_bmi > 30:
        warnings.append("BUILD RATING: High BMI typically triggers a Table Rating based on build alone.")

    # 2. SPECIFIC COMBINATION Rules
    if is_smoker:
        if "COPD / Emphysema" in selected_conditions or "Asthma" in selected_conditions:
            warnings.append("DECLINE WARNING: COPD/Asthma + Smoking is a major knockout for most carriers.")
        if "Heart Attack (History of)" in selected_conditions:
            warnings.append("HIGH RISK: Smoking after a Heart Attack is typically Table 4 to Decline.")
        if "Diabetes Type 2" in selected_conditions:
            warnings.append("RATE UP: Smoker + Diabetes often adds +2 Tables to the base rating.")

    if current_bmi > 35:
        if "Sleep Apnea" in selected_conditions:
            warnings.append("BUILD RISK: Sleep Apnea with BMI > 35 requires documented CPAP compliance for best rates.")
        if "Diabetes Type 2" in selected_conditions:
            warnings.append("METABOLIC: High BMI + Diabetes will likely trigger Metabolic Syndrome guidelines.")

    if "Diabetes Type 2" in selected_conditions and "Heart Attack (History of)" in selected_conditions:
        warnings.append("COMORBIDITY ALERT: Diabetes + Heart History is treated very strictly. Expect Table 4 minimum.")
        
    return warnings

# =========================================================
#  APP LAYOUT
# =========================================================
# UPDATED ORDER: Single Drug | Multi-Med | Impairment Analyst
tab1, tab2, tab3 = st.tabs(["🔍 Drug Decoder (FDA)", "💊 Multi-Med Combo Check", "🩺 Impairment Analyst (Conditions)"])

# --- TAB 1: Single Drug ---
with tab1:
    col_a, col_b = st.columns([4, 1])
    with col_a: st.markdown("### 🔍 Search by Medication Name")
    with col_b: st.button("🔄 Clear", on_click=clear_single)

    single_drug = st.text_input("Enter Drug Name:", placeholder="e.g., Metformin", key="single_input")
    
    if single_drug:
        with st.spinner("Accessing FDA Database..."):
            try:
                url = f'https://api.fda.gov/drug/label.json?search=openfda.brand_name:"{single_drug}"+openfda.generic_name:"{single_drug}"&limit=1'
                r = requests.get(url)
                if r.status_code == 200:
                    data = r.json()['results'][0]
                    brand = data['openfda'].get('brand_name', [single_drug])[0]
                    indications = data.get('indications_and_usage', ["No text found"])[0]
                    
                    insight = analyze_single_med(indications, single_drug)
                    
                    st.success(f"**Found:** {brand}")
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        st.markdown(f"<div class='{insight['style']}'><b>Risk:</b><br>{insight['risk']}</div>", unsafe_allow_html=True)
                        st.caption(f"Est. Rating: {insight['rating']}")
                    with c2:
                        st.markdown("**❓ Field Questions:**")
                        for q in insight['questions']: st.write(f"✅ *{q}*")
                    
                    with st.expander("Show FDA Official Text"): st.write(indications)

                    # PDF
                    report_text = [f"Risk: {insight['risk']}", f"Est. Rating: {insight['rating']}"] + [f"Ask: {q}" for q in insight['questions']]
                    pdf_data = create_pdf(f"Report - {brand}", [brand], report_text, fda_text_content=indications)
                    st.download_button("📄 Download PDF Report", data=pdf_data, file_name=f"{brand}_report.pdf", mime="application/pdf")
                else:
                    # --- SPELL CHECK LOGIC (NEW v9.4 - CALLBACK) ---
                    matches = difflib.get_close_matches(single_drug, COMMON_DRUGS_LIST, n=1, cutoff=0.6)
                    st.error(f"❌ '{single_drug}' not found in FDA Database.")
                    if matches:
                        suggested_word = matches[0]
                        st.info(f"💡 Did you mean: **{suggested_word}**?")
                        
                        # SAVE TO TEMP STATE for callback to read
                        st.session_state.suggestion = suggested_word
                        # CALLBACK on button press
                        st.button(f"Yes, search for {suggested_word}", on_click=fix_spelling_callback)
                        
                    else:
                        st.warning("Double check spelling. Brand names are required for FDA search.")
            except Exception as e:
                # REVEAL REAL ERROR if connection fails
                st.error(f"Connection/Data Error: {e}")

# --- TAB 2: MULTI-MED ---
with tab2:
    col_x, col_y = st.columns([4, 1])
    with col_x: st.markdown("### 💊 Multi-Medication Combo Check")
    with col_y: st.button("🔄 Clear List", on_click=clear_multi)
    
    multi_input = st.text_area("Paste Med List (comma separated):", key="multi_input", placeholder="Metformin, Lisinopril, Plavix")
    
    if st.button("Analyze Combinations"):
        if multi_input:
            meds = [m.strip() for m in multi_input.split(',')]
            cats = []
            valid_meds = []
            
            for med in meds:
                if len(med) < 3: continue
                try:
                    url = f'https://api.fda.gov/drug/label.json?search=openfda.brand_name:"{med}"+openfda.generic_name:"{med}"&limit=1'
                    r = requests.get(url)
                    if r.status_code == 200:
                        ind = r.json()['results'][0].get('indications_and_usage', [""])[0]
                        cat = simple_category_check(ind, med)
                        cats.append(cat)
                        valid_meds.append(med)
                        st.write(f"✅ **{med}** identified as *{cat}*")
                    else:
                        st.write(f"❌ **{med}** not found")
                except: pass
            
            combos = check_med_combinations(cats)
            if combos:
                st.divider()
                for c in combos: st.error(c)
            else:
                st.success("No major negative combinations detected.")
                
            # PDF for Multi
            if valid_meds:
                combo_text = combos if combos else ["No high-risk combinations found."]
                pdf_bytes = create_pdf("Multi-Med Analysis", valid_meds, combo_text)
                st.download_button("📄 Download Combo Report", data=pdf_bytes, file_name="combo_report.pdf", mime="application/pdf")

# --- TAB 3: IMPAIRMENT ANALYST (Expanded) ---
with tab3:
    st.markdown("### 🩺 Condition & Impairment Search")
    st.info("Select known conditions to generate reflexive questions and check for co-morbidities.")
    
    # Inputs
    col_i1, col_i2 = st.columns(2)
    with col_i1:
        # SORT THE LIST ALPHABETICALLY FOR EASIER FINDING
        sorted_conditions = sorted(list(IMPAIRMENT_DATA.keys()))
        conditions = st.multiselect("Select Conditions (Scroll or Type to Search):", sorted_conditions)
    with col_i2:
        st.write("Risk Factors:")
        is_smoker = st.checkbox("🚬 Tobacco / Nicotine User")
        st.write(f"⚖️ Current BMI: **{bmi}** ({bmi_category})")

    # LOGIC UPDATE: Triggers even if only Risk Factors are present
    if conditions or is_smoker or bmi > 30:
        st.divider()
        st.subheader("📝 Underwriting Analysis")
        
        # 1. Co-morbidity Check
        warnings = check_comorbidities(conditions, is_smoker, bmi)
        if warnings:
            for w in warnings:
                st.error(w)
        elif not conditions:
             # Just smoker or BMI checked, but no disease
             st.warning("Note: No specific medical condition selected yet.")
        else:
            st.success("✅ No major negative co-morbidity factors (Smoker/BMI/Combo) detected.")

        # 2. Condition Breakdown
        pdf_lines = []
        if warnings:
            # FIXED LINE: LIST ADDITION INSTEAD OF APPEND
            pdf_lines = ["--- WARNINGS ---"] + warnings + ["--- DETAILS ---"]
        
        if conditions:
            for cond in conditions:
                data = IMPAIRMENT_DATA[cond]
                with st.container():
                    st.markdown(f"**{cond}**")
                    st.caption(f"Base Rating: {data['rating']}")
                    for q in data['qs']:
                        st.write(f"🔹 *{q}*")
                    
                    # Add to PDF content
                    pdf_lines.append(f"Condition: {cond}")
                    pdf_lines.append(f"Rating Guide: {data['rating']}")
                    pdf_lines.append("Questions to Ask:")
                    for q in data['qs']: pdf_lines.append(f" - {q}")
                    pdf_lines.append("---")
            
            st.markdown("---")
            # PDF Button for Impairments
            imp_pdf = create_pdf("Impairment Analysis", conditions, pdf_lines)
            st.download_button("📄 Download Impairment Report", data=imp_pdf, file_name="condition_report.pdf", mime="application/pdf")

# --- FOOTER ---
st.markdown("---")

with st.expander("⚠️ Legal Disclaimer & Liability Information"):
    st.markdown("""
    **1. Educational Use Only:** This tool is designed solely for informational and educational purposes to assist insurance professionals. It is not a medical device and should not be used for medical diagnosis.
    
    **2. No Binding Offer:** The risk class estimates (e.g., "Standard", "Table 2") are generalized approximations based on industry averages. They do not constitute a binding offer, quote, or guarantee of coverage from any specific insurance carrier.
    
    **3. Carrier Specifics:** Every insurance carrier has unique underwriting guidelines, knock-out questions, and credit programs. Users must always consult the official underwriting manuals and guides of the specific carrier they are writing business with.
    
    **4. Liability Waiver:** InsurTech Express and the creators of this tool accept no liability for errors, omissions, inaccuracies, or financial losses resulting from the use of this software. The user assumes all responsibility for verifying information with the appropriate carrier.
    """)

# Powered By Link (Moved BELOW Disclaimer)
st.markdown("""
<div class='footer-link'>
    Powered by <a href='https://www.insurtechexpress.com' target='_blank'>InsurTech Express</a>
</div>
""", unsafe_allow_html=True)
