import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import requests
from fpdf import FPDF
import difflib
import os
import json

# THIS MUST BE THE FIRST STREAMLIT LINE
st.set_page_config(page_title="Rx Field Assistant Pro", page_icon="🛡️", layout="wide")

# ==========================================
# 🔐 SECRETS & CLOUD HANDSHAKE
# ==========================================

def get_gspread_client():
    import os
    import json
    import gspread
    from google.oauth2.service_account import Credentials

    # 1. Try to build the key from the big Railway JSON variable
    try:
        gcp_json = os.environ.get("GCP_SERVICE_ACCOUNT")
        if gcp_json:
            creds_dict = json.loads(gcp_json)
            # Fix the private key formatting just in case
            if "private_key" in creds_dict:
                creds_dict["private_key"] = creds_dict["private_key"].replace('\\n', '\n')
            
            scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            return gspread.authorize(creds)
    except Exception as e:
        print(f"Railway connection failed: {e}")

    # 2. Safety Fallback for local testing/Streamlit Cloud
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "gcp_service_account" in st.secrets:
            creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
            return gspread.authorize(creds)
    except:
        pass

    return None

# Load the credentials
google_secrets = get_gspread_client()
# ==========================================
# 🔐 REGISTRATION & LOGGING SECTION
# ==========================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Rx Assistant - Registration")
    st.write("Please provide your details to access the tool.")
    
    with st.form("login_form"):
        user_name = st.text_input("Name")
        user_email = st.text_input("Email")
        submit = st.form_submit_button("Access Rx Assistant Pro")

        if submit:
            if not user_name or not user_email:
                st.error("⚠️ Please fill in BOTH Name and Email.")
            else:
                try:
                    p_key = os.environ.get("PRIVATE_KEY") or os.environ.get("private_key")
                    c_email = os.environ.get("CLIENT_EMAIL") or os.environ.get("client_email")
                    p_id = os.environ.get("PROJECT_ID") or os.environ.get("project_id")
                    s_id = os.environ.get("sheet_id") or os.environ.get("SHEET_ID")

                    creds_dict = {
                        "type": "service_account",
                        "project_id": p_id,
                        "private_key": p_key.replace('\\n', '\n'),
                        "client_email": c_email,
                        "token_uri": "https://oauth2.googleapis.com/token",
                    }
                    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
                    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
                    client = gspread.authorize(creds)
                    sheet = client.open_by_key(s_id).sheet1
                    
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    sheet.append_row([current_time, user_name, user_email])

                    st.session_state.logged_in = True
                    st.success("✅ Success! Entering app...")
                    st.rerun()
                except Exception as e:
                    st.error(f"🚨 Connection Error: {e}")
    
    # This stops the code here ONLY IF the user isn't logged in yet
    st.stop()

# ==========================================
# 🔍 MAIN APP STARTS BELOW THIS LINE
# ==========================================
# (Your drug search and decoder code goes here)
# --- CONFIGURATION (Reached only if logged in) ---

# =========================================================
#  CALLBACKS (MUST BE AT THE TOP)
# =========================================================
def fix_spelling_callback():
    if "suggestion" in st.session_state:
        st.session_state.single_input = st.session_state.suggestion

def clear_single(): st.session_state.single_input = ""
def clear_multi(): st.session_state.multi_input = ""

# --- CSS STYLING ---
# --- CSS STYLING (Banner-Aligned & Mobile-Fluid) ---
css_style = """<style>
/* 1. 📱 GLOBAL MOBILE FIX: Forces elastic scrolling */
html, body, [data-testid="stAppViewContainer"] {
    overflow: auto !important;
    -webkit-overflow-scrolling: touch !important;
}

/* 2. 📱 MOBILE & IPAD SPECIFIC (Fixes the scrolling 'lock') */
@media (max-width: 1024px) {
    .main .block-container {
        padding-bottom: 20rem !important; 
        overflow: visible !important;
        touch-action: pan-y !important;
    }
    
    [data-testid="stSidebar"] {
        position: absolute !important;
        height: auto !important;
    }

    .bmi-pointer { 
        display: block !important;
        position: fixed !important;
        top: 10px !important; 
        left: 10px !important;
        font-size: 11px !important; 
        padding: 4px 8px !important;
        background-color: #0066cc;
        color: white;
        z-index: 999999 !important;
        border-radius: 4px;
        pointer-events: none !important; 
    }
    
    .stButton>button {
        height: 3.5em !important;
    }
}

/* 3. 💻 LAPTOP SPECIFIC: Tightened UI */
@media (min-width: 1025px) {
    .main .block-container {
        padding-bottom: 3rem !important;
    }
    .bmi-pointer { 
        position: fixed; top: 60px; left: 20px; z-index: 99999; 
        background-color: #0066cc; color: white; padding: 5px 10px; 
        border-radius: 5px; font-weight: bold; font-size: 14px; 
        pointer-events: none; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); 
    }
}

/* 4. 📝 RATING TEXT & MATRIX TWEAKS */
.rating-text { 
    font-size: 0.95rem !important; 
    font-weight: 600 !important; 
    color: #E65100 !important; 
    display: block; 
    margin-top: 2px; 
}
.stTable { font-size: 12px !important; }
</style>"""

