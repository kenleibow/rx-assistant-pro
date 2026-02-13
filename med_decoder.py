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
st.set_page_config(page_title="Rx Assistant Pro", page_icon="🛡️", layout="wide")

# ==========================================
# 🔐 SESSION INITIALIZATION
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "combo_results" not in st.session_state:
    st.session_state.combo_results = None
if "suggestion" not in st.session_state:
    st.session_state.suggestion = ""

# ==========================================
# 🔐 SECRETS & CLOUD HANDSHAKE
# ==========================================
def get_gspread_client():
    try:
        gcp_json = os.environ.get("GCP_SERVICE_ACCOUNT")
        if gcp_json:
            creds_dict = json.loads(gcp_json)
            if "private_key" in creds_dict:
                creds_dict["private_key"] = creds_dict["private_key"].replace('\\n', '\n')
            scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            return gspread.authorize(creds)
    except:
        pass
    return None

# ==========================================
# 🔐 REGISTRATION GATEKEEPER
# ==========================================
if not st.session_state.logged_in:
    st.title("🛡️ Rx Assistant Pro - Access")
    st.info("Please register to access the Field Underwriting Tool.")
    
    with st.form("registration_gate"):
        user_name = st.text_input("Full Name")
        user_email = st.text_input("Email")
        if st.form_submit_button("Access Rx Assistant Pro"):
            if user_name and user_email:
                try:
                    p_key = os.environ.get("PRIVATE_KEY") or os.environ.get("private_key")
                    c_email = os.environ.get("CLIENT_EMAIL") or os.environ.get("client_email")
                    p_id = os.environ.get("PROJECT_ID") or os.environ.get("project_id")
                    s_id = os.environ.get("sheet_id") or os.environ.get("SHEET_ID")
                    
                    creds_dict = {
                        "type": "service_account",
                        "project_id": p_id,
                        "private_key": p_key.replace('\\n', '\n') if p_key else "",
                        "client_email": c_email,
                        "token_uri": "https://oauth2.googleapis.com/token",
                    }
                    client = gspread.authorize(Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]))
                    sheet = client.open_by_key(s_id).sheet1
                    sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_name, user_email])
                    
                    st.session_state.logged_in = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Registration Error: {e}")
            else:
                st.warning("Please enter your name and email.")
    st.stop() 

# ==========================================
# 🛡️ PROTECTED ZONE
# ==========================================

# 1. SIDEBAR BMI (Calculated first)
with st.sidebar:
    st.header("⚖️ BMI Calculator")
    f_val = st.number_input("Height (Feet)", 4, 8, 5, key="bmi_ft")
    i_val = st.number_input("Height (Inches)", 0, 11, 9, key="bmi_in")
    w_val = st.number_input("Weight (lbs)", 80, 500, 140, key="bmi_lb")
    
    total_inches = (f_val * 12) + i_val
    bmi = 0.0
    bmi_category = "Normal"
    if total_inches > 0:
        bmi = round((w_val / (total_inches ** 2)) * 703, 1)
        if bmi < 18.5: bmi_category = "Underweight"
        elif bmi < 25: bmi_category = "Normal"
        elif bmi < 30: bmi_category = "Overweight"
        else: bmi_category = "Obese"
    st.markdown(f"### BMI: **{bmi}** ({bmi_category})")
    st.markdown("---")
    st.caption("Rx Assistant Pro v10.0")

# 2. DEFINE TABS
tab1, tab2, tab3 = st.tabs(["🔍 Drug Decoder (FDA)", "💊 Multi-Med Combo Check", "🩺 Impairment Analyst (Conditions)"])

# 3. CALLBACKS
def fix_spelling_callback():
    if "suggestion" in st.session_state:
        st.session_state.single_input = st.session_state.suggestion

def clear_single(): st.session_state.single_input = ""
def clear_multi(): 
    st.session_state.combo_results = None
    st.session_state.multi_input_area = ""

