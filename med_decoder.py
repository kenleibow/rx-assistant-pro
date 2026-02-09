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
                import os
                import json
                
                # 1. Grab the big JSON block we put in Railway
                creds_json = os.environ.get("GCP_SERVICE_ACCOUNT")
                
                if not creds_json:
                    st.error("🚨 GCP_SERVICE_ACCOUNT variable not found in Railway.")
                else:
                    # 2. Parse the JSON
                    creds_dict = json.loads(creds_json)
                    
                    # 3. Fix the private key formatting
                    if "private_key" in creds_dict:
                        creds_dict["private_key"] = creds_dict["private_key"].replace('\\n', '\n')

                    # 4. Connect to Google
                    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
                    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
                    client = gspread.authorize(creds)
                    
                    # 5. Open the sheet (using the sheet_id variable from Railway)
                    s_id = os.environ.get("sheet_id") or os.environ.get("SHEET_ID")
                    sheet = client.open_by_key(s_id).sheet1
                    
                    # 6. Log the entry
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    sheet.append_row([current_time, user_name, user_email])

                    st.session_state.logged_in = True
                    st.rerun()
            except Exception as e:
                st.error(f"🚨 Connection Error: {e}")

st.stop()
# --- CONFIGURATION (Reached only if logged in) ---
st.set_page_config(page_title="Rx Field Assistant", page_icon="🛡️", layout="wide")

# =========================================================
#  CALLBACKS (MUST BE AT THE TOP)
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
    st.header("⚖️ BMI Calculator")
    feet = st.number_input("Height (Feet)", 4, 8, 5)
    inches = st.number_input("Height (Inches)", 0, 11, 9)
    weight = st.number_input("Weight (lbs)", 80, 500, 140)
    total_inches = (feet * 12) + inches
    bmi = 0.0
    bmi_category = "Normal"
    if total_inches > 0:
        bmi = round((weight / (total_inches ** 2)) * 703, 1)
        if bmi < 18.5: st.info(f"BMI: {bmi} (Underweight)"); bmi_category = "Underweight"
        elif bmi < 25: st.success(f"BMI: {bmi} (Normal)"); bmi_category = "Normal"
        elif bmi < 30: st.warning(f"BMI: {bmi} (Overweight)"); bmi_category = "Overweight"
        else: st.error(f"BMI: {bmi} (Obese)"); bmi_category = "Obese"
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
#  IMPAIRMENT DATA
# =========================================================
IMPAIRMENT_DATA = {
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
    "Diabetes Type 2": {"qs": ["Current A1C?", "Age of diagnosis?", "Insulin use?", "Neuropathy?"], "rating": "Standard (A1C<7) to Table 4 (Insulin)."},
    "Diabetes Type 1": {"qs": ["Age diagnosed?", "Insulin pump?", "Kidney issues?", "A1C average?"], "rating": "Table 4 to Table 8. Rarely Standard."},
    "Hypothyroidism": {"qs": ["Date diagnosed?", "TSH levels stable?", "Taking Synthroid?"], "rating": "Preferred Possible."},
    "Hyperthyroidism / Graves": {"qs": ["Date diagnosed?", "Treatment type (Radioactive iodine)?", "Current TSH?"], "rating": "Standard (Stable > 1yr)."},
    "Hashimoto's": {"qs": ["TSH levels?", "Any goiter or nodules?", "Medications?"], "rating": "Preferred to Standard."},
    "Sleep Apnea": {"qs": ["CPAP use nightly?", "Compliance logs?", "Last sleep study?"], "rating": "Standard (Compliant). Table 2 to Decline (No CPAP)."},
    "COPD / Emphysema": {"qs": ["Oxygen use?", "Hospitalizations?", "Tobacco use?"], "rating": "Table 2 (Mild) to Decline (Severe/Smoker)."},
    "Asthma": {"qs": ["Inhaler frequency?", "Oral steroids (Prednisone)?", "Hospital visits?"], "rating": "Standard (Mild) to Table 3 (Severe)."},
    "Sarcoidosis": {"qs": ["Lungs only or systemic?", "Current steroid use?", "Date of last flare?"], "rating": "Standard (In remission) to Table 4."},
    "Anxiety": {"qs": ["Medication count?", "Hospitalizations?", "Time off work?"], "rating": "Preferred (Mild) to Table 2 (Severe)."},
    "Depression": {"qs": ["Hospitalizations?", "Suicide attempts?", "Electro-shock therapy?"], "rating": "Standard (Mild) to Table 4/Decline (Severe)."},
    "Bipolar Disorder": {"qs": ["Type 1 or 2?", "Hospitalizations < 5 years?", "Stable on meds?"], "rating": "Table 2 minimum. Often Table 4+."},
    "ADHD / ADD": {"qs": ["Medication name?", "Any history of drug abuse?", "Stable employment?"], "rating": "Preferred to Standard."},
    "PTSD": {"qs": ["Source of trauma?", "Disability status?", "Substance abuse history?"], "rating": "Standard (Mild) to Decline."},
    "Crohn's Disease": {"qs": ["Date of last flare?", "Surgery history?", "Biologic meds (Humira)?"], "rating": "Standard (Remission > 2yr) to Table 4."},
    "Ulcerative Colitis": {"qs": ["Colonoscopy results?", "Steroid use?", "Surgery?"], "rating": "Standard (Mild) to Table 3."},
    "Hepatitis C": {"qs": ["Cured/Treated?", "Liver enzyme levels?", "Alcohol use?"], "rating": "Standard (Cured) to Decline (Untreated)."},
    "Fatty Liver": {"qs": ["Liver function tests?", "Alcohol history?", "BMI?"], "rating": "Standard (Mild) to Table 3."},
    "Gastric Bypass / Sleeve": {"qs": ["Date of surgery?", "Current weight stable?", "Complications?"], "rating": "Postpone (<6mos). Standard (After 1yr)."},
    "GERD / Reflux": {"qs": ["Medications?", "Barrett's Esophagus diagnosis?", "Endoscopy results?"], "rating": "Preferred to Standard."},
    "Seizures / Epilepsy": {"qs": ["Date of last seizure?", "Type (Grand/Petit)?", "Driving restrictions?"], "rating": "Standard (>2yrs seizure free) to Table 4."},
    "Multiple Sclerosis (MS)": {"qs": ["Relapsing or Progressive?", "Can you walk unassisted?", "Date diagnosed?"], "rating": "Table 2 to Decline."},
    "Parkinson's": {"qs": ["Age onset?", "Progression speed?", "Daily living activities?"], "rating": "Table 4 to Decline."},
    "Rheumatoid Arthritis": {"qs": ["Biologic meds?", "Deformity?", "Disability?"], "rating": "Standard to Table 3."},
    "Lupus (SLE)": {"qs": ["Organ involvement (Kidney)?", "Steroid use?", "Date diagnosed?"], "rating": "Table 2 to Decline."},
    "Fibromyalgia": {"qs": ["Disability status?", "Narcotic pain meds?", "Depression history?"], "rating": "Standard to Table 2."},
    "Gout": {"qs": ["Frequency of attacks?", "Kidney function?", "Alcohol use?"], "rating": "Standard."},
    "Breast Cancer History": {"qs": ["Date of last treatment?", "Stage/Grade?", "Lymph node involvement?"], "rating": "Flat Extra ($2-5/1000) or Standard > 5yrs."},
    "Prostate Cancer History": {"qs": ["Gleason score?", "Surgery or Radiation?", "Current PSA?"], "rating": "Standard (Low grade/Surgery) to Table 4."},
    "Melanoma History": {"qs": ["Clark Level / Breslow Depth?", "Date removed?", "Chemo?"], "rating": "Standard (In Situ) to Decline (Deep)."},
    "Colon Cancer History": {"qs": ["Stage?", "Date of surgery?", "Colonoscopy since?"], "rating": "Postpone (0-2yrs). Table 2 to Standard > 5yrs."},
    "Thyroid Cancer": {"qs": ["Type (Papillary)?", "Radioactive iodine?", "Date treatment ended?"], "rating": "Standard (after 1 year)."},
    "Lymphoma (Hodgkins)": {"qs": ["Stage?", "Date of last chemo?", "Recurrence?"], "rating": "Flat Extra or Table Rating (Requires 2-5yr wait)."},
    "Kidney Stones": {"qs": ["Single or multiple?", "Surgery required?", "Kidney function normal?"], "rating": "Preferred (Single) to Table 2."},
    "Chronic Kidney Disease": {"qs": ["What is the Stage (1-5)?", "GFR level?", "Diabetic?"], "rating": "Standard (Stage 1) to Decline (Stage 3+)."},
    "Barrett's Esophagus": {"qs": ["Biopsy results?", "Dysplasia?", "Follow up schedule?"], "rating": "Standard to Table 3."},
    "Alcohol History": {"qs": ["Date of last drink?", "AA attendance?", "DUI history?"], "rating": "Postpone (<2yrs sober). Standard (>5yrs sober)."}
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

# =========================================================
# APP TABS
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
                        st.caption(f"Est. Rating: {insight['rating']}")
                    with c2:
                        st.markdown("**❓ Field Questions:**")
                        for q in insight['questions']: st.write(f"✅ *{q}*")
                    with st.expander("Show FDA Official Text"): st.write(indications)
                    
                    # --- PDF BUTTON (RECOVERED) ---
                    report_text = [f"Risk: {insight['risk']}", f"Est. Rating: {insight['rating']}"] + [f"Ask: {q}" for q in insight['questions']]
                    pdf_data = create_pdf(f"Report - {brand}", [brand], report_text, fda_text_content=indications)
                    st.download_button("📄 Download PDF Report", data=pdf_data, file_name=f"{brand}_report.pdf", mime="application/pdf", key=f"pdf_btn_{brand}")
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
                with st.container():
                    st.markdown(f"**{cond}**")
                    st.caption(f"Base Rating: {data['rating']}")
                    for q in data['qs']: st.write(f"🔹 *{q}*")
                    pdf_lines.append(f"Condition: {cond} | Rating: {data['rating']}")
                    for q in data['qs']: pdf_lines.append(f" - {q}")
            st.markdown("---")
            imp_pdf = create_pdf("Impairment Analysis", conditions, pdf_lines)
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

st.markdown("<div class='footer-link'>Powered by <a href='https://www.insurtechexpress.com' target='_blank'>InsurTech Express</a></div>", unsafe_allow_html=True)