/* 4. DESIGN TWEAKS FOR MATRIX */
.stTable {
    font-size: 12px !important;
}
</style>"""
/* 2. RISK & RATING STYLES */
.risk-high { background-color: #ffcccc; padding: 10px; border-radius: 5px; color: #8a0000; border-left: 5px solid #cc0000; }
.risk-med { background-color: #fff4cc; padding: 10px; border-radius: 5px; color: #664d00; border-left: 5px solid #ffcc00; }
.risk-safe { background-color: #e6fffa; padding: 10px; border-radius: 5px; color: #004d40; border-left: 5px solid #00bfa5; }
.rating-text { font-size: 0.95rem !important; font-weight: 600 !important; color: #E65100 !important; display: block; margin-top: 2px; }

/* 3. TABLE & BUTTONS */
div[data-testid="stTable"] {
    overflow-x: auto !important;
    overflow-y: hidden !important;
    touch-action: pan-x !important;
}
div.stButton > button { width: 100%; }
.footer-link { text-align: center; margin-top: 40px; font-size: 14px; color: #888; }
</style>
<div class="bmi-pointer">BMI Indicator</div>"""

st.markdown(css_style, unsafe_allow_html=True)

# =========================================================
#  DATA: COMMON DRUG LIST
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
    st.header("⚖️ BMI & Build Assistant™")
    feet = st.number_input("Height (Feet)", 4, 8, 5)
    inches = st.number_input("Height (Inches)", 0, 11, 9)
    weight = st.number_input("Weight (lbs)", 80, 500, 165)
    
    total_inches = (feet * 12) + inches
    bmi = 0.0
    bmi_category = "Normal"
    
    if total_inches > 0:
        bmi = round((weight / (total_inches ** 2)) * 703, 1)
        
        # --- CARRIER-ALIGNED THRESHOLDS (Based on Banner/Prudential Tables) ---
        if bmi < 18.5: 
            st.info(f"BMI: {bmi} (Underweight)")
            bmi_category = "Underweight"
            
        elif bmi < 30.0: # Preferred / Preferred Plus range
            st.success(f"BMI: {bmi} (Preferred Outlook)")
            bmi_category = "Normal"
            
        elif bmi < 33.0: # Standard Plus / Standard range
            st.warning(f"BMI: {bmi} (Standard Outlook)")
            bmi_category = "Overweight"
            
        elif bmi < 40.0: # Substandard / Table Rated
            st.error(f"BMI: {bmi} (Obese / Rated)")
            bmi_category = "Obese"
        else:
            st.error(f"BMI: {bmi} (Decline Risk)")
            bmi_category = "Obese"

    st.markdown("---")
    st.caption("Rx Assistant Pro™ v9.5")
    st.caption("Carrier-Agnostic Field Guide")

st.title("🛡️ Life Insurance Rx Assistant Pro")

