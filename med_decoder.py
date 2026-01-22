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
                    # Connect to Google
                    creds_dict = st.secrets["gcp_service_account"]
                    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
                    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
                    client = gspread.authorize(creds)
                    
                    # Log the login
                    sheet = client.open("Rx_Login_Tracker").sheet1
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    sheet.append_row([current_time, user_name, user_email])

                    # Unlock app
                    st.session_state.logged_in = True
                    st.rerun()

                except Exception as e:
                    st.error(f"🚨 Connection Error: {e}")

    # STOP ONLY FOR UNAUTHORIZED USERS
    st.stop()

# =========================================================
#  APP CONTENT (REACHED ONLY IF LOGGED IN)
# =========================================================

# --- CALLBACKS ---
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
    </style>
    <div class="bmi-pointer">BMI Calculator</div>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚖️ BMI Calculator")
    feet = st.number_input("Height (Feet)", 4, 8, 5)
    inches = st.number_input("Height (Inches)", 0, 11, 9)
    weight = st.number_input("Weight (lbs)", 80, 500, 140)
    total_inches = (feet * 12) + inches
    bmi = round((weight / (total_inches ** 2)) * 703, 1) if total_inches > 0 else 0.0
    bmi_category = "Normal"
    if bmi < 18.5: st.info(f"BMI: {bmi}"); bmi_category="Underweight"
    elif bmi < 25: st.success(f"BMI: {bmi}"); bmi_category="Normal"
    elif bmi < 30: st.warning(f"BMI: {bmi}"); bmi_category="Overweight"
    else: st.error(f"BMI: {bmi}"); bmi_category="Obese"

# --- PDF GENERATOR (THE MISSING PIECE) ---
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
    pdf.cell(200, 10, txt="Analysis Results:", ln=True, align='L')
    pdf.set_font("Arial", size=12)
    if isinstance(analysis_text, list):
        for line in analysis_text: pdf.multi_cell(0, 10, txt=clean(f"- {line}"))
    else: pdf.multi_cell(0, 10, txt=clean(analysis_text))
    return pdf.output(dest='S').encode('latin-1')

# --- LOGIC ENGINES ---
def analyze_single_med(indication_text, brand_name):
    name = brand_name.lower()
    if "metformin" in name: return {"risk": "Diabetes Type 2", "style": "risk-med", "questions": ["Is this for Pre-Diabetes or Type 2?", "What is your A1C?"], "rating": "Standard to Table 2."}
    elif "lisinopril" in name or "amlodipine" in name: return {"risk": "Hypertension", "style": "risk-safe", "questions": ["Is BP controlled?"], "rating": "Preferred."}
    return {"risk": "Maintenance", "style": "risk-safe", "questions": ["Why was this prescribed?"], "rating": "Depends on condition."}

# ==========================================
# 🚀 MAIN APP LAYOUT
# ==========================================
st.title("🛡️ Life Insurance Rx Assistant")

tab1, tab2, tab3 = st.tabs(["🔍 Drug Decoder", "💊 Multi-Med Check", "🩺 Impairments"])

with tab1:
    single_drug = st.text_input("Enter Medication Name:", key="single_input")
    if single_drug:
        try:
            url = f'https://api.fda.gov/drug/label.json?search=openfda.brand_name:"{single_drug}"&limit=1'
            r = requests.get(url)
            if r.status_code == 200:
                data = r.json()['results'][0]
                brand = data['openfda'].get('brand_name', [single_drug])[0]
                indications = data.get('indications_and_usage', ["No text found"])[0]
                insight = analyze_single_med(indications, brand)
                
                st.success(f"**Found:** {brand}")
                st.markdown(f"<div class='{insight['style']}'><b>Risk:</b> {insight['risk']}</div>", unsafe_allow_html=True)
                for q in insight['questions']: st.write(f"✅ {q}")
                
                # PDF BUTTON
                rep_text = [f"Risk: {insight['risk']}", f"Rating: {insight['rating']}"] + insight['questions']
                pdf_data = create_pdf(brand, [brand], rep_text)
                st.download_button("📄 Download PDF Report", data=pdf_data, file_name=f"{brand}_report.pdf", key=f"pdf_{brand}")
        except Exception as e: st.error(f"Error: {e}")

with tab2:
    st.write("Multi-Med logic active.")

with tab3:
    st.write("Impairment logic active.")

# --- FOOTER ---
st.markdown("---")
st.markdown("<div class='footer-link'>Powered by <a href='https://www.insurtechexpress.com'>InsurTech Express</a></div>", unsafe_allow_html=True)
