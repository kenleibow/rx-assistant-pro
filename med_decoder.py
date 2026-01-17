import streamlit as st
import requests
from fpdf import FPDF

# --- CONFIGURATION ---
st.set_page_config(page_title="Rx Field Assistant", page_icon="🛡️", layout="wide")

# --- CSS STYLING ---
st.markdown("""
    <style>
    .risk-high { background-color: #ffcccc; padding: 10px; border-radius: 5px; color: #8a0000;}
    .risk-med { background-color: #fff4cc; padding: 10px; border-radius: 5px; color: #664d00;}
    .risk-safe { background-color: #e6fffa; padding: 10px; border-radius: 5px; color: #004d40;}
    div.stButton > button { width: 100%; }
    .footer-text { font-size: 12px; color: #666; }
    </style>
    """, unsafe_allow_html=True)

# =========================================================
#  NEW FEATURE: BMI CALCULATOR SIDEBAR
# =========================================================
with st.sidebar:
    st.header("⚖️ BMI Calculator")
    st.markdown("Quick check for height/weight knockouts.")
    
    feet = st.number_input("Height (Feet)", min_value=4, max_value=8, value=5)
    inches = st.number_input("Height (Inches)", min_value=0, max_value=11, value=9)
    weight = st.number_input("Weight (lbs)", min_value=80, max_value=500, value=180)
    
    # Calculate
    total_inches = (feet * 12) + inches
    if total_inches > 0:
        bmi = (weight / (total_inches ** 2)) * 703
        bmi = round(bmi, 1)
        
        # Color Code BMI
        if bmi < 18.5:
            st.info(f"BMI: {bmi} (Underweight)")
        elif 18.5 <= bmi < 25:
            st.success(f"BMI: {bmi} (Normal)")
        elif 25 <= bmi < 30:
            st.warning(f"BMI: {bmi} (Overweight)")
        elif 30 <= bmi < 40:
            st.error(f"BMI: {bmi} (Obese)")
        else:
            st.error(f"BMI: {bmi} (Morbidly Obese - Check Tables)")
    
    st.markdown("---")
    st.caption("Rx Field Assistant v6.2")

st.title("🛡️ Life Insurance Rx Assistant")

# --- NEW FEATURE: PDF GENERATOR ---
def create_pdf(med_list, risk_notes, fda_text_content=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Rx Assistant - Case Report", ln=True, align='C')
    pdf.ln(10)
    
    # Meds
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Medications Analyzed:", ln=True, align='L')
    pdf.set_font("Arial", size=12)
    
    for med in med_list:
        pdf.cell(200, 10, txt=f"- {med}", ln=True, align='L')
    pdf.ln(5)
    
    # Risks
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Risk Analysis:", ln=True, align='L')
    pdf.set_font("Arial", size=12)
    
    if risk_notes:
        for note in risk_notes:
            # Check format of note (dictionary vs string) to prevent errors
            if isinstance(note, dict):
                title = note.get('title', 'Alert')
                desc = note.get('desc', '')
                text_line = f"ALERT: {title} - {desc}"
            else:
                text_line = f"ALERT: {note}"
                
            pdf.set_text_color(194, 24, 7) # Red-ish
            pdf.multi_cell(0, 10, txt=text_line)
            pdf.set_text_color(0, 0, 0)
    else:
        pdf.cell(200, 10, txt="No major negative factors detected.", ln=True)
    
    pdf.ln(10)

    # FDA Text Section
    if fda_text_content:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="Official FDA Indications (Excerpt):", ln=True, align='L')
        pdf.set_font("Arial", size=10) 
        # Clean text to prevent PDF errors
        clean_text = fda_text_content.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 6, txt=clean_text[:2000] + "...") 
        
    return pdf.output(dest='S').encode('latin-1')

# --- CLEAR FUNCTIONS ---
def clear_single():
    st.session_state["single_input"] = ""

def clear_multi():
    st.session_state["multi_input"] = ""

# --- CREATE TABS ---
tab1, tab2 = st.tabs(["🔍 Single Med Decoder (Deep Dive)", "💊 Multi-Med Analyzer (Combinations)"])