# --- PDF GENERATOR FUNCTION (REPLACEMENT) ---
def create_pdf(title, items_list, analysis_text, risk_level=None, fda_text_content=None):
    pdf = FPDF()
    pdf.add_page()
    
    # This helper function strips emojis/non-latin characters that crash PDFs
    def clean_text(text):
        if not text: return ""
        # Remove the specific emojis used in your matrix
        safe_text = str(text).replace("💎", "").replace("✅", "").replace("⚠️", "").replace("❌", "")
        # Remove any other non-standard characters
        return safe_text.encode('ascii', 'ignore').decode('ascii')

    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=clean_text(f"Rx Assistant - {title}"), ln=True, align='C')
    pdf.ln(10)

    # Items Analyzed Section
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Items Analyzed:", ln=True)
    pdf.set_font("Arial", size=11)
    for item in items_list:
        pdf.cell(200, 8, txt=clean_text(f"- {item}"), ln=True)
    pdf.ln(5)

    # Underwriting Analysis Section
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Underwriting Analysis:", ln=True)
    pdf.set_font("Arial", size=11)
    if isinstance(analysis_text, list):
        for line in analysis_text:
            pdf.multi_cell(0, 8, txt=clean_text(line))
    else:
        pdf.multi_cell(0, 8, txt=clean_text(analysis_text))

    # --- PURE TEXT PRODUCT OUTLOOK (STABLE VERSION) ---
    if risk_level:
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(230, 81, 0) # Professional Orange
        pdf.cell(200, 10, txt="PRODUCT SUITABILITY OUTLOOK:", ln=True)
        pdf.set_text_color(0, 0, 0) # Reset to Black
        
        pdf.set_font("Arial", size=10)
        # Pull the data from your matrix function
        matrix_data = get_product_matrix(risk_level)
        for row in matrix_data:
            # Format: PRODUCT: OUTLOOK -- NOTE
            cat = clean_text(row['Category']).upper()
            out = clean_text(row['Outlook']).strip()
            note = clean_text(row['Note'])
            pdf.multi_cell(0, 7, txt=f"{cat}: {out} -- {note}")
            pdf.ln(1)

    # FDA Text (Optional)
    if fda_text_content:
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="Official FDA Indications (Excerpt):", ln=True)
        pdf.set_font("Arial", size=9)
        pdf.multi_cell(0, 5, txt=clean_text(fda_text_content[:1500] + "..."))

    return pdf.output(dest='S').encode('latin-1')

# =========================================================
#  LOGIC ENGINES
# =========================================================
def analyze_single_med(indication_text, brand_name):
    text = indication_text.lower(); name = brand_name.lower()
    if "metformin" in name: return {"risk": "Diabetes Type 2", "style": "risk-med", "questions": ["Is this for Pre-Diabetes or Type 2?", "What is your A1C?", "Any neuropathy?"], "rating": "Standard (if A1C < 7.0) to Table 2."}
    elif "lisinopril" in name or "amlodipine" in name: return {"risk": "Hypertension (High BP)", "style": "risk-safe", "questions": ["Is BP controlled?", "Last reading?", "Do you take >2 BP meds?"], "rating": "Preferred Best possible."}
    elif "plavix" in name or "clopidogrel" in name: return {"risk": "Heart Disease / Stroke", "style": "risk-high", "questions": ["History of TIA/Stroke?", "Stent placement?"], "rating": "Standard to Decline."}
    elif "abilify" in name or "aripiprazole" in name: return {"risk": "Bipolar / Depression / Schizophrenia", "style": "risk-high", "questions": ["Hospitalizations in last 5 years?", "Suicide attempts?"], "rating": "Complex. Bipolar = Table Rating."}
    elif "entresto" in name: return {"risk": "Heart Failure (CHF)", "style": "risk-high", "questions": ["What is your Ejection Fraction?", "Any hospitalizations recently?"], "rating": "Likely Decline."}
    if "metastatic" in text: return {"risk": "FLAGGED: Cancer (Severe)", "style": "risk-high", "questions": ["Diagnosis date?", "Treatment status?"], "rating": "Likely Decline."}
    if "hiv" in text: return {"risk": "FLAGGED: HIV/AIDS", "style": "risk-high", "questions": ["Current Viral Load?", "CD4 Count?"], "rating": "Table Rating to Decline."}
    return {"risk": "General / Maintenance", "style": "risk-safe", "questions": ["Why was this prescribed?", "Any symptoms?"], "rating": "Depends on condition."}

def check_med_combinations(found_categories):
    unique_cats = set(found_categories)
    insights = []
    if "Diabetes" in unique_cats and "Hypertension" in unique_cats and "Cholesterol" in unique_cats: insights.append("METABOLIC SYNDROME: Client has the 'Trifecta'. Look for carriers with Metabolic Syndrome credits.")
    elif "Diabetes" in unique_cats and "Cardiac" in unique_cats: insights.append("HIGH RISK (Diabetes + Heart): Compounded mortality risk. Expect Table 4+ or Decline.")
    return insights

