import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import requests
from fpdf import FPDF
import difflib

# --- CONFIGURATION (MUST BE FIRST) ---
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
                    # 1. Get keys from the Streamlit "Vault"
                    creds_dict = st.secrets["gcp_service_account"]

                    # 2. Set the permissions
                    scopes = [
                        "https://www.googleapis.com/auth/spreadsheets",
                        "https://www.googleapis.com/auth/drive"
                    ]

                    # 3. Connect to Google
                    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
                    client = gspread.authorize(creds)
                    
                    # 4. Open the sheet and write the data
                    sheet = client.open("Rx_Login_Tracker").sheet1
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    sheet.append_row([current_time, user_name, user_email])

                    # 5. Success! Unlock the app
                    st.session_state.logged_in = True
                    st.rerun()

                except Exception as e:
                    st.error(f"🚨 Connection Error: {e}")

    # STOP HERE IF NOT LOGGED IN
    st.stop()

# =========================================================
# CALLBACKS
# =========================================================
def fix_spelling_callback():
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
    .bmi-pointer {
        position: fixed; top: 60px; left: 20px; z-index: 9999;
        background-color: #0066cc; color: white; padding: 5px 10px;
        border-radius: 5px; font-weight: bold; font-size: 14px;
        pointer-events: none; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }
    section[data-testid="stSidebar"][aria-expanded="true"] + .main .bmi-pointer { display: none; }
    </style>
    <div class="bmi-pointer">BMI Calculator</div>
    """, unsafe_allow_html=True)

# =========================================================
# DATA: COMMON DRUG LIST
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
# GLOBAL STATE: BMI CALCULATOR (SIDEBAR)
# =========================================================
with st.sidebar:
    st.header("⚖️ BMI Calculator")
    feet = st.number_input("Height (Feet)", 4, 8, 5)
    inches = st.number_input("Height (Inches)", 0, 11, 9)
    weight = st.number_input("Weight (lbs)", 80, 500, 140)
    total_inches = (feet * 12) + inches
    bmi = round((weight / (total_inches ** 2)) * 703, 1) if total_inches > 0 else 0.0
    bmi_category = "Normal"
    if bmi < 18.5: st.info(f"BMI: {bmi} (Underweight)"); bmi_category="Underweight"
    elif bmi < 25: st.success(f"BMI: {bmi} (Normal)"); bmi_category="Normal"
    elif bmi < 30: st.warning(f"BMI: {bmi} (Overweight)"); bmi_category="Overweight"
    elif bmi < 35: st.error(f"BMI: {bmi} (Obese)"); bmi_category="Obese"
    else: st.error(f"BMI: {bmi} (Severe Obesity)"); bmi_category="Severe Obesity"
    st.markdown("---")
    st.caption("Rx Field Assistant v9.4")

st.title("🛡️ Life Insurance Rx Assistant")

# --- PDF GENERATOR FUNCTION ---
def create_pdf(title, items_list, analysis_text, fda_text_content=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    def clean(text): return text.encode('latin-1', 'replace').decode('latin-1')
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=clean(f"Rx Assistant - {title}"), ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Items Analyzed:", ln=True, align='L')
    pdf.set_font("Arial", size=12)
    for item in items_list: pdf.cell(200, 10, txt=clean(f"- {item}"), ln=True, align='L')
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Underwriting Analysis:", ln=True, align='L')
    pdf.set_font("Arial", size=12)
    if isinstance(analysis_text, list):
        for line in analysis_text: pdf.multi_cell(0, 10, txt=clean(f"- {line}"))
    else: pdf.multi_cell(0, 10, txt=clean(analysis_text))
    if fda_text_content:
        pdf.ln(10); pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="Official FDA Indications (Excerpt):", ln=True, align='L')
        pdf.set_font("Arial", size=10); pdf.multi_cell(0, 6, txt=clean(fda_text_content[:2000] + "..."))
    return pdf.output(dest='S').encode('latin-1')

# =========================================================
# LOGIC ENGINES
# =========================================================
def analyze_single_med(indication_text, brand_name):
    text = indication_text.lower(); name = brand_name.lower()
    if "metformin" in name: return {"risk": "Diabetes Type 2", "style": "risk-med", "questions": ["Is this for Pre-Diabetes or Type 2?", "What is your A1C?"], "rating": "Standard to Table 2."}
    elif "lisinopril" in name or "amlodipine" in name: return {"risk": "Hypertension", "style": "risk-safe", "questions": ["Is BP controlled?"], "rating": "Preferred Best possible."}
    elif "plavix" in name or "clopidogrel" in name: return {"risk": "Heart/Stroke", "style": "risk-high", "questions": ["Stent placement history?"], "rating": "Standard to Decline."}
    return {"risk": "General Maintenance", "style": "risk-safe", "questions": ["Why was this prescribed?"], "rating": "Depends on condition."}

def check_med_combinations(found_categories):
    unique_cats = set(found_categories)
    insights = []
    if "Diabetes" in unique_cats and "Hypertension" in unique_cats: insights.append("METABOLIC SYNDROME: Watch for combo credits.")
    return insights

def simple_category_check(text, name):
    t = text.lower(); n = name.lower()
    if "diabetes" in t or "metformin" in n: return "Diabetes"
    if "hypertension" in t or "lisinopril" in n: return "Hypertension"
    return "Other"

# =========================================================
# IMPAIRMENT DATA
# =========================================================
IMPAIRMENT_DATA = {
    "Hypertension (High BP)": {"qs": ["Date of last reading?", "Is it controlled?"], "rating": "Preferred to Table 2."},
    "Heart Attack (History of)": {"qs": ["Date of event?", "Current EF%?"], "rating": "Table 2 to 4."},
    "Diabetes Type 2": {"qs": ["Current A1C?", "Insulin use?"], "rating": "Standard to Table 4."},
    "Sleep Apnea": {"qs": ["CPAP use nightly?"], "rating": "Standard (Compliant)."}
}

def check_comorbidities(selected_conditions, is_smoker, current_bmi):
    warnings = []
    if is_smoker: warnings.append("SMOKER STATUS: Standard Smoker rates apply.")
    if current_bmi > 30: warnings.append("BUILD RATING: BMI triggers Table Rating.")
    return warnings

# =========================================================
# APP LAYOUT
# =========================================================
tab1, tab2, tab3 = st.tabs(["🔍 Drug Decoder (FDA)", "💊 Multi-Med Check", "🩺 Impairment Analyst"])

with tab1:
    col_a, col_b = st.columns([4, 1])
    with col_a: st.markdown("### 🔍 Search by Medication")
    with col_b: st.button("🔄 Clear", on_click=clear_single, key="clear_1")
    single_drug = st.text_input("Enter Drug Name:", key="single_input")
    if single_drug:
        try:
            url = f'https://api.fda.gov/drug/label.json?search=openfda.brand_name:"{single_drug}"&limit=1'
            r = requests.get(url)
            if r.status_code == 200:
                data = r.json()['results'][0]
                brand = data['openfda'].get('brand_name', [single_drug])[0]
                indications = data.get('indications_and_usage', ["No text found"])[0]
                insight = analyze_single_med(indications, single_drug)
                st.success(f"**Found:** {brand}")
                st.markdown(f"<div class='{insight['style']}'><b>Risk:</b> {insight['risk']}</div>", unsafe_allow_html=True)
                for q in insight['questions']: st.write(f"✅ {q}")
                with st.expander("Show FDA Text"): st.write(indications)
                # PDF
                report_text = [f"Risk: {insight['risk']}", f"Est. Rating: {insight['rating']}"] + insight['questions']
                pdf_data = create_pdf(brand, [brand], report_text, indications)
                st.download_button("📄 Download PDF Report", data=pdf_data, file_name=f"{brand}_report.pdf", key=f"pdf_{brand}")
            else:
                matches = difflib.get_close_matches(single_drug, COMMON_DRUGS_LIST, n=1, cutoff=0.6)
                if matches:
                    st.session_state.suggestion = matches[0]
                    st.button(f"Did you mean {matches[0]}?", on_click=fix_spelling_callback)
        except Exception as e: st.error(f"Error: {e}")

with tab2:
    multi_input = st.text_area("Paste Med List:", key="multi_input")
    if st.button("Analyze Combinations"):
        meds = [m.strip() for m in multi_input.split(',')]
        valid_meds = []
        for med in meds:
            if len(med) > 2: valid_meds.append(med); st.write(f"✅ {med} Added")
        if valid_meds:
            pdf_bytes = create_pdf("Multi-Med", valid_meds, "No major high-risk combos.")
            st.download_button("📄 Download Combo Report", data=pdf_bytes, file_name="combo_report.pdf", key="pdf_multi")

with tab3:
    sorted_conditions = sorted(list(IMPAIRMENT_DATA.keys()))
    conditions = st.multiselect("Select Conditions:", sorted_conditions)
    is_smoker = st.checkbox("🚬 Tobacco User")
    if conditions or is_smoker or bmi > 30:
        pdf_lines = []
        for cond in conditions:
            data = IMPAIRMENT_DATA[cond]
            st.write(f"**{cond}** (Rating: {data['rating']})")
            pdf_lines.append(f"{cond}: {data['rating']}")
        imp_pdf = create_pdf("Impairment Analysis", conditions, pdf_lines)
        st.download_button("📄 Download Impairment Report", data=imp_pdf, file_name="imp_report.pdf", key="pdf_imp")

st.markdown("---")
with st.expander("⚠️ Legal Disclaimer"): st.write("Educational use only. Not a binding offer.")
st.markdown("<div class='footer-link'>Powered by <a href='https://www.insurtechexpress.com'>InsurTech Express</a></div>", unsafe_allow_html=True)