# 4. CSS & FLOATING BOX
style_tags = """
<style>
.risk-high { background-color: #ffcccc; padding: 10px; border-radius: 5px; color: #8a0000; border-left: 5px solid #cc0000; }
.risk-med { background-color: #fff4cc; padding: 10px; border-radius: 5px; color: #664d00; border-left: 5px solid #ffcc00; }
.risk-safe { background-color: #e6fffa; padding: 10px; border-radius: 5px; color: #004d40; border-left: 5px solid #00bfa5; }
.rating-text { font-size: 0.95rem !important; font-weight: 600 !important; color: #E65100 !important; display: block; margin-top: 2px; }
div.stButton > button { width: 100%; }
.footer-link { text-align: center; margin-top: 20px; font-size: 14px; color: #888; }
.bmi-pointer { 
    position: fixed; top: 80px; left: 20px; z-index: 9999; 
    background-color: #0066cc; color: white; padding: 10px 15px; 
    border-radius: 8px; font-weight: bold; font-size: 16px; 
    box-shadow: 2px 2px 10px rgba(0,0,0,0.3); border: 1px solid white;
}
</style>
"""
st.markdown(style_tags, unsafe_allow_html=True)
st.markdown(f'<div class="bmi-pointer">⚖️ BMI: {bmi}</div>', unsafe_allow_html=True)

st.title("🛡️ Rx Assistant Pro")

# 5. DATA & LOGIC
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
    "Xanax", "Klonopin", "Ativan", "Ambien", "Lunesta", 
    "Viagra", "Cialis", "Levitra", "Allopurinol", "Colchicine", "Warfarin", 
    "Coumadin", "Digoxin", "Amiodarone", "Flecanide", "Sotalol", "Nitroglycerin",
    "Ranolazine", "Imdur", "Bisoprolol", "Carvedilol", "Labetalol"
]

def create_pdf(title, items_list, analysis_text, fda_text_content=None, matrix_data=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    def clean(text): return text.encode('latin-1', 'replace').decode('latin-1')
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=clean(f"Rx Assistant Pro - {title}"), ln=True, align='C')
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
    if matrix_data:
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="Product Suitability Matrix:", ln=True, align='L')
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(60, 8, "Category", 1); pdf.cell(40, 8, "Outlook", 1); pdf.cell(80, 8, "Note", 1); pdf.ln()
        pdf.set_font("Arial", size=10)
        for row in matrix_data:
            pdf.cell(60, 8, clean(row['Category']), 1)
            pdf.cell(40, 8, clean(row['Outlook']), 1)
            pdf.cell(80, 8, clean(row['Note']), 1)
            pdf.ln()
    if fda_text_content:
        pdf.ln(10); pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="Official FDA Indications (Excerpt):", ln=True, align='L')
        pdf.set_font("Arial", size=10); pdf.multi_cell(0, 6, txt=clean(fda_text_content[:2000] + "..."))
    return pdf.output(dest='S').encode('latin-1')

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

def get_product_matrix(risk_level):
    if risk_level == "risk-high":
        return [
            {"Category": "Term (10-30yr)", "Outlook": "❌ Poor", "Note": "Likely Decline"},
            {"Category": "Perm (IUL/UL/WL)", "Outlook": "⚠️ Fair", "Note": "Table 4 - 8"},
            {"Category": "Final Expense", "Outlook": "✅ Good", "Note": "Standard / Level"},
            {"Category": "Disability (DI)", "Outlook": "❌ Poor", "Note": "Auto-Decline"},
            {"Category": "Long-Term Care", "Outlook": "❌ Poor", "Note": "Decline"}
        ]
    elif risk_level == "risk-med":
        return [
            {"Category": "Term (10-30yr)", "Outlook": "⚠️ Fair", "Note": "Std to Table 2"},
            {"Category": "Perm (IUL/UL/WL)", "Outlook": "✅ Good", "Note": "Standard Likely"},
            {"Category": "Final Expense", "Outlook": "💎 Best", "Note": "Preferred"},
            {"Category": "Disability (DI)", "Outlook": "⚠️ Fair", "Note": "Table 2 / Excl."},
            {"Category": "Long-Term Care", "Outlook": "⚠️ Fair", "Note": "Rated / Wait"}
        ]
    else:
        return [
            {"Category": "Term (10-30yr)", "Outlook": "💎 Best", "Note": "Preferred / Std"},
            {"Category": "Perm (IUL/UL/WL)", "Outlook": "💎 Best", "Note": "Preferred / Std"},
            {"Category": "Final Expense", "Outlook": "💎 Best", "Note": "Preferred"},
            {"Category": "Disability (DI)", "Outlook": "✅ Good", "Note": "Standard"},
            {"Category": "Long-Term Care", "Outlook": "✅ Good", "Note": "Standard"}
        ]