def simple_category_check(text, name):
    t = text.lower(); n = name.lower()
    if "diabetes" in t or "metformin" in n: return "Diabetes"
    if "hypertension" in t or "lisinopril" in n: return "Hypertension"
    if "cholesterol" in t or "statin" in n: return "Cholesterol"
    if "heart failure" in t or "plavix" in n: return "Cardiac"
    return "Other"

# =========================================================
#  IMPAIRMENT DATA (Tagged for Universal Logic)
# =========================================================
IMPAIRMENT_DATA = {
    "Hypertension (High BP)": {"qs": ["Date of last reading?", "Is it controlled?", "Med change <12 mos?"], "rating": "Preferred (Controlled) to Table 2.", "risk": "risk-safe"},
    "Heart Attack (History of)": {"qs": ["Date of event?", "Current EF%?", "Recent stress test?"], "rating": "Postpone (0-6mos). Table 2 to 4 (After 1yr).", "risk": "risk-high"},
    "Atrial Fibrillation (AFib)": {"qs": ["Chronic or Paroxysmal?", "Blood thinners?", "Date last episode?"], "rating": "Standard (Infrequent) to Table 2.", "risk": "risk-med"},
    "Stent Placement": {"qs": ["Date inserted?", "How many stents?", "Any chest pain since?"], "rating": "Table 2 (Single) to Table 4 (Multiple).", "risk": "risk-med"},
    "Coronary Artery Disease": {"qs": ["Date of diagnosis?", "Any bypass surgery?", "Current symptoms?"], "rating": "Table 2 to Decline.", "risk": "risk-high"},
    "Stroke / TIA": {"qs": ["Date of event?", "Any residual weakness?", "Carotid ultrasound results?"], "rating": "Postpone (0-1yr). Table 4 to Decline.", "risk": "risk-high"},
    "Pacemaker": {"qs": ["Date implanted?", "Underlying condition?", "Battery check date?"], "rating": "Standard (Sinus Node) to Table 2.", "risk": "risk-med"},
    "Heart Murmur": {"qs": ["Functional or organic?", "Recent echocardiogram?", "Valve involvement?"], "rating": "Preferred (Functional) to Table 4.", "risk": "risk-med"},
    "Aortic Stenosis": {"qs": ["Mild, Moderate or Severe?", "Valve replacement planned?", "Symptoms?"], "rating": "Mild/Stable = Standard. Severe = Decline.", "risk": "risk-med"},
    "Peripheral Vascular Disease": {"qs": ["Do you have pain walking?", "Any surgery?", "Tobacco use?"], "rating": "Table 4 to Decline.", "risk": "risk-high"},
    "Diabetes Type 2": {"qs": ["Current A1C?", "Age of diagnosis?", "Insulin use?", "Neuropathy?"], "rating": "Standard (A1C < 7.0) to Table 2. (Table 4 if Insulin).", "risk": "risk-med"},
    "Diabetes Type 1": {"qs": ["Age diagnosed?", "Insulin pump?", "Kidney issues?", "A1C average?"], "rating": "Table 4 to Table 8. Rarely Standard.", "risk": "risk-high"},
    "Hypothyroidism": {"qs": ["Date diagnosed?", "TSH levels stable?", "Taking Synthroid?"], "rating": "Preferred Possible.", "risk": "risk-safe"},
    "Hyperthyroidism / Graves": {"qs": ["Date diagnosed?", "Treatment type (Radioactive iodine)?", "Current TSH?"], "rating": "Standard (Stable > 1yr).", "risk": "risk-safe"},
    "Hashimoto's": {"qs": ["TSH levels?", "Any goiter or nodules?", "Medications?"], "rating": "Preferred to Standard.", "risk": "risk-safe"},
    "Sleep Apnea": {"qs": ["CPAP use nightly?", "Compliance logs?", "Last sleep study?"], "rating": "Standard (Compliant). Table 2 to Decline (No CPAP).", "risk": "risk-med"},
    "COPD / Emphysema": {"qs": ["Oxygen use?", "Hospitalizations?", "Tobacco use?"], "rating": "Table 2 (Mild) to Decline (Severe/Smoker).", "risk": "risk-high"},
    "Asthma": {"qs": ["Inhaler frequency?", "Oral steroids (Prednisone)?", "Hospital visits?"], "rating": "Standard (Mild) to Table 3 (Severe).", "risk": "risk-safe"},
    "Sarcoidosis": {"qs": ["Lungs only or systemic?", "Current steroid use?", "Date of last flare?"], "rating": "Standard (In remission) to Table 4.", "risk": "risk-med"},
    "Anxiety": {"qs": ["Medication count?", "Hospitalizations?", "Time off work?"], "rating": "Preferred (Mild) to Table 2 (Severe).", "risk": "risk-safe"},
    "Depression": {"qs": ["Hospitalizations?", "Suicide attempts?", "Electro-shock therapy?"], "rating": "Standard (Mild) to Table 4/Decline (Severe).", "risk": "risk-med"},
    "Bipolar Disorder": {"qs": ["Type 1 or 2?", "Hospitalizations < 5 years?", "Stable on meds?"], "rating": "Table 2 minimum. Often Table 4+.", "risk": "risk-high"},
    "ADHD / ADD": {"qs": ["Medication name?", "Any history of drug abuse?", "Stable employment?"], "rating": "Preferred to Standard.", "risk": "risk-safe"},
    "PTSD": {"qs": ["Source of trauma?", "Disability status?", "Substance abuse history?"], "rating": "Standard (Mild) to Decline.", "risk": "risk-med"},
    "Crohn's Disease": {"qs": ["Date of last flare?", "Surgery history?", "Biologic meds (Humira)?"], "rating": "Standard (Remission > 2yr) to Table 4.", "risk": "risk-med"},
    "Ulcerative Colitis": {"qs": ["Colonoscopy results?", "Steroid use?", "Surgery?"], "rating": "Standard (Mild) to Table 3.", "risk": "risk-med"},
    "Hepatitis C": {"qs": ["Cured/Treated?", "Liver enzyme levels?", "Alcohol use?"], "rating": "Standard (Cured) to Decline (Untreated).", "risk": "risk-safe"},
    "Fatty Liver": {"qs": ["Liver function tests?", "Alcohol history?", "BMI?"], "rating": "Standard (Mild) to Table 3.", "risk": "risk-med"},
    "Gastric Bypass / Sleeve": {"qs": ["Date of surgery?", "Current weight stable?", "Complications?"], "rating": "Postpone (<6mos). Standard (After 1yr).", "risk": "risk-safe"},
    "GERD / Reflux": {"qs": ["Medications?", "Barrett's Esophagus diagnosis?", "Endoscopy results?"], "rating": "Preferred to Standard.", "risk": "risk-safe"},
    "Seizures / Epilepsy": {"qs": ["Date of last seizure?", "Type (Grand/Petit)?", "Driving restrictions?"], "rating": "Standard (>2yrs seizure free) to Table 4.", "risk": "risk-med"},
    "Multiple Sclerosis (MS)": {"qs": ["Relapsing or Progressive?", "Can you walk unassisted?", "Date diagnosed?"], "rating": "Table 2 to Decline.", "risk": "risk-high"},
    "Parkinson's": {"qs": ["Age onset?", "Progression speed?", "Daily living activities?"], "rating": "Table 4 to Decline.", "risk": "risk-high"},
    "Rheumatoid Arthritis": {"qs": ["Biologic meds?", "Deformity?", "Disability?"], "rating": "Standard to Table 3.", "risk": "risk-med"},
    "Lupus (SLE)": {"qs": ["Organ involvement (Kidney)?", "Steroid use?", "Date diagnosed?"], "rating": "Table 2 to Decline.", "risk": "risk-high"},
    "Fibromyalgia": {"qs": ["Disability status?", "Narcotic pain meds?", "Depression history?"], "rating": "Standard to Table 2.", "risk": "risk-safe"},
    "Gout": {"qs": ["Frequency of attacks?", "Kidney function?", "Alcohol use?"], "rating": "Standard.", "risk": "risk-safe"},
    "Breast Cancer History": {"qs": ["Date of last treatment?", "Stage/Grade?", "Lymph node involvement?"], "rating": "Flat Extra or Standard > 5yrs.", "risk": "risk-high"},
    "Prostate Cancer History": {"qs": ["Gleason score?", "Surgery or Radiation?", "Current PSA?"], "rating": "Standard (Low grade/Surgery) to Table 4.", "risk": "risk-high"},
    "Melanoma History": {"qs": ["Clark Level / Breslow Depth?", "Date removed?", "Chemo?"], "rating": "Standard (In Situ) to Decline (Deep).", "risk": "risk-high"},
    "Colon Cancer History": {"qs": ["Stage?", "Date of surgery?", "Colonoscopy since?"], "rating": "Postpone (0-2yrs). Table 2 to Standard > 5yrs.", "risk": "risk-high"},
    "Thyroid Cancer": {"qs": ["Type (Papillary)?", "Radioactive iodine?", "Date treatment ended?"], "rating": "Standard (after 1 year).", "risk": "risk-med"},
    "Lymphoma (Hodgkins)": {"qs": ["Stage?", "Date of last chemo?", "Recurrence?"], "rating": "Flat Extra or Table Rating (Requires 2-5yr wait).", "risk": "risk-high"},
    "Kidney Stones": {"qs": ["Single or multiple?", "Surgery required?", "Kidney function normal?"], "rating": "Preferred (Single) to Table 2.", "risk": "risk-safe"},
    "Chronic Kidney Disease": {"qs": ["What is the Stage (1-5)?", "GFR level?", "Diabetic?"], "rating": "Standard (Stage 1) to Decline (Stage 3+).", "risk": "risk-high"},
    "Barrett's Esophagus": {"qs": ["Biopsy results?", "Dysplasia?", "Follow up schedule?"], "rating": "Standard to Table 3.", "risk": "risk-med"},
    "Alcohol History": {"qs": ["Date of last drink?", "AA attendance?", "DUI history?"], "rating": "Postpone (<2yrs sober). Standard (>5yrs sober).", "risk": "risk-high"}
}

