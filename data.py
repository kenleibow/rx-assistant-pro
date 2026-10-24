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
    "Coumadin", "Digoxin", "Amiodarone", "Flecainide", "Sotalol", "Nitroglycerin",
    "Ranolazine", "Imdur", "Bisoprolol", "Carvedilol", "Labetalol"
]

# =========================================================
#  IMPAIRMENT DATA (Tagged for Universal Logic)
# =========================================================
IMPAIRMENT_DATA = {
    "Hypertension (High BP)": {"qs": ["Date of last reading?", "Is it controlled?", "Med change <12 mos?"], "rating": "Preferred (Controlled) to Table 2.", "risk": "risk-safe"},
    "Heart Attack (History of)": {"qs": ["Date of event?", "Current EF%?", "Recent stress test?"], "rating": "Postpone (0-6mos). Table 2 to 4 (After 1yr).", "risk": "risk-high"},
    "Atrial Fibrillation (AFib)": {"qs": ["Chronic or Paroxysmal?", "Blood thinners?", "Date last episode?"], "rating": "Standard (Infrequent) to Table 2.", "risk": "risk-med"},
    "Stent Placement": {"qs": ["Date inserted?", "How many stents?", "Any chest pain since?"], "rating": "Table 2 (Single) to Table 4 (Multiple).", "risk": "risk-med"},
    "Coronary Artery Disease": {"qs": ["Date of diagnosis?", "Any bypass surgery?", "Current symptoms?"], "rating": "Table 2 to Decline.", "risk": "risk-high"},
    "Stroke / TIA": {"qs": ["Date of event?", "Any residual weakness?", "Carotid ultrasound results?"], "rating": "Postpone (0-1yr). Table 4 to Decline.", "risk": "risk-high"},
    "Pacemaker": {"qs": ["Date implanted?", "Underlying condition?", "Battery check date?"], "rating": "Standard (Sinus Node) to Table 2.", "risk": "risk-med"},
    "Heart Murmur": {"qs": ["Functional or organic?", "Recent echocardiogram?", "Valve involvement?"], "rating": "Preferred (Functional) to Table 4.", "risk": "risk-med"},
    "Aortic Stenosis": {"qs": ["Mild, Moderate or Severe?", "Valve replacement planned?", "Symptoms?"], "rating": "Mild/Stable = Standard. Severe = Decline.", "risk": "risk-med"},
    "Peripheral Vascular Disease": {"qs": ["Do you have pain walking?", "Any surgery?", "Tobacco use?"], "rating": "Table 4 to Decline.", "risk": "risk-high"},
    "Diabetes Type 2": {"qs": ["Current A1C?", "Age of diagnosis?", "Insulin use?", "Neuropathy?"], "rating": "Standard (A1C < 7.0) to Table 2. (Table 4 if Insulin).", "risk": "risk-med"},
    "Diabetes Type 1": {"qs": ["Age diagnosed?", "Insulin pump?", "Kidney issues?", "A1C average?"], "rating": "Table 4 to Table 8. Rarely Standard.", "risk": "risk-high"},
    "Hypothyroidism": {"qs": ["Date diagnosed?", "TSH levels stable?", "Taking Synthroid?"], "rating": "Preferred Possible.", "risk": "risk-safe"},
    "Hyperthyroidism / Graves": {"qs": ["Date diagnosed?", "Treatment type (Radioactive iodine)?", "Current TSH?"], "rating": "Standard (Stable > 1yr).", "risk": "risk-safe"},
    "Hashimoto's": {"qs": ["TSH levels?", "Any goiter or nodules?", "Medications?"], "rating": "Preferred to Standard.", "risk": "risk-safe"},
    "Sleep Apnea": {"qs": ["CPAP use nightly?", "Compliance logs?", "Last sleep study?"], "rating": "Standard (Compliant). Table 2 to Decline (No CPAP).", "risk": "risk-med"},
    "COPD / Emphysema": {"qs": ["Oxygen use?", "Hospitalizations?", "Tobacco use?"], "rating": "Table 2 (Mild) to Decline (Severe/Smoker).", "risk": "risk-high"},
    "Asthma": {"qs": ["Inhaler frequency?", "Oral steroids (Prednisone)?", "Hospital visits?"], "rating": "Standard (Mild) to Table 3 (Severe).", "risk": "risk-safe"},
    "Sarcoidosis": {"qs": ["Lungs only or systemic?", "Current steroid use?", "Date of last flare?"], "rating": "Standard (In remission) to Table 4.", "risk": "risk-med"},
    "Anxiety": {"qs": ["Medication count?", "Hospitalizations?", "Time off work?"], "rating": "Preferred (Mild) to Table 2 (Severe).", "risk": "risk-safe"},
    "Depression": {"qs": ["Hospitalizations?", "Suicide attempts?", "Electro-shock therapy?"], "rating": "Standard (Mild) to Table 4/Decline (Severe).", "risk": "risk-med"},
    "Bipolar Disorder": {"qs": ["Type 1 or 2?", "Hospitalizations < 5 years?", "Stable on meds?"], "rating": "Table 2 minimum. Often Table 4+.", "risk": "risk-high"},
    "ADHD / ADD": {"qs": ["Medication name?", "Any history of drug abuse?", "Stable employment?"], "rating": "Preferred to Standard.", "risk": "risk-safe"},
    "PTSD": {"qs": ["Source of trauma?", "Disability status?", "Substance abuse history?"], "rating": "Standard (Mild) to Decline.", "risk": "risk-med"},
    "Crohn's Disease": {"qs": ["Date of last flare?", "Surgery history?", "Biologic meds (Humira)?"], "rating": "Standard (Remission > 2yr) to Table 4.", "risk": "risk-med"},
    "Ulcerative Colitis": {"qs": ["Colonoscopy results?", "Steroid use?", "Surgery?"], "rating": "Standard (Mild) to Table 3.", "risk": "risk-med"},
    "Hepatitis C": {"qs": ["Cured/Treated?", "Liver enzyme levels?", "Alcohol use?"], "rating": "Standard (Cured) to Decline (Untreated).", "risk": "risk-safe"},
    "Fatty Liver": {"qs": ["Liver function tests?", "Alcohol history?", "BMI?"], "rating": "Standard (Mild) to Table 3.", "risk": "risk-med"},
    "Gastric Bypass / Sleeve": {"qs": ["Date of surgery?", "Current weight stable?", "Complications?"], "rating": "Postpone (<6mos). Standard (After 1yr).", "risk": "risk-safe"},
    "GERD / Reflux": {"qs": ["Medications?", "Barrett's Esophagus diagnosis?", "Endoscopy results?"], "rating": "Preferred to Standard.", "risk": "risk-safe"},
    "Seizures / Epilepsy": {"qs": ["Date of last seizure?", "Type (Grand/Petit)?", "Driving restrictions?"], "rating": "Standard (>2yrs seizure free) to Table 4.", "risk": "risk-med"},
    "Multiple Sclerosis (MS)": {"qs": ["Relapsing or Progressive?", "Can you walk unassisted?", "Date diagnosed?"], "rating": "Table 2 to Decline.", "risk": "risk-high"},
    "Parkinson's": {"qs": ["Age onset?", "Progression speed?", "Daily living activities?"], "rating": "Table 4 to Decline.", "risk": "risk-high"},
    "Rheumatoid Arthritis": {"qs": ["Biologic meds?", "Deformity?", "Disability?"], "rating": "Standard to Table 3.", "risk": "risk-med"},
    "Lupus (SLE)": {"qs": ["Organ involvement (Kidney)?", "Steroid use?", "Date diagnosed?"], "rating": "Table 2 to Decline.", "risk": "risk-high"},
    "Fibromyalgia": {"qs": ["Disability status?", "Narcotic pain meds?", "Depression history?"], "rating": "Standard to Table 2.", "risk": "risk-safe"},
    "Gout": {"qs": ["Frequency of attacks?", "Kidney function?", "Alcohol use?"], "rating": "Standard.", "risk": "risk-safe"},
    "Breast Cancer History": {"qs": ["Date of last treatment?", "Stage/Grade?", "Lymph node involvement?"], "rating": "Flat Extra or Standard > 5yrs.", "risk": "risk-high"},
    "Prostate Cancer History": {"qs": ["Gleason score?", "Surgery or Radiation?", "Current PSA?"], "rating": "Standard (Low grade/Surgery) to Table 4.", "risk": "risk-high"},
    "Melanoma History": {"qs": ["Clark Level / Breslow Depth?", "Date removed?", "Chemo?"], "rating": "Standard (In Situ) to Decline (Deep).", "risk": "risk-high"},
    "Colon Cancer History": {"qs": ["Stage?", "Date of surgery?", "Colonoscopy since?"], "rating": "Postpone (0-2yrs). Table 2 to Standard > 5yrs.", "risk": "risk-high"},
    "Thyroid Cancer": {"qs": ["Type (Papillary)?", "Radioactive iodine?", "Date treatment ended?"], "rating": "Standard (after 1 year).", "risk": "risk-med"},
    "Lymphoma (Hodgkins)": {"qs": ["Stage?", "Date of last chemo?", "Recurrence?"], "rating": "Flat Extra or Table Rating (Requires 2-5yr wait).", "risk": "risk-high"},
    "Kidney Stones": {"qs": ["Single or multiple?", "Surgery required?", "Kidney function normal?"], "rating": "Preferred (Single) to Table 2.", "risk": "risk-safe"},
    "Chronic Kidney Disease": {"qs": ["What is the Stage (1-5)?", "GFR level?", "Diabetic?"], "rating": "Standard (Stage 1) to Decline (Stage 3+).", "risk": "risk-high"},
    "Barrett's Esophagus": {"qs": ["Biopsy results?", "Dysplasia?", "Follow up schedule?"], "rating": "Standard to Table 3.", "risk": "risk-med"},
    "Alcohol History": {"qs": ["Date of last drink?", "AA attendance?", "DUI history?"], "rating": "Postpone (<2yrs sober). Standard (>5yrs sober).", "risk": "risk-high"}
}

