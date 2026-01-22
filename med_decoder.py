import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import requests
from fpdf import FPDF
import difflib

# --- 1. CONFIGURATION (MUST BE FIRST) ---
st.set_page_config(page_title="Rx Field Assistant", page_icon="🛡️", layout="wide")

# ==========================================
# 🔐 REGISTRATION & LOGGING SECTION
# ==========================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Rx Assistant - Registration")
    st.write("Please provide your details to access the tool.")
    
    with st.form("registration_form"):
        user_name = st.text_input("Full Name")
        user_email = st.text_input("Email Address")
        submit = st.form_submit_button("Enter Assistant")

        if submit:
            if not user_name or not user_email:
                st.error("⚠️ Please fill in BOTH Name and Email.")
            else:
                try:
                    creds_dict = st.secrets["gcp_service_account"]
                    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
                    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
                    client = gspread.authorize(creds)
                    sheet = client.open("Rx_Login_Tracker").sheet1
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    sheet.append_row([current_time, user_name, user_email])

                    st.session_state.logged_in = True
                    st.rerun()
                except Exception as e:
                    st.error(f"🚨 Connection Error: {e}")
    st.stop() # Only stops unregistered users

# ==========================================
# 🛠️ PDF GENERATOR FUNCTION
# ==========================================
def create_pdf(title, items_list, analysis_text, fda_text_content=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    def clean(text): return text.encode('latin-1', 'replace').decode('latin-1')
    
    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=clean(f"Rx Assistant - {title}"), ln=True, align='C')
    pdf.ln(10)
    
    # Items
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Items Analyzed:", ln=True, align='L')
    pdf.set_font("Arial", size=11)
    for item in items_list:
        pdf.cell(200, 8, txt=clean(f"- {item}"), ln=True, align='L')
    pdf.ln(5)
    
    # Analysis
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Underwriting Analysis:", ln=True, align='L')
    pdf.set_font("Arial", size=11)
    if isinstance(analysis_text, list):
        for line in analysis_text: pdf.multi_cell(0, 8, txt=clean(f"- {line}"))
    else: pdf.multi_cell(0, 8, txt=clean(analysis_text))
    
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 🧠 UNDERWRITING LOGIC & DATA
# ==========================================

def analyze_single_med(indication_text, brand_name):
    text = indication_text.lower(); name = brand_name.lower()
    if "metformin" in name: return {"risk": "Diabetes Type 2", "style": "risk-med", "questions": ["Is this for Pre-Diabetes or Type 2?", "What is your A1C?", "Any neuropathy?"], "rating": "Standard (if A1C < 7.0) to Table 2."}
    elif "lisinopril" in name or "amlodipine" in name: return {"risk": "Hypertension (High BP)", "style": "risk-safe", "questions": ["Is BP controlled?", "Last reading?", "Do you take >2 BP meds?"], "rating": "Preferred Best possible."}
    elif "plavix" in name or "clopidogrel" in name: return {"risk": "Heart Disease / Stroke", "style": "risk-high", "questions": ["History of TIA/Stroke?", "Stent placement?"], "rating": "Standard to Decline."}
    elif "abilify" in name or "aripiprazole" in name: return {"risk": "Bipolar / Depression", "style": "risk-high", "questions": ["Hospitalizations in last 5 years?", "Suicide attempts?"], "rating": "Complex. Bipolar = Table Rating."}
    elif "entresto" in name: return {"risk": "Heart Failure (CHF)", "style": "risk-high", "questions": ["What is your Ejection Fraction?", "Recent hospitalizations?"], "rating": "Likely Decline."}
    if "metastatic" in text: return {"risk": "FLAGGED: Cancer (Severe)", "style": "risk-high", "questions": ["Diagnosis date?", "Treatment status?"], "rating": "Likely Decline."}
    return {"risk": "General / Maintenance", "style": "risk-safe", "questions": ["Why was this prescribed?"], "rating": "Depends on condition."}

def simple_category_check(text, name):
    t = text.lower(); n = name.lower()
    if "diabetes" in t or "metformin" in n: return "Diabetes"
    if "hypertension" in t or "lisinopril" in n: return "Hypertension"
    if "cholesterol" in t or "statin" in n: return "Cholesterol"
    if "heart failure" in t or "plavix" in n: return "Cardiac"
    return "Other"

# MASTER IMPAIRMENT DATA
IMPAIRMENT_DATA = {
    "Hypertension (High BP)": {"qs": ["Date of last reading?", "Is it controlled?", "Med change <12 mos?"], "rating": "Preferred to Table 2."},
    "Heart Attack (History of)": {"qs": ["Date of event?", "Current EF%?", "Recent stress test?"], "rating": "Postpone (0-6mos). Table 2 to 4."},
    "Atrial Fibrillation (AFib)": {"qs": ["Chronic or Paroxysmal?", "Blood thinners?"], "rating": "Standard to Table 2."},
    "Diabetes Type 2": {"qs": ["Current A1C?", "Age of diagnosis?", "Insulin use?"], "rating": "Standard (A1C<7) to Table 4."},
    "Sleep Apnea": {"qs": ["CPAP use nightly?", "Compliance logs?"], "rating": "Standard (Compliant)."},
    "COPD / Emphysema": {"qs": ["Oxygen use?", "Tobacco use?"], "rating": "Table 2 to Decline."},
    "Asthma": {"qs": ["Inhaler frequency?", "Oral steroids?"], "rating": "Standard to Table 3."},
    "Crohn's Disease": {"qs": ["Date of last flare?", "Surgery history?"], "rating": "Standard to Table 4."},
    "Bipolar Disorder": {"qs": ["Hospitalizations?", "Stable on meds?"], "rating": "Table 2 minimum."},
    "Stroke / TIA": {"qs": ["Date of event?", "Residual weakness?"], "rating": "Postpone 1yr. Table 4 to Decline."},
    "Barrett's Esophagus": {"qs": ["Biopsy results?", "Dysplasia?"], "rating": "Standard to Table 3."},
    "Breast Cancer History": {"qs": ["Date last treatment?", "Stage/Grade?"], "rating": "Flat Extra or Standard > 5yrs."}
    # (Note: Add remaining from your original list to this dictionary)
}

