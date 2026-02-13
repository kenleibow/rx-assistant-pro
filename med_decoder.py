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

# 1. MUST BE FIRST
st.set_page_config(page_title="Rx Assistant Pro", page_icon="🛡️", layout="wide")

# 2. SESSION INITIALIZATION (The Shield)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "combo_results" not in st.session_state:
    st.session_state.combo_results = None

# 3. REGISTRATION GATE (Hard Wall)
if not st.session_state.logged_in:
    st.title("🛡️ Rx Assistant Pro - Access")
    with st.form("gate"):
        u_name = st.text_input("Full Name")
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
                    st.error(f"Login Error: {e}")
    st.stop()

# ==========================================
# PROTECTED APP ZONE (Reached only if logged in)
# ==========================================

# 4. SIDEBAR BMI
with st.sidebar:
    st.header("⚖️ BMI Calculator")
    f = st.number_input("Feet", 4, 8, 5, key="f_in")
    i = st.number_input("Inches", 0, 11, 9, key="i_in")
    w = st.number_input("Weight (lbs)", 80, 500, 140, key="w_in")
    bmi = round((w / (((f * 12) + i) ** 2)) * 703, 1) if ((f * 12) + i) > 0 else 0
    st.write(f"**BMI: {bmi}**")

# 5. UI STYLING (The Blue Box and Risk Colors)
st.markdown(f"""
    <style>
    .bmi-pointer {{ 
        position: fixed; top: 70px; left: 10px; z-index: 9999; 
        background-color: #0066cc; color: white; padding: 8px 12px; 
        border-radius: 5px; font-weight: bold; font-size: 14px; border: 1px solid white;
    }}
    .risk-high {{ background-color: #ffcccc; padding: 10px; border-radius: 5px; color: #8a0000; border-left: 5px solid #cc0000; }}
    .risk-med {{ background-color: #fff4cc; padding: 10px; border-radius: 5px; color: #664d00; border-left: 5px solid #ffcc00; }}
    .risk-safe {{ background-color: #e6fffa; padding: 10px; border-radius: 5px; color: #004d40; border-left: 5px solid #00bfa5; }}
    </style>
    <div class="bmi-pointer">⚖️ BMI: {bmi}</div>
""", unsafe_allow_html=True)

st.title("🛡️ Rx Assistant Pro")

# 6. APP CONTENT
tab1, tab2, tab3 = st.tabs(["🔍 Drug Decoder", "💊 Combo Check", "🩺 Impairments"])

with tab1:
    drug = st.text_input("Enter Medication:", key="single_input")
    if drug:
        st.info(f"Searching FDA for {drug}...")
        # (FDA Logic here...)

with tab2:
    meds_raw = st.text_area("Med List (comma separated):", key="multi_input")
    if st.button("Analyze"):
        st.session_state.combo_results = ["Checking combinations..."]
    if st.session_state.combo_results:
        st.write(st.session_state.combo_results)

with tab3:
    st.write(f"Analyzing for BMI: {bmi}")
    # (Impairment logic here...)

st.markdown("---")
st.caption("Powered by InsurTech Express")