def check_comorbidities(selected_conditions, is_smoker, current_bmi):
    warnings = []
    if is_smoker: warnings.append("SMOKER STATUS: Rates will be Standard Smoker (Tobacco) at best.")
    if current_bmi > 30: warnings.append("BUILD RATING: High BMI typically triggers a Table Rating based on build alone.")
    if is_smoker:
        if "COPD / Emphysema" in selected_conditions or "Asthma" in selected_conditions: warnings.append("DECLINE WARNING: COPD/Asthma + Smoking is a major knockout for most carriers.")
        if "Heart Attack (History of)" in selected_conditions: warnings.append("HIGH RISK: Smoking after a Heart Attack is typically Table 4 to Decline.")
    if current_bmi > 35:
        if "Sleep Apnea" in selected_conditions: warnings.append("BUILD RISK: Sleep Apnea with BMI > 35 requires documented CPAP compliance for best rates.")
    if "Diabetes Type 2" in selected_conditions and "Heart Attack (History of)" in selected_conditions: warnings.append("COMORBIDITY ALERT: Diabetes + Heart History is treated very strictly. Expect Table 4 minimum.")
    return warnings
def get_product_matrix(risk_level):
    if risk_level == "risk-safe":
        return [
            {"Category": "Term (10-30yr)", "Outlook": "💎 Best", "Note": "Preferred Potential"},
            {"Category": "Perm (IUL/UL/WL)", "Outlook": "💎 Best", "Note": "Standard/Preferred"},
            {"Category": "Final Expense", "Outlook": "💎 Best", "Note": "Preferred Rates"},
            {"Category": "Disability (DI)", "Outlook": "✅ Good", "Note": "Subject to Occupation"},
            {"Category": "Long-Term Care", "Outlook": "💎 Best", "Note": "Standard/Preferred"}
        ]
    
    elif risk_level == "risk-med":
        return [
            {"Category": "Term (10-30yr)", "Outlook": "⚠️ Rated", "Note": "Standard to Table 4"},
            {"Category": "Perm (IUL/UL/WL)", "Outlook": "✅ Good", "Note": "Standard Likely"},
            {"Category": "Final Expense", "Outlook": "💎 Best", "Note": "Preferred Available"},
            {"Category": "Disability (DI)", "Outlook": "❌ Poor", "Note": "Likely Decline/Excl."},
            {"Category": "Long-Term Care", "Outlook": "⚠️ Rated", "Note": "Standard to Class 2"}
        ]
    
    else: # risk-high
        return [
            {"Category": "Term (10-30yr)", "Outlook": "❌ Poor", "Note": "Likely Decline/Postpone"},
            {"Category": "Perm (IUL/UL/WL)", "Outlook": "⚠️ Rated", "Note": "Trial App Required"},
            {"Category": "Final Expense", "Outlook": "✅ Good", "Note": "Standard/Graded"},
            {"Category": "Disability (DI)", "Outlook": "❌ Poor", "Note": "Decline"},
            {"Category": "Long-Term Care", "Outlook": "❌ Poor", "Note": "Decline"}
        ]
