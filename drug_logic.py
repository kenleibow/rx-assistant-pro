"""Resolves typed drug names (brand, generic, strength/form variants) to rows in data.DRUG_INFO.

No Streamlit here, so it can be tested on its own.
"""
import re
from data import DRUG_INFO, DRUG_INSIGHTS, CATEGORY_DEFAULTS, IMPAIRMENT_DATA

# Words that don't change which drug it is: strengths, forms, "and".
_NOISE = {"mg", "mcg", "g", "ml", "unit", "units", "er", "xr", "sr", "xl", "cr", "dr", "la",
          "tablet", "tablets", "tab", "tabs", "capsule", "capsules", "cap", "caps", "oral", "and"}
_RISK_ORDER = {"risk-safe": 0, "risk-med": 1, "risk-high": 2}


def _tokens(text):
    words = re.sub(r"[^a-z0-9]+", " ", str(text).lower()).split()
    return [w for w in words if w not in _NOISE and not w.isdigit()]


def _build_alias_index():
    index = {}
    for key, row in DRUG_INFO.items():
        for name in [key] + list(row.get("aliases", [])):
            phrase = " ".join(_tokens(name))
            if not phrase: continue
            if index.setdefault(phrase, key) != key:   # never crash the app over a table typo
                print(f"[drug table] alias '{phrase}' is used by both '{index[phrase]}' and '{key}'; keeping the first", flush=True)
    return index

ALIAS_INDEX = _build_alias_index()
_MAX_ALIAS_WORDS = max((len(p.split()) for p in ALIAS_INDEX), default=1)


def _scan(text):
    # Every known drug named in the text, longest names first, in the order they appear.
    toks, found, i = _tokens(text), [], 0
    while i < len(toks):
        for n in range(min(_MAX_ALIAS_WORDS, len(toks) - i), 0, -1):
            key = ALIAS_INDEX.get(" ".join(toks[i:i + n]))
            if key:
                if key not in found: found.append(key)
                i += n
                break
        else:
            i += 1
    return found


def resolve_drugs(name, label=None):
    """Drug-table keys for a typed name (a combination like 'lisinopril/hctz' gives several).
    If the typed name isn't in the table, fall back to the generic/brand names on the FDA label."""
    found = _scan(name)
    if not found and label:
        openfda = label.get("openfda", {})
        for field in ("generic_name", "brand_name"):
            found = _scan(" ".join(openfda.get(field, [])))
            if found: break
    return found


def drug_categories(keys):
    cats = []
    for k in keys:
        for c in DRUG_INFO[k]["categories"]:
            if c not in cats: cats.append(c)
    return cats


def drug_notes(keys):
    return [(k, DRUG_INFO[k]["confirm"]) for k in keys if DRUG_INFO[k].get("confirm")]


def hand_written_insight(keys):
    for k in DRUG_INSIGHTS:          # dict order is the precedence order
        if k in keys: return _copy(DRUG_INSIGHTS[k])
    return None


def category_insight(keys):
    best = None
    for c in drug_categories(keys):
        d = CATEGORY_DEFAULTS.get(c)
        if isinstance(d, str) and d in IMPAIRMENT_DATA:
            e = IMPAIRMENT_DATA[d]
            d = {"risk": d, "style": e["risk"], "questions": e["qs"], "rating": e["rating"]}
        if isinstance(d, dict) and (best is None or _RISK_ORDER[d["style"]] > _RISK_ORDER[best["style"]]):
            best = d                  # several categories: keep the most cautious
    return _copy(best) if best else None


def _copy(d):
    return {**d, "questions": list(d["questions"])}