# =========================================================
#  LOGIC ENGINE 1: SINGLE MEDICATION (YOUR ORIGINAL CODE)
# =========================================================
def analyze_single_med(indication_text, brand_name):
    text = indication_text.lower()
    name = brand_name.lower()
    
    # 1. HARDCODED CHEAT SHEET
    if "metformin" in name:
        return {
            "risk": "Diabetes Type 2",
            "style": "risk-med",
            "questions": ["Is this for Pre-Diabetes or Type 2?", "What is your A1C?", "Any neuropathy?"],
            "rating": "Standard (if A1C < 7.0) to Table 2."
        }
    elif "lisinopril" in name or "amlodipine" in name:
        return {
            "risk": "Hypertension (High BP)",
            "style": "risk-safe",
            "questions": ["Is BP controlled?", "Last reading?", "Do you take >2 BP meds?"],
            "rating": "Preferred Best possible."
        }
    elif "plavix" in name or "clopidogrel" in name:
        return {
            "risk": "Heart Disease / Stroke",
            "style": "risk-high",
            "questions": ["History of TIA/Stroke?", "Stent placement?", "Preventative or active treatment?"],
            "rating": "Standard to Decline."
        }
    elif "abilify" in name or "aripiprazole" in name:
        return {
            "risk": "Bipolar / Depression / Schizophrenia",
            "style": "risk-high",
            "questions": ["Hospitalizations in last 5 years?", "Suicide attempts?", "Ability to work?"],
            "rating": "Complex. Mild = Standard. Bipolar = Table Rating."
        }
    elif "entresto" in name:
        return {
            "risk": "Heart Failure (CHF)",
            "style": "risk-high",
            "questions": ["What is your Ejection Fraction?", "Any hospitalizations recently?"],
            "rating": "Likely Decline or High Table Rating."
        }

    # 2. KEYWORD SEARCH
    risk_keywords = {
        "metastatic": "Cancer (Severe)",
        "chemotherapy": "Cancer Treatment",
        "hiv": "HIV/AIDS",
        "dementia": "Cognitive Decline"
    }
    
    for word, risk in risk_keywords.items():
        if word in text:
            return {
                "risk": f"FLAGGED: {risk}",
                "style": "risk-high",
                "questions": ["Ask: Specific diagnosis date?", "Ask: Current treatment status?"],
                "rating": "Likely Rated or Decline."
            }

    # 3. DEFAULT
    return {
        "risk": "General / Maintenance",
        "style": "risk-safe",
        "questions": ["Why was this prescribed?", "Any symptoms currently?"],
        "rating": "Depends on underlying condition."
    }

# =========================================================
#  LOGIC ENGINE 2: MULTI MED (YOUR ORIGINAL CODE)
# =========================================================
def check_combinations(found_categories):
    unique_cats = set(found_categories)
    insights = []
    
    if "Diabetes" in unique_cats and "Hypertension" in unique_cats and "Cholesterol" in unique_cats:
        insights.append({"title": "METABOLIC SYNDROME", "desc": "Client has the 'Trifecta'. Look for carriers with Metabolic Syndrome credits."})
    elif "Diabetes" in unique_cats and "Cardiac" in unique_cats:
        insights.append({"title": "HIGH RISK: DIABETES + HEART", "desc": "Compounded mortality risk. Expect Table 4+ or Decline."})
        
    return insights

def simple_category_check(text, name):
    t = text.lower(); n = name.lower()
    if "diabetes" in t or "metformin" in n: return "Diabetes"
    if "hypertension" in t or "lisinopril" in n: return "Hypertension"
    if "cholesterol" in t or "statin" in n: return "Cholesterol"
    if "heart failure" in t or "plavix" in n: return "Cardiac"
    return "Other"