# =========================================================
#  DRUG TABLE  (*** DRAFT - needs underwriter review ***)
# =========================================================
# One row per drug, keyed by generic name (lowercase). Edit freely:
#   "aliases"    other names that mean the same drug: brands, spellings, common forms.
#                Typing any alias is treated exactly like typing the generic name.
#   "categories" what the drug tells an underwriter. These feed the combination rules:
#                  Diabetes + Hypertension + Cholesterol -> metabolic syndrome note
#                  Diabetes + Cardiac                    -> HIGH RISK warning
#                Other categories are recorded but currently trigger no combination rule.
#                "Other" means NOT categorized yet: Tab 2 names the drug and qualifies its
#                "no combinations" message instead of reassuring.
#   "confirm"    (optional) shown in Tab 2 when the drug could mean different things
#                (e.g. a blood thinner for AFib vs. a leg clot). Leave out if not needed.
# A drug not in this table falls back to the old guess from the FDA label text.
DRUG_INFO = {
    # --- Diabetes ---
    "metformin": {"aliases": ["glucophage", "metformin hydrochloride", "metformin hcl", "fortamet", "glumetza"], "categories": ["Diabetes"]},
    "glipizide": {"aliases": ["glucotrol"], "categories": ["Diabetes"]},
    "sitagliptin": {"aliases": ["januvia"], "categories": ["Diabetes"]},
    "dapagliflozin": {"aliases": ["farxiga"], "categories": ["Diabetes"], "confirm": "Also prescribed for heart failure and kidney disease - confirm the reason."},
    "empagliflozin": {"aliases": ["jardiance"], "categories": ["Diabetes"], "confirm": "Also prescribed for heart failure and kidney disease - confirm the reason."},
    "semaglutide": {"aliases": ["ozempic", "rybelsus"], "categories": ["Diabetes"], "confirm": "The same drug is sold as Wegovy for weight loss - confirm the reason."},
    "tirzepatide": {"aliases": ["mounjaro", "zepbound"], "categories": ["Diabetes"], "confirm": "Zepbound is the weight-loss brand - confirm the reason."},
    "dulaglutide": {"aliases": ["trulicity"], "categories": ["Diabetes"]},
    "wegovy": {"aliases": [], "categories": ["Weight Management"], "confirm": "Weight-loss use - build/BMI rating applies; ask about diabetes and heart history."},
    # --- Blood pressure ---
    "lisinopril": {"aliases": ["zestril", "prinivil", "qbrelis"], "categories": ["Hypertension"]},
    "amlodipine": {"aliases": ["norvasc"], "categories": ["Hypertension"]},
    "losartan": {"aliases": ["cozaar", "losartan potassium"], "categories": ["Hypertension"]},
    "hydrochlorothiazide": {"aliases": ["hctz", "microzide"], "categories": ["Hypertension"]},
    "olmesartan": {"aliases": ["benicar"], "categories": ["Hypertension"]},
    "labetalol": {"aliases": ["trandate", "normodyne"], "categories": ["Hypertension"]},
    "metoprolol": {"aliases": ["lopressor", "toprol xl", "metoprolol tartrate", "metoprolol succinate"], "categories": ["Hypertension"], "confirm": "Beta-blocker also prescribed for angina, a prior heart attack, heart failure and AFib - confirm the reason."},
    "bisoprolol": {"aliases": ["zebeta"], "categories": ["Hypertension"], "confirm": "Beta-blocker also prescribed for heart failure - confirm the reason."},
    "furosemide": {"aliases": ["lasix"], "categories": ["Hypertension"], "confirm": "Water pill often prescribed for heart failure or swelling - confirm the reason."},
    # --- Cholesterol ---
    "atorvastatin": {"aliases": ["lipitor"], "categories": ["Cholesterol"]},
    "simvastatin": {"aliases": ["zocor"], "categories": ["Cholesterol"]},
    "rosuvastatin": {"aliases": ["crestor"], "categories": ["Cholesterol"]},
    # --- Heart / blood thinners ---
    "clopidogrel": {"aliases": ["plavix"], "categories": ["Cardiac"]},
    "sacubitril and valsartan": {"aliases": ["entresto"], "categories": ["Cardiac"]},
    "digoxin": {"aliases": ["lanoxin"], "categories": ["Cardiac"]},
    "amiodarone": {"aliases": ["pacerone", "cordarone"], "categories": ["Cardiac"]},
    "flecainide": {"aliases": ["tambocor", "flecanide"], "categories": ["Cardiac"]},
    "sotalol": {"aliases": ["betapace"], "categories": ["Cardiac"]},
    "nitroglycerin": {"aliases": ["nitrostat"], "categories": ["Cardiac"]},
    "ranolazine": {"aliases": ["ranexa"], "categories": ["Cardiac"]},
    "isosorbide mononitrate": {"aliases": ["imdur"], "categories": ["Cardiac"]},
    "carvedilol": {"aliases": ["coreg"], "categories": ["Cardiac"], "confirm": "Prescribed for heart failure or for high blood pressure - confirm which."},
    "apixaban": {"aliases": ["eliquis"], "categories": ["Cardiac"], "confirm": "Blood thinner for AFib or for a blood clot (DVT/PE) - confirm which."},
    "rivaroxaban": {"aliases": ["xarelto"], "categories": ["Cardiac"], "confirm": "Blood thinner for AFib or for a blood clot (DVT/PE) - confirm which."},
    "dabigatran": {"aliases": ["pradaxa"], "categories": ["Cardiac"], "confirm": "Blood thinner for AFib or for a blood clot (DVT/PE) - confirm which."},
    "warfarin": {"aliases": ["coumadin", "jantoven"], "categories": ["Cardiac"], "confirm": "Blood thinner for AFib, a heart valve or a blood clot - confirm which."},
    "aspirin": {"aliases": ["bayer", "ecotrin", "baby aspirin", "low dose aspirin"], "categories": ["Other"], "confirm": "Daily low-dose aspirin may mean prevention or existing heart disease - confirm the reason."},
    # --- Thyroid / stomach / gout ---
    "levothyroxine": {"aliases": ["synthroid", "levoxyl", "unithroid", "euthyrox"], "categories": ["Thyroid"]},
    "omeprazole": {"aliases": ["prilosec"], "categories": ["GI"]},
    "pantoprazole": {"aliases": ["protonix"], "categories": ["GI"]},
    "esomeprazole": {"aliases": ["nexium"], "categories": ["GI"]},
    "allopurinol": {"aliases": ["zyloprim"], "categories": ["Gout"]},
    "colchicine": {"aliases": ["colcrys", "mitigare"], "categories": ["Gout"]},
    # --- Breathing ---
    "montelukast": {"aliases": ["singulair"], "categories": ["Respiratory"]},
    "fluticasone": {"aliases": ["flonase", "flovent", "fluticasone propionate"], "categories": ["Respiratory"]},
    "albuterol": {"aliases": ["ventolin", "proair", "proventil"], "categories": ["Respiratory"]},
    "fluticasone and salmeterol": {"aliases": ["advair", "advair diskus", "wixela"], "categories": ["Respiratory"], "confirm": "Asthma vs. COPD changes the rating - ask which."},
    "budesonide and formoterol": {"aliases": ["symbicort", "breyna"], "categories": ["Respiratory"], "confirm": "Asthma vs. COPD changes the rating - ask which."},
    "tiotropium": {"aliases": ["spiriva"], "categories": ["Respiratory"], "confirm": "Mainly a COPD medication - ask about severity, oxygen use and hospitalizations."},
    # --- Mental health / sleep ---
    "sertraline": {"aliases": ["zoloft"], "categories": ["Mental Health"]},
    "escitalopram": {"aliases": ["lexapro"], "categories": ["Mental Health"]},
    "fluoxetine": {"aliases": ["prozac", "sarafem"], "categories": ["Mental Health"]},
    "venlafaxine": {"aliases": ["effexor", "effexor xr"], "categories": ["Mental Health"]},
    "duloxetine": {"aliases": ["cymbalta"], "categories": ["Mental Health"]},
    "trazodone": {"aliases": ["desyrel"], "categories": ["Mental Health"]},
    "bupropion": {"aliases": ["wellbutrin", "zyban", "bupropion hcl"], "categories": ["Mental Health"], "confirm": "Also prescribed for smoking cessation - ask about tobacco use."},
    "aripiprazole": {"aliases": ["abilify"], "categories": ["Psychiatric (Serious)"]},
    "quetiapine": {"aliases": ["seroquel"], "categories": ["Psychiatric (Serious)"]},
    "alprazolam": {"aliases": ["xanax"], "categories": ["Anxiety / Sedative"]},
    "clonazepam": {"aliases": ["klonopin"], "categories": ["Anxiety / Sedative"], "confirm": "Also used for seizures and panic disorder - ask which."},
    "diazepam": {"aliases": ["valium"], "categories": ["Anxiety / Sedative"]},
    "lorazepam": {"aliases": ["ativan"], "categories": ["Anxiety / Sedative"]},
    "zolpidem": {"aliases": ["ambien"], "categories": ["Sleep"]},
    "eszopiclone": {"aliases": ["lunesta"], "categories": ["Sleep"]},
    # --- Pain / inflammation / immune ---
    "gabapentin": {"aliases": ["neurontin", "gralise"], "categories": ["Pain"], "confirm": "Used for nerve pain and for seizures - confirm the reason."},
    "pregabalin": {"aliases": ["lyrica"], "categories": ["Pain"], "confirm": "Used for nerve pain, fibromyalgia and seizures - ask which."},
    "tramadol": {"aliases": ["ultram"], "categories": ["Pain"], "confirm": "Opioid - ask how long and how often it has been taken."},
    "meloxicam": {"aliases": ["mobic"], "categories": ["Pain"]},
    "prednisone": {"aliases": ["deltasone", "rayos"], "categories": ["Steroid"], "confirm": "Reason varies widely (asthma/COPD, arthritis, lupus, IBD, transplant) - ask why."},
    "adalimumab": {"aliases": ["humira"], "categories": ["Autoimmune"], "confirm": "Used for RA, psoriasis, Crohn's/colitis and more - ask which."},
    "etanercept": {"aliases": ["enbrel"], "categories": ["Autoimmune"], "confirm": "Used for RA, psoriasis and more - ask which."},
    # --- Urology ---
    "tamsulosin": {"aliases": ["flomax"], "categories": ["Urology"]},
    "sildenafil": {"aliases": ["viagra"], "categories": ["Urology"]},
    "tadalafil": {"aliases": ["cialis"], "categories": ["Urology"]},
    "vardenafil": {"aliases": ["levitra", "staxyn"], "categories": ["Urology"]},
}