# ==========================================
# 🚀 APP INTERFACE
# ==========================================
st.title("🛡️ Life Insurance Rx Assistant")

# Sidebar BMI
with st.sidebar:
    st.header("⚖️ BMI Calculator")
    feet = st.number_input("Height (Feet)", 4, 8, 5)
    inches = st.number_input("Height (Inches)", 0, 11, 9)
    weight = st.number_input("Weight (lbs)", 80, 500, 140)
    total_in = (feet * 12) + inches
    bmi = round((weight / (total_in ** 2)) * 703, 1) if total_in > 0 else 0
    bmi_cat = "Normal"
    if bmi > 30: st.error(f"BMI: {bmi} (Obese)"); bmi_cat="Obese"
    elif bmi > 25: st.warning(f"BMI: {bmi} (Overweight)"); bmi_cat="Overweight"
    else: st.success(f"BMI: {bmi} (Normal)"); bmi_cat="Normal"

# CSS
st.markdown("<style>.risk-high { background-color: #ffcccc; padding: 10px; border-radius: 5px; color: #8a0000; border-left: 5px solid #cc0000; } .risk-med { background-color: #fff4cc; padding: 10px; border-radius: 5px; color: #664d00; border-left: 5px solid #ffcc00; } .risk-safe { background-color: #e6fffa; padding: 10px; border-radius: 5px; color: #004d40; border-left: 5px solid #00bfa5; } div.stButton > button { width: 100%; }</style>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🔍 Drug Decoder", "💊 Multi-Med Check", "🩺 Impairment Analyst"])

with tab1:
    drug_name = st.text_input("Enter Medication Name (e.g., Metformin):")
    if drug_name:
        with st.spinner("Checking FDA..."):
            url = f'https://api.fda.gov/drug/label.json?search=openfda.brand_name:"{drug_name}"&limit=1'
            r = requests.get(url)
            if r.status_code == 200:
                data = r.json()['results'][0]
                brand = data['openfda'].get('brand_name', [drug_name])[0]
                inds = data.get('indications_and_usage', ["No text found"])[0]
                insight = analyze_single_med(inds, brand)
                
                st.success(f"**Found:** {brand}")
                st.markdown(f"<div class='{insight['style']}'><b>Risk:</b> {insight['risk']}</div>", unsafe_allow_html=True)
                st.write(f"**Estimated Rating:** {insight['rating']}")
                for q in insight['questions']: st.write(f"✅ *{q}*")
                
                # --- PDF BUTTON ---
                pdf_body = [f"Risk: {insight['risk']}", f"Est Rating: {insight['rating']}"] + [f"Question: {q}" for q in insight['questions']]
                pdf_bytes = create_pdf(brand, [brand], pdf_body)
                st.download_button("📄 Download PDF Report", data=pdf_bytes, file_name=f"{brand}_Report.pdf", key=f"pdf_{brand}")
            else:
                st.error("Medication not found in FDA database.")

with tab2:
    multi_input = st.text_area("Enter medications separated by commas:")
    if st.button("Analyze List"):
        meds = [m.strip() for m in multi_input.split(',')]
        cats = []
        for med in meds:
            st.write(f"✅ {med} Added")
            cats.append(med)
        # PDF for Multi
        pdf_bytes = create_pdf("Multi-Med Analysis", meds, "Commonly used for the conditions listed. Check for Metabolic Syndrome if Diabetes/BP/Cholesterol are present.")
        st.download_button("📄 Download Multi-Med Report", data=pdf_bytes, file_name="MultiMed_Report.pdf", key="pdf_multi")

with tab3:
    conds = st.multiselect("Select Conditions:", sorted(list(IMPAIRMENT_DATA.keys())))
    is_smoker = st.checkbox("🚬 Smoker")
    if conds:
        pdf_lines = []
        for c in conds:
            st.subheader(c)
            st.write(f"**Rating:** {IMPAIRMENT_DATA[c]['rating']}")
            for q in IMPAIRMENT_DATA[c]['qs']: st.write(f"🔹 {q}")
            pdf_lines.append(f"{c}: {IMPAIRMENT_DATA[c]['rating']}")
        # PDF for Impairments
        pdf_bytes = create_pdf("Impairment Analysis", conds, pdf_lines)
        st.download_button("📄 Download Impairment Report", data=pdf_bytes, file_name="Impairment_Report.pdf", key="pdf_imp")

st.markdown("---")
st.markdown("<center>Powered by <a href='https://www.insurtechexpress.com'>InsurTech Express</a></center>", unsafe_allow_html=True)