# =========================================================
#  TAB 1 CONTENT: SINGLE LOOKUP
# =========================================================
with tab1:
    col_a, col_b = st.columns([4, 1])
    with col_a:
        st.markdown("### 🔍 Single Drug Deep Dive")
    with col_b:
        st.button("🔄 New Case", on_click=clear_single, key="btn_clear_single")

    single_drug = st.text_input("Enter Drug Name:", placeholder="e.g., Abilify", key="single_input")
    
    if single_drug:
        with st.spinner("Decoding..."):
            try:
                url = f'https://api.fda.gov/drug/label.json?search=openfda.brand_name:"{single_drug}"+openfda.generic_name:"{single_drug}"&limit=1'
                r = requests.get(url)
                if r.status_code == 200:
                    data = r.json()['results'][0]
                    brand = data['openfda'].get('brand_name', [single_drug])[0]
                    indications = data.get('indications_and_usage', ["No text found"])[0]
                    
                    insight = analyze_single_med(indications, single_drug)
                    
                    st.success(f"**Found:** {brand}")
                    
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.markdown(f"<div class='{insight['style']}'><b>Suspected Risk:</b><br>{insight['risk']}</div>", unsafe_allow_html=True)
                        st.caption(f"Rating Impact: {insight['rating']}")
                    with col2:
                        st.markdown("**❓ Essential Field Questions:**")
                        for q in insight['questions']:
                            st.write(f"✅ *{q}*")
                            
                    with st.expander("Show Official FDA Text"):
                        st.write(indications)

                    st.markdown("---")
                    # PDF Logic
                    single_risk_note = [{"title": insight['risk'], "desc": f"Rating: {insight['rating']}"}]
                    pdf_bytes = create_pdf([brand], single_risk_note, fda_text_content=indications)
                    
                    st.download_button(
                        label="📄 Download Report (PDF)",
                        data=pdf_bytes,
                        file_name=f"{brand}_report.pdf",
                        mime="application/pdf"
                    )

                else:
                    st.error("Drug not found. Check spelling.")
            except:
                st.error("Connection Error or API unavailable.")

# =========================================================
#  TAB 2 CONTENT: MULTI ANALYZER
# =========================================================
with tab2:
    col_x, col_y = st.columns([4, 1])
    with col_x:
        st.markdown("### 💊 Multi-Medication Analyzer")
    with col_y:
        st.button("🔄 New Case", on_click=clear_multi, key="btn_clear_multi")
    
    st.markdown("Paste a list to check for **Dangerous Combinations** (Triads).")
    
    multi_input = st.text_area("List Meds (comma separated):", height=100, 
                              placeholder="Metformin, Lisinopril, Atorvastatin", key="multi_input")
    
    if st.button("Analyze Combinations"):
        if multi_input:
            meds = [m.strip() for m in multi_input.split(',')]
            categories = []
            found_meds_list = []

            for med in meds:
                if len(med) < 3: continue
                try:
                    url = f'https://api.fda.gov/drug/label.json?search=openfda.brand_name:"{med}"+openfda.generic_name:"{med}"&limit=1'
                    r = requests.get(url)
                    if r.status_code == 200:
                        data = r.json()['results'][0]
                        ind = data.get('indications_and_usage', [""])[0]
                        cat = simple_category_check(ind, med)
                        categories.append(cat)
                        found_meds_list.append(med)
                        st.write(f"✅ **{med}** identified as *{cat}*")
                    else:
                        st.write(f"❌ **{med}** not found")
                except:
                    pass
            
            combos = check_combinations(categories)
            if combos:
                st.divider()
                for c in combos:
                    st.error(f"**{c['title']}**\n\n{c['desc']}")
            else:
                st.success("No major negative combinations detected.")

            st.markdown("---")
            if found_meds_list:
                pdf_bytes = create_pdf(found_meds_list, combos)
                st.download_button(
                    label="📄 Download Case PDF",
                    data=pdf_bytes,
                    file_name="client_med_report.pdf",
                    mime="application/pdf"
                )

# =========================================================
#  LEGAL DISCLAIMER (FOOTER)
# =========================================================
st.markdown("---")
with st.expander("⚠️ Legal Disclaimer & Liability Information"):
    st.markdown("""
    **Educational Use Only**
    This tool is designed to assist insurance agents in field underwriting and data gathering. It is for **informational and educational purposes only**.

    **Not an Offer of Coverage**
    The results, risk classes, and rating estimates provided by this tool are generalized approximations based on industry averages. They do **not** represent a binding offer, quote, or underwriting decision from any specific insurance carrier.
    
    **Carrier Specifics**
    Every insurance carrier (e.g., Prudential, Lincoln, Mutual of Omaha, etc.) has unique underwriting guidelines, knock-out questions, and proprietary build tables. You must consult the official underwriting guides of the specific carrier you are applying with.
    
    **Liability Waiver**
    By using this tool, you acknowledge that the creator and host of this software are **not liable** for any errors, omissions, or financial losses that may result from the use of this data. Final underwriting decisions are made solely by the insurance carrier's home office.
    """)