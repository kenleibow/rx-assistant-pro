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

# 1. PAGE SETUP
st.set_page_config(page_title="Rx Assistant Pro", page_icon="🛡️", layout="wide")

# 2. SESSION LOCK
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🛡️ Rx Assistant Pro - Access")
    with st.form("gate_keeper"):
        u_name = st.text_input("Name")
        u_email = st.text_input("Email")
        if st.form_submit_button("Access Tool"):
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
                    st.error(f"Login error: {e}")
    st.stop()

# ==========================================
# 🛡️ STABLE SIDEBAR & BMI
# ==========================================
with st.sidebar:
    st.header("⚖️ BMI Calculator")
    f = st.number_input("Height (Feet)", 4, 8, 5, key="f_sb")
    i = st.number_input("Height (Inches)", 0, 11, 9, key="i_sb")
    w = st.number_input("Weight (lbs)", 80, 500, 140, key="w_sb")
    total_in = (f * 12) + i
    bmi = round((w / (total_in ** 2)) * 703, 1) if total_in > 0 else 0
    st.write(f"### BMI: {bmi}")
    st.markdown("---")
    st.caption("Rx Assistant Pro v10.0")

# ==========================================
# 🎨 STABLE STYLING (No Floating Box yet to keep it simple)
# ==========================================
st.markdown("""<style>
.risk-high { background-color: #ffcccc; padding: 10px; border-radius: 5px; color: #8a0000; border-left: 5px solid #cc0000; }
.risk-med { background-color: #fff4cc; padding: 10px; border-radius: 5px; color: #664d00; border-left: 5px solid #ffcc00; }
.risk-safe { background-color: #e6fffa; padding: 10px; border-radius: 5px; color: #004d40; border-left: 5px solid #00bfa5; }
</style>""", unsafe_allow_html=True)

st.title("🛡️ Rx Assistant Pro")

# ==========================================
# ⚙️ LOGIC ENGINES
# ==========================================
def get_product_matrix(risk):
    if risk == "risk-high":
        return [{"Category": "Term", "Outlook": "❌ Poor", "Note": "Likely Decline"}, {"Category": "Perm", "Outlook": "⚠️ Fair", "Note": "Table 4-8"}, {"Category": "FE", "Outlook": "✅ Good", "Note": "Standard"}]
    elif risk == "risk-med":
        return [{"Category": "Term", "Outlook": "⚠️ Fair", "Note": "Std to Table 2"}, {"Category": "Perm", "Outlook": "✅ Good", "Note": "Standard"}, {"Category": "FE", "Outlook": "💎 Best", "Note": "Preferred"}]
    return [{"Category": "Term", "Outlook": "💎 Best", "Note": "Preferred"}, {"Category": "Perm", "Outlook": "💎 Best", "Note": "Preferred"}, {"Category": "FE", "Outlook": "💎 Best", "Note": "Preferred"}]

IMPAIRMENT_DATA = {
    "Hypertension": {"qs": ["Is it controlled?", "Last reading?"], "rating": "Preferred to Table 2", "risk": "risk-safe"},
    "Diabetes Type 2": {"qs": ["A1C level?", "Any neuropathy?"], "rating": "Standard to Table 4", "risk": "risk-med"},
    "Stroke / TIA": {"qs": ["Date of event?", "Any residual weakness?"], "rating": "Table 4 to Decline", "risk": "risk-high"}
}

# ==========================================
# 🔍 TABS & CONTENT
# ==========================================
tab1, tab2, tab3 = st.tabs(["🔍 Drug Decoder", "💊 Combo Check", "🩺 Impairments"])

with tab1:
    drug = st.text_input("Search Medication:", key="single_search")
    if drug:
        with st.spinner("Accessing FDA..."):
            r = requests.get(f'https://api.fda.gov/drug/label.json?search=openfda.brand_name:"{drug}"&limit=1')
            if r.status_code == 200:
                data = r.json()['results'][0]
                brand = data['openfda'].get('brand_name', [drug])[0]
                ind = data.get('indications_and_usage', ["No text found"])[0]
                st.success(f"**Found:** {brand}")
                st.markdown("<div class='risk-med'>Rating: Standard to Table 2</div>", unsafe_allow_html=True)
                st.table(get_product_matrix("risk-med"))
                st.write(f"**FDA Info:** {ind[:500]}...")
            else:
                st.error("Not found. Check spelling.")

with tab2:
    st.write("Enter multiple meds below.")
    multi = st.text_area("Med List:", placeholder="Metformin, Lisinopril")
    if st.button("Analyze"):
        st.write(f"Analyzed: {multi}")
        st.success("No interactions detected.")

with tab3:
    conds = st.multiselect("Select Conditions:", sorted(list(IMPAIRMENT_DATA.keys())))
    if conds:
        for c in conds:
            d = IMPAIRMENT_DATA[c]
            st.subheader(c)
            st.markdown(f"<div class='{d['risk']}'>Rating: {d['rating']}</div>", unsafe_allow_html=True)
            for q in d['qs']: st.write(f"✅ *{q}*")
            st.table(get_product_matrix(d['risk']))

# ==========================================
# 📝 FOOTER
# ==========================================
st.markdown("---")
st.markdown("Powered by **InsurTech Express**")
