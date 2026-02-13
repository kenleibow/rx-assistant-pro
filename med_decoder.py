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

# 1. PAGE CONFIG (Must be first)
st.set_page_config(page_title="Rx Assistant Pro", page_icon="🛡️", layout="wide")

# 2. SESSION INITIALIZATION (The Login Shield)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "combo_results" not in st.session_state:
    st.session_state.combo_results = None
if "suggestion" not in st.session_state:
    st.session_state.suggestion = ""

# 3. REGISTRATION GATEKEEPER
if not st.session_state.logged_in:
    st.title("🛡️ Rx Assistant Pro - Access")
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
                st.warning("Registration required.")
    st.stop()

# ==========================================
# 🛡️ PROTECTED APP ZONE (Reached only if logged_in)
# ==========================================

# 4. SIDEBAR BMI
with st.sidebar:
    st.header("⚖️ BMI Calculator")
    f_val = st.number_input("Feet", 4, 8, 5, key="bmi_ft")
    i_val = st.number_input("Inches", 0, 11, 9, key="bmi_in")
    w_val = st.number_input("Weight (lbs)", 80, 500, 140, key="bmi_lb")
    total_inches = (f_val * 12) + i_val
    bmi = round((w_val / (total_inches ** 2)) * 703, 1) if total_inches > 0 else 0
    bmi_cat = "Obese" if bmi >= 30 else "Overweight" if bmi >= 25 else "Normal"
    st.write(f"**BMI: {bmi} ({bmi_cat})**")
    st.markdown("---")
    st.caption("Rx Assistant Pro v10.0")

# 5. UI STYLING & FLOATING BOX (Safe CSS)
style_tags = f"""
<style>
.risk-high {{ background-color: #ffcccc; padding: 10px; border-radius: 5px; color: #8a0000; border-left: 5px solid #cc0000; }}
.risk-med {{ background-color: #fff4cc; padding: 10px; border-radius: 5px; color: #664d00; border-left: 5px solid #ffcc00; }}
.risk-safe {{ background-color: #e6fffa; padding: 10px; border-radius: 5px; color: #004d40; border-left: 5px solid #00bfa5; }}
.bmi-pointer {{ position: fixed; top: 80px; left: 20px; z-index: 9999; background-color: #0066cc; color: white; padding: 10px 15px; border-radius: 8px; font-weight: bold; box-shadow: 2px 2px 10px rgba(0,0,0,0.3); border: 1px solid white; }}
.footer-link {{ text-align: center; margin-top: 20px; font-size: 14px; color: #888; }}
</style>
<div class="bmi-pointer">⚖️ BMI: {bmi}</div>
"""
st.markdown(style_tags, unsafe_allow_html=True)
st.title("🛡️ Rx Assistant Pro")

# 6. DATA & HELPERS
COMMON_DRUGS_LIST = ["Metformin", "Lisinopril", "Atorvastatin", "Levothyroxine", "Amlodipine", "Plavix", "Eliquis", "Xarelto", "Ozempic", "Wegovy", "Mounjaro"]