# Hand-written drug analyses (moved unchanged from Tab 1). Checked in this order.
_HEART_INSIGHT = {"risk": "Heart Disease / Stroke", "style": "risk-high", "questions": ["History of TIA/Stroke?", "Stent placement?"], "rating": "Standard to Decline."}
DRUG_INSIGHTS = {
    "metformin": {"risk": "Diabetes Type 2", "style": "risk-med", "questions": ["Is this for Pre-Diabetes or Type 2?", "What is your A1C?", "Any neuropathy?"], "rating": "Standard (if A1C < 7.0) to Table 2."},
    "lisinopril": {"risk": "Hypertension (High BP)", "style": "risk-safe", "questions": ["Is BP controlled?", "Last reading?", "Do you take >2 BP meds?"], "rating": "Preferred Best possible."},
    "amlodipine": {"risk": "Hypertension (High BP)", "style": "risk-safe", "questions": ["Is BP controlled?", "Last reading?", "Do you take >2 BP meds?"], "rating": "Preferred Best possible."},
    "clopidogrel": _HEART_INSIGHT,
    "aripiprazole": {"risk": "Bipolar / Depression / Schizophrenia", "style": "risk-high", "questions": ["Hospitalizations in last 5 years?", "Suicide attempts?"], "rating": "Complex. Bipolar = Table Rating."},
    "sacubitril and valsartan": {"risk": "Heart Failure (CHF)", "style": "risk-high", "questions": ["What is your Ejection Fraction?", "Any hospitalizations recently?"], "rating": "Likely Decline."},
}