IMPAIRMENT_DATA = {
    "Hypertension (High BP)": {"qs": ["Date of last reading?", "Is it controlled?", "Med change <12 mos?"], "rating": "Preferred (Controlled) to Table 2."},
    "Heart Attack (History of)": {"qs": ["Date of event?", "Current EF%?", "Recent stress test?"], "rating": "Postpone (0-6mos). Table 2 to 4 (After 1yr)."},
    "Atrial Fibrillation (AFib)": {"qs": ["Chronic or Paroxysmal?", "Blood thinners?", "Date last episode?"], "rating": "Standard (Infrequent) to Table 2."},
    "Stent Placement": {"qs": ["Date inserted?", "How many stents?", "Any chest pain since?"], "rating": "Table 2 (Single) to Table 4 (Multiple)."},
    "Coronary Artery Disease": {"qs": ["Date of diagnosis?", "Any bypass surgery?", "Current symptoms?"], "rating": "Table 2 to Decline."},
    "Stroke / TIA": {"qs": ["Date of event?", "Any residual weakness?", "Carotid ultrasound results?"], "rating": "Postpone (0-1yr). Table 4 to Decline."},
    "Diabetes Type 2": {"qs": ["Current A1C?", "Age of diagnosis?", "Insulin use?", "Neuropathy?"], "rating": "Standard (A1C<7) to Table 4 (Insulin)."},
    "Sleep Apnea": {"qs": ["CPAP use nightly?", "Compliance logs?", "Last sleep study?"], "rating": "Standard (Compliant). Table 2 to Decline (No CPAP)."},
    "COPD / Emphysema": {"qs": ["Oxygen use?", "Hospitalizations?", "Tobacco use?"], "rating": "Table 2 (Mild) to Decline (Severe/Smoker)."}
}

def check_comorbidities(selected_conditions, is_smoker, current_bmi):
    warnings = []
    if is_smoker: warnings.append("SMOKER STATUS: Rates will be Standard Smoker (Tobacco) at best.")
    if current_bmi > 30: warnings.append("BUILD RATING: High BMI typically triggers a Table Rating based on build alone.")
    if is_smoker:
        if "COPD / Emphysema" in selected_conditions: warnings.append("DECLINE WARNING: COPD + Smoking is a knockout.")
    return warnings

# --- TAB 1 LOGIC ---
with tab1:
    col_a, col_b = st.columns([4, 1])
    with col_a: st.markdown("### 🔍 Search by Medication Name")
    with col_b: st.button("🔄 Clear", on_click=clear_single, key="clear_1")
    single_drug = st.text_input("Enter Drug Name:", placeholder="e.g., Metformin", key="single_input")
    if single_drug:
        with st.spinner("Accessing FDA..."):
            try:
                url = f'https://api.fda.gov/drug/label.json?search=openfda.brand_name:"{single_drug}"+openfda.generic_name:"{single_drug}"&limit=1'
                r = requests.get(url)
                if r.status_code == 200:
                    data = r.json()['results'][0]
                    brand = data['openfda'].get('brand_name', [single_drug])[0]
                    indications = data.get('indications_and_usage', ["No text found"])[0]
                    insight = analyze_single_med(indications, brand)
                    st.success(f"**Found:** {brand}")
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        st.markdown(f"<div class='{insight['style']}'><b>Risk:</b><br>{insight['risk']}</div>", unsafe_allow_html=True)
                        st.markdown(f"<span class='rating-text'>📊 Est. Life Rating: {insight['rating']}</span>", unsafe_allow_html=True)
                        m_data = get_product_matrix(insight['style'])
                        report_text = [f"Risk: {insight['risk']}", f"Est. Life Rating: {insight['rating']}"] + [f"Ask: {q}" for q in insight['questions']]
                        pdf_data = create_pdf(f"Report - {brand}", [brand], report_text, fda_text_content=indications, matrix_data=m_data)
                        st.download_button("📄 Download PDF Report", data=pdf_data, file_name=f"{brand}_report.pdf", mime="application/pdf", key=f"pdf_btn_{brand}")
                    with c2:
                        st.markdown("#### ❓ Field Questions:")
                        for q in insight['questions']: st.write(f"✅ *{q}*")
                        st.markdown("#### 🎯 Product Suitability Matrix")
                        st.table(get_product_matrix(insight['style']))
                else:
                    matches = difflib.get_close_matches(single_drug, COMMON_DRUGS_LIST, n=1, cutoff=0.6)
                    st.error(f"❌ '{single_drug}' not found.")
                    if matches:
                        suggested_word = matches[0]
                        st.info(f"💡 Did you mean: **{suggested_word}**?")
                        st.session_state.suggestion = suggested_word
                        st.button(f"Yes, search for {suggested_word}", on_click=fix_spelling_callback, key="spell_check_btn")
            except Exception as e: st.error(f"Error: {e}")

# --- TAB 2 LOGIC ---
with tab2:
    col_x, col_y = st.columns([4, 1])
    with col_x: st.markdown("### 💊 Multi-Medication Combo Check")
    if col_y.button("🔄 Clear List", key="clear_combo_btn"):
        st.session_state.combo_results = None
        st.session_state.multi_input_area = ""
        st.rerun()
    multi_input = st.text_area("Paste Med List (comma separated):", key="multi_input_area", placeholder="Metformin, Lisinopril, Plavix")
    if st.button("Analyze Combinations", key="analyze_btn"):
        if multi_input:
            meds = [m.strip() for m in multi_input.split(',') if len(m.strip()) > 2]
            cats = []; valid_meds = []
            for med in meds:
                try:
                    url = f'https://api.fda.gov/drug/label.json?search=openfda.brand_name:"{med}"&limit=1'
                    r = requests.get(url)
                    if r.status_code == 200:
                        ind = r.json()['results'][0].get('indications_and_usage', [""])[0]
                        cat = simple_category_check(ind, med)
                        cats.append(cat); valid_meds.append(med)
                except: pass
            st.session_state.combo_results = {"combos": check_med_combinations(cats), "meds": valid_meds}
    if st.session_state.get("combo_results"):
        res = st.session_state.combo_results
        for m in res["meds"]: st.write(f"✅ **{m}** identified")
        if res["combos"]:
            for c in res["combos"]: st.error(c)
        else: st.success("No major negative combinations detected.")
        pdf_bytes = create_pdf("Multi-Med Analysis", res["meds"], res["combos"] if res["combos"] else ["No risks found."])
        st.download_button("📄 Download Combo Report", data=pdf_bytes, file_name="combo_report.pdf", mime="application/pdf", key="pdf_multi_persist")

# --- TAB 3 LOGIC ---
with tab3:
    st.markdown("### 🩺 Condition & Impairment Search")
    col_i1, col_i2 = st.columns(2)
    with col_i1:
        conditions = st.multiselect("Select Conditions:", sorted(list(IMPAIRMENT_DATA.keys())), key="cond_select")
    with col_i2:
        is_smoker = st.checkbox("🚬 Tobacco / Nicotine User", key="tobacco_user")
        st.write(f"⚖️ Current BMI: **{bmi}**")
    if conditions or is_smoker or bmi > 30:
        warnings = check_comorbidities(conditions, is_smoker, bmi)
        for w in warnings: st.error(w)
        pdf_lines = []
        if conditions:
            current_matrix = None
            for cond in conditions:
                data = IMPAIRMENT_DATA[cond]
                st.markdown(f"### {cond}")
                st.markdown(f"**Base Rating:** {data['rating']}")
                for q in data['qs']: st.write(f"✅ *{q}*")
                current_matrix = get_product_matrix("risk-med")
                st.table(current_matrix)
                pdf_lines.append(f"Condition: {cond} | Rating: {data['rating']}")
            imp_pdf_bytes = create_pdf("Impairment Analysis", conditions, pdf_lines, matrix_data=current_matrix)
            st.download_button("📄 Download Impairment Report", data=imp_pdf_bytes, file_name="imp_report.pdf", mime="application/pdf", key="pdf_imp_final")

# --- FOOTER ---
st.markdown("---")
with st.expander("⚠️ Legal Disclaimer"):
    st.write("Educational use only. Not medical advice.")
st.markdown("<div class='footer-link'>Powered by <a href='https://www.insurtechexpress.com' target='_blank'>InsurTech Express</a></div>", unsafe_allow_html=True)