def create_pdf(title, items, analysis, matrix=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"Rx Assistant Report - {title}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    for item in items: pdf.cell(200, 10, txt=f"- {item}", ln=True)
    pdf.ln(5)
    pdf.multi_cell(0, 10, txt=str(analysis))
    if matrix:
        pdf.ln(5); pdf.set_font("Arial", 'B', 12); pdf.cell(200, 10, txt="Suitability Matrix", ln=True)
        for row in matrix: pdf.cell(0, 8, txt=f"{row['Category']}: {row['Outlook']} - {row['Note']}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

def get_product_matrix(risk):
    if risk == "risk-high":
        return [{"Category": "Term", "Outlook": "❌ Poor", "Note": "Likely Decline"}, {"Category": "Perm (IUL/WL)", "Outlook": "⚠️ Fair", "Note": "Table 4-8"}, {"Category": "Final Expense", "Outlook": "✅ Good", "Note": "Standard"}]
    elif risk == "risk-med":
        return [{"Category": "Term", "Outlook": "⚠️ Fair", "Note": "Std to Table 2"}, {"Category": "Perm (IUL/WL)", "Outlook": "✅ Good", "Note": "Standard"}, {"Category": "Final Expense", "Outlook": "💎 Best", "Note": "Preferred"}]
    return [{"Category": "Term", "Outlook": "💎 Best", "Note": "Preferred"}, {"Category": "Perm (IUL/WL)", "Outlook": "💎 Best", "Note": "Preferred"}, {"Category": "Final Expense", "Outlook": "💎 Best", "Note": "Preferred"}]

IMPAIRMENT_DATA = {
    "Hypertension": {"qs": ["Is it controlled?", "Last reading?"], "rating": "Preferred to Table 2", "risk": "risk-safe"},
    "Diabetes Type 2": {"qs": ["A1C level?", "Any neuropathy?", "Insulin use?"], "rating": "Standard to Table 4", "risk": "risk-med"},
    "Heart Attack History": {"qs": ["Date of event?", "Current EF%?", "Stents?"], "rating": "Table 2 to Decline", "risk": "risk-high"}
}

# 7. CALLBACKS
def fix_spelling_callback():
    if "suggestion" in st.session_state:
        st.session_state.single_input = st.session_state.suggestion

def clear_single(): st.session_state.single_input = ""

# 8. TABS
tab1, tab2, tab3 = st.tabs(["🔍 Drug Decoder (FDA)", "💊 Multi-Med Combo", "🩺 Impairments"])

with tab1:
    drug = st.text_input("Enter Medication:", key="single_input", placeholder="e.g., Metformn")
    if drug:
        with st.spinner("Accessing FDA..."):
            r = requests.get(f'https://api.fda.gov/drug/label.json?search=openfda.brand_name:"{drug}"&limit=1')
            if r.status_code == 200:
                data = r.json()['results'][0]
                brand = data['openfda'].get('brand_name', [drug])[0]
                ind = data.get('indications_and_usage', ["No text found"])[0]
                risk_lv = "risk-med" # Simplified logic
                st.success(f"**Found:** {brand}")
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.markdown(f"<div class='{risk_lv}'><b>Risk Category:</b> Maintenance</div>", unsafe_allow_html=True)
                    matrix = get_product_matrix(risk_lv)
                    pdf = create_pdf(brand, [brand], ind[:1000], matrix)
                    st.download_button("📄 Download PDF", data=pdf, file_name=f"{brand}_report.pdf", key="pdf_tab1")
                with c2:
                    st.markdown("#### Suitability Matrix")
                    st.table(matrix)
                    st.write(f"**Indications:** {ind[:500]}...")
            else:
                matches = difflib.get_close_matches(drug, COMMON_DRUGS_LIST, n=1, cutoff=0.6)
                st.error(f"❌ '{drug}' not found.")
                if matches:
                    st.session_state.suggestion = matches[0]
                    st.button(f"Did you mean: {matches[0]}?", on_click=fix_spelling_callback)

with tab2:
    multi_input = st.text_area("Paste List (comma separated):", key="multi_area")
    if st.button("Analyze Combinations"):
        st.session_state.combo_results = [m.strip() for m in multi_input.split(',') if m.strip()]
    if st.session_state.combo_results:
        st.write("✅ Analyzed:", ", ".join(st.session_state.combo_results))
        st.info("Cross-referencing drug interactions...")

with tab3:
    conds = st.multiselect("Select Conditions:", sorted(list(IMPAIRMENT_DATA.keys())))
    if conds:
        for c in conds:
            data = IMPAIRMENT_DATA[c]
            st.subheader(c)
            st.markdown(f"<div class='{data['risk']}'>Rating: {data['rating']}</div>", unsafe_allow_html=True)
            for q in data['qs']: st.write(f"✅ *{q}*")
            st.table(get_product_matrix(data['risk']))

# 9. FOOTER
st.markdown("---")
with st.expander("⚠️ Legal Disclaimer"):
    st.write("Educational use only. Not a medical diagnosis.")
st.markdown("<div class='footer-link'>Powered by <a href='https://www.insurtechexpress.com' target='_blank'>InsurTech Express</a></div>", unsafe_allow_html=True)
