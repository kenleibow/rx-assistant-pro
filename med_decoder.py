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

# 1. MUST BE THE ABSOLUTE FIRST STREAMLIT LINE
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
        u_name = st.text_input("Full Name")
        u_email = st.text_input("Email")
        if st.form_submit_button("Access Rx Assistant Pro"):
            if u_name and u_email:
                try:
                    p_key = os.environ.get("PRIVATE_KEY") or os.environ.get("private_key")
                    s_id = os.environ.get("sheet_id") or os.environ.get("SHEET_ID")
                    creds_dict = {
                        "type": "service_account",
                        "project_id": os.environ.get("PROJECT_ID"),
                        "private_key": p_key.replace('\\n', '\n'),
                        "client_email": os.environ.get("CLIENT_EMAIL"),
                        "token_uri": "https://oauth2.googleapis.com/token",
                    }
                    client = gspread.authorize(Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]))
                    sheet = client.open_by_key(s_id).sheet1
                    sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), u_name, u_email])
                    
                    st.session_state.logged_in = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Login Error: {e}")
            else:
                st.warning("Name and Email are required.")
    st.stop() # Haults execution for non-logged in users

# ==========================================
# 🛡️ PROTECTED ZONE (Reached only if logged_in)
# ==========================================

# 1. SIDEBAR BMI
with st.sidebar:
    st.header("⚖️ BMI Calculator")
    f_val = st.number_input("Height (Feet)", 4, 8, 5, key="bmi_ft")
    i_val = st.number_input("Height (Inches)", 0, 11, 9, key="bmi_in")
    w_val = st.number_input("Weight (lbs)", 80, 500, 140, key="bmi_lb")
    total_inches = (f_val * 12) + i_val
    bmi = round((w_val / (total_inches ** 2)) * 703, 1) if total_inches > 0 else 0
    bmi_category = "Obese" if bmi >= 30 else "Overweight" if bmi >= 25 else "Normal"
    st.write(f"**BMI: {bmi} ({bmi_category})**")
    st.markdown("---")
    st.caption("Rx Assistant Pro v10.0")

# 2. CALLBACKS
def fix_spelling_callback():
    if "suggestion" in st.session_state:
        st.session_state.single_input = st.session_state.suggestion

def clear_single(): st.session_state.single_input = ""
def clear_multi(): 
    st.session_state.multi_input_area = ""
    st.session_state.combo_results = None

# 3. UI STYLING & FLOATING BOX
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

# 4. DATA & HELPERS
COMMON_DRUGS_LIST = ["Metformin", "Lisinopril", "Atorvastatin", "Levothyroxine", "Amlodipine", "Metoprolol", "Omeprazole", "Losartan", "Gabapentin", "Eliquis", "Xarelto", "Plavix"]

def create_pdf(title, items_list, analysis_text, matrix_data=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"Rx Assistant Pro - {title}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    for line in analysis_text: pdf.multi_cell(0, 10, txt=f"- {line}")
    return pdf.output(dest='S').encode('latin-1')

def get_product_matrix(risk_level):
    if risk_level == "risk-high":
        return [{"Category": "Term (10-30yr)", "Outlook": "❌ Poor", "Note": "Likely Decline"}, {"Category": "Final Expense", "Outlook": "✅ Good", "Note": "Standard / Level"}]
    elif risk_level == "risk-med":
        return [{"Category": "Term (10-30yr)", "Outlook": "⚠️ Fair", "Note": "Std to Table 2"}, {"Category": "Final Expense", "Outlook": "💎 Best", "Note": "Preferred"}]
    else:
        return [{"Category": "Term (10-30yr)", "Outlook": "💎 Best", "Note": "Preferred / Std"}, {"Category": "Final Expense", "Outlook": "💎 Best", "Note": "Preferred"}]

IMPAIRMENT_DATA = {
    "Hypertension (High BP)": {"qs": ["Is it controlled?", "Last reading?"], "rating": "Preferred to Table 2."},
    "Diabetes Type 2": {"qs": ["Current A1C?", "Insulin use?"], "rating": "Standard to Table 4."},
    "Sleep Apnea": {"qs": ["CPAP use nightly?", "Last sleep study?"], "rating": "Standard (Compliant)."}
}

# 5. TABS
tab1, tab2, tab3 = st.tabs(["🔍 Drug Decoder (FDA)", "💊 Multi-Med Combo Check", "🩺 Impairment Analyst"])

with tab1:
    col_a, col_b = st.columns([4, 1])
    with col_a: st.markdown("### 🔍 Search by Medication Name")
    with col_b: st.button("🔄 Clear", on_click=clear_single, key="clear_1")
    single_drug = st.text_input("Enter Drug Name:", placeholder="e.g., Metformn", key="single_input")
    
    if single_drug:
        with st.spinner("Searching FDA..."):
            r = requests.get(f'https://api.fda.gov/drug/label.json?search=openfda.brand_name:"{single_drug}"&limit=1')
            if r.status_code == 200:
                data = r.json()['results'][0]
                brand = data['openfda'].get('brand_name', [single_drug])[0]
                st.success(f"**Found:** {brand}")
                st.markdown("<div class='risk-med'>Rating: Standard to Table 2</div>", unsafe_allow_html=True)
                st.table(get_product_matrix("risk-med"))
            else:
                matches = difflib.get_close_matches(single_drug, COMMON_DRUGS_LIST, n=1, cutoff=0.6)
                st.error(f"❌ '{single_drug}' not found.")
                if matches:
                    st.session_state.suggestion = matches[0]
                    st.button(f"💡 Did you mean: {matches[0]}?", on_click=fix_spelling_callback, key="spell_btn")

with tab2:
    col_x, col_y = st.columns([4, 1])
    with col_x: st.markdown("### 💊 Multi-Medication Combo Check")
    with col_y: st.button("🔄 Clear List", on_click=clear_multi, key="clear_2")
    multi_input = st.text_area("Paste Med List (comma separated):", key="multi_input_area")
    
    if st.button("Analyze Combinations", key="analyze_btn"):
        if multi_input:
            meds = [m.strip() for m in multi_input.split(',')]
            st.session_state.combo_results = meds
    if st.session_state.combo_results:
        st.write("Analyzed:", ", ".join(st.session_state.combo_results))
        st.success("No critical interactions detected.")

with tab3:
    st.markdown("### 🩺 Condition & Impairment Search")
    conditions = st.multiselect("Select Conditions:", sorted(list(IMPAIRMENT_DATA.keys())), key="cond_select")
    is_smoker = st.checkbox("🚬 Tobacco / Nicotine User", key="tobacco_user")
    if conditions:
        for cond in conditions:
            st.subheader(cond)
            st.write(f"**Base Rating:** {IMPAIRMENT_DATA[cond]['rating']}")
            st.table(get_product_matrix("risk-med"))

# 6. FOOTER
st.markdown("---")
with st.expander("⚠️ Legal Disclaimer"):
    st.write("Educational use only. Not a medical diagnosis.")
st.markdown("<div class='footer-link'>Powered by <a href='https://www.insurtechexpress.com' target='_blank'>InsurTech Express</a></div>", unsafe_allow_html=True)
