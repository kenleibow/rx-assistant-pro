import streamlit as st
import requests

# --- CONFIGURATION ---
st.set_page_config(page_title="Rx Field Assistant", page_icon="🛡️", layout="wide")

# --- CSS STYLING ---
st.markdown("""
    <style>
    .risk-high { background-color: #ffcccc; padding: 10px; border-radius: 5px; color: #8a0000;}
    .risk-med { background-color: #fff4cc; padding: 10px; border-radius: 5px; color: #664d00;}
    .risk-safe { background-color: #e6fffa; padding: 10px; border-radius: 5px; color: #004d40;}
    /* Make buttons full width for easier clicking */
    div.stButton > button { width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Life Insurance Rx Assistant")

# --- CLEAR FUNCTIONS (The Magic Erasers) ---
# These functions run when you click "Start New Case"
def clear_single():
    st.session_state["single_input"] = ""

def clear_multi():
    st.session_state["multi_input"] = ""

# --- CREATE TABS ---
tab1, tab2 = st.tabs(["🔍 Single Med Decoder (Deep Dive)", "💊 Multi-Med Analyzer (Combinations)"])

# =========================================================
#  LOGIC ENGINE 1: SINGLE MEDICATION
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
#  LOGIC ENGINE 2: MULTI MED
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
        # THE NEW BUTTON: Calls 'clear_single' when clicked
        st.button("🔄 New Case", on_click=clear_single, key="btn_clear_single")

    # The 'key="single_input"' connects this box to the session state
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
        # THE NEW BUTTON: Calls 'clear_multi' when clicked
        st.button("🔄 New Case", on_click=clear_multi, key="btn_clear_multi")
    
    st.markdown("Paste a list to check for **Dangerous Combinations** (Triads).")
    
    # The 'key="multi_input"' connects this box to the session state
    multi_input = st.text_area("List Meds (comma separated):", height=100, 
                              placeholder="Metformin, Lisinopril, Atorvastatin", key="multi_input")
    
    if st.button("Analyze Combinations"):
        if multi_input:
            meds = [m.strip() for m in multi_input.split(',')]
            categories = []
            
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