# =========================================================
# APP TABS (Rx Assistant Pro Edition)
# =========================================================
tab1, tab2, tab3 = st.tabs(["🔍 Drug Decoder (FDA)", "💊 Multi-Med Combo Check", "🩺 Impairment Analyst (Conditions)"])

with tab1:
    col_a, col_b = st.columns([4, 1])
    with col_a: st.markdown("### 🔍 Search by Medication Name")
    with col_b: st.button("🔄 Clear", on_click=clear_single, key="clear_1")
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
                        st.markdown(f"<span class='rating-text'>📊 Est. Life Rating: {insight['rating']}</span>", unsafe_allow_html=True)
                        
                        # --- PDF BUTTON ---
                        report_text = [f"Risk: {insight['risk']}", f"Est. Life Rating: {insight['rating']}"] + [f"Ask: {q}" for q in insight['questions']]
                        pdf_data = create_pdf(f"Report - {brand}", [brand], report_text, risk_level=insight['style'], fda_text_content=indications)
                        st.download_button("📄 Download PDF Report", data=pdf_data, file_name=f"{brand}_report.pdf", mime="application/pdf", key=f"pdf_btn_{brand}")

                    with c2:
                        st.markdown("**❓ Field Questions:**")
                        for q in insight['questions']: st.write(f"✅ *{q}*")
                        
                        # --- ADDED MATRIX WITH BALANCED CAPTION ---
                        st.markdown("#### 🎯 Product Suitability Matrix")
                        st.caption("💡 *Ratings are estimates based on clinical control and co-morbidities.*")
                        st.table(get_product_matrix(insight['style']))
                        
                        with st.expander("Show FDA Official Text"): st.write(indications)
                else:
                    matches = difflib.get_close_matches(single_drug, COMMON_DRUGS_LIST, n=1, cutoff=0.6)
                    st.error(f"❌ '{single_drug}' not found.")
                    if matches:
                        suggested_word = matches[0]
                        st.info(f"💡 Did you mean: **{suggested_word}**?")
                        st.session_state.suggestion = suggested_word
                        st.button(f"Yes, search for {suggested_word}", on_click=fix_spelling_callback, key="spell_check")
            except Exception as e: st.error(f"Error: {e}")

with tab2:
    col_x, col_y = st.columns([4, 1])
    with col_x: st.markdown("### 💊 Multi-Medication Combo Check")
    with col_y: st.button("🔄 Clear List", on_click=clear_multi, key="clear_2")
    multi_input = st.text_area("Paste Med List (comma separated):", key="multi_input", placeholder="Metformin, Lisinopril, Plavix")
    
    if st.button("Analyze Combinations", key="analyze_btn"):
        if multi_input:
            meds = [m.strip() for m in multi_input.split(',')]
            cats = []; valid_meds = []
            for med in meds:
                if len(med) < 3: continue
                try:
                    url = f'https://api.fda.gov/drug/label.json?search=openfda.brand_name:"{med}"&limit=1'
                    r = requests.get(url)
                    if r.status_code == 200:
                        ind = r.json()['results'][0].get('indications_and_usage', [""])[0]
                        cat = simple_category_check(ind, med)
                        cats.append(cat); valid_meds.append(med)
                        st.write(f"✅ **{med}** identified as *{cat}*")
                except: pass
            
            combos = check_med_combinations(cats)
            if combos:
                for c in combos: st.error(c)
            else: st.success("No major negative combinations detected.")
            
            if valid_meds:
                combo_text = combos if combos else ["No high-risk combinations found."]
                pdf_bytes = create_pdf("Multi-Med Analysis", valid_meds, combo_text)
                st.download_button("📄 Download Combo Report", data=pdf_bytes, file_name="combo_report.pdf", key="pdf_multi")

with tab3:
    st.markdown("### 🩺 Condition & Impairment Search")
    col_i1, col_i2 = st.columns(2)
    with col_i1:
        sorted_conditions = sorted(list(IMPAIRMENT_DATA.keys()))
        conditions = st.multiselect("Select Conditions:", sorted_conditions, key="cond_select")
    with col_i2:
        st.write("Risk Factors:")
        is_smoker = st.checkbox("🚬 Tobacco / Nicotine User")
        st.write(f"⚖️ Current BMI: **{bmi}** ({bmi_category})")
    
    if conditions or is_smoker or bmi > 30:
        st.divider()
        st.subheader("📝 Underwriting Analysis")
        warnings = check_comorbidities(conditions, is_smoker, bmi)
        for w in warnings: st.error(w)
        
        pdf_lines = []
        if warnings: pdf_lines = ["--- WARNINGS ---"] + warnings + ["--- DETAILS ---"]
        if conditions:
            for cond in conditions:
                data = IMPAIRMENT_DATA[cond]
                
               # --- UNIVERSAL RISK LOGIC ---
                # Pulls the risk directly from the 'risk' tag in your dictionary
                # Defaults to 'risk-med' if a tag is missing
                risk_lv = data.get('risk', 'risk-med') 
                
                # Risk Bump: Upgrades risk if they smoke or are obese
                if is_smoker or bmi > 35:
                    if risk_lv == "risk-safe": 
                        risk_lv = "risk-med"
                    elif risk_lv == "risk-med": 
                        risk_lv = "risk-high"

                st.markdown(f"### {cond}")
                
                # Create the same 1:2 column ratio as Tab 1
                ic1, ic2 = st.columns([1, 2])
                
                with ic1:
                    # Base Rating Box
                    st.markdown(f"<span class='rating-text'>📊 Base Life Rating: {data['rating']}</span>", unsafe_allow_html=True)
                    st.write("") # Spacer

                with ic2:
                    # 1. DISPLAY THE QUESTIONS (This was the missing piece)
                    st.markdown("#### ❓ Field Questions:")
                    if 'qs' in data:
                        for q in data['qs']: 
                            st.write(f"✅ *{q}*")
                    
                    st.write("") # Small spacer

                    # 2. DISPLAY THE MATRIX
                    st.markdown("#### 🎯 Product Suitability Matrix")
                    st.caption("💡 *Ratings are estimates based on clinical control and co-morbidities.*")
                    st.table(get_product_matrix(risk_lv))

                # Keep the PDF lines logic behind the scenes
                pdf_lines.append(f"Condition: {cond} | Rating: {data['rating']}")
                for q in data['qs']: pdf_lines.append(f" - {q}")
            
            st.divider()
            imp_pdf = create_pdf("Impairment Analysis", conditions, pdf_lines, risk_level=risk_lv)
            st.download_button("📄 Download Impairment Report", data=imp_pdf, file_name="imp_report.pdf", key="pdf_imp")
# --- FOOTER ---
st.markdown("---")

# RESTORED DISCLAIMER
with st.expander("⚠️ Legal Disclaimer & Liability Information"):
    st.markdown("""
    **1. Educational Use Only:** This tool is designed solely for informational and educational purposes to assist insurance professionals. It is not a medical device and should not be used for medical diagnosis.
    
    **2. No Binding Offer:** The risk class estimates (e.g., "Standard", "Table 2") are generalized approximations based on industry averages. They do not constitute a binding offer, quote, or guarantee of coverage from any specific insurance carrier.
    
    **3. Carrier Specifics:** Every insurance carrier has unique underwriting guidelines, knock-out questions, and credit programs. Users must always consult the official underwriting manuals and guides of the specific carrier they are writing business with.
    
    **4. Liability Waiver:** InsurTech Express and the creators of this tool accept no liability for errors, omissions, inaccuracies, or financial losses resulting from the use of this software. The user assumes all responsibility for verifying information with the appropriate carrier.
    """)

# BRANDING & TRADEMARK NOTICE
st.markdown(
    """
    <div style="text-align: center; margin-top: 20px;">
        <div class='footer-link'>Powered by <a href='https://www.insurtechexpress.com' target='_blank'>InsurTech Express</a></div>
        <div style="color: #888; font-size: 11px; margin-top: 15px; line-height: 1.6;">
            <b>Rx Assistant™</b> and <b>Product Suitability Matrix™</b> are trademarks of InsurTech Express. <br>
            © 2026 ITXMeds.com | All Rights Reserved. <br>
            <span style="font-style: italic;">Carrier-Agnostic Field Guide for Licensed Professionals.</span>
        </div>
    </div>
    """, 
    unsafe_allow_html=True
)