# Starting rating/questions for a drug with no hand-written analysis, by category.
# A text value borrows that entry from IMPAIRMENT_DATA above; a dict is written inline;
# None (or a missing category) means "no default yet" -> generic "depends on condition".
CATEGORY_DEFAULTS = {
    "Diabetes": "Diabetes Type 2",
    "Hypertension": "Hypertension (High BP)",
    "Thyroid": "Hypothyroidism",
    "GI": "GERD / Reflux",
    "Gout": "Gout",
    "Mental Health": "Depression",
    "Psychiatric (Serious)": "Bipolar Disorder",
    "Anxiety / Sedative": "Anxiety",
    "Autoimmune": "Rheumatoid Arthritis",
    "Cholesterol": {"risk": "Cholesterol / Lipids", "style": "risk-safe", "questions": ["Current LDL / total cholesterol?", "Taking it for prevention or after a heart event?", "Any heart or diabetes history?"], "rating": "Preferred to Standard (controlled)."},
    "Cardiac": {"risk": "Heart Disease / Rhythm", "style": "risk-high", "questions": ["What heart condition is this for?", "Date of last cardiac event or hospitalization?", "Ejection fraction (if heart failure)?"], "rating": "Table 2 to Decline (depends on condition and control)."},
    "Respiratory": {"risk": "Asthma / COPD", "style": "risk-med", "questions": ["Asthma or COPD?", "Oral steroids or hospitalizations?", "Tobacco use?"], "rating": "Standard (Mild asthma) to Decline (Severe COPD / Smoker)."},
}
