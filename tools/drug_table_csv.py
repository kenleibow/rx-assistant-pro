"""Maintain DRUG_INFO (the drug table in data.py) through a spreadsheet-friendly CSV.

Workflow:
  1. python3 -I tools/drug_table_csv.py export            -> drug_table_review.csv + drug_table_categories.csv
  2. Edit drug_table_review.csv in a spreadsheet (editable columns: section, generic, aliases,
     categories, confirm; separate lists with " | "). The info_* columns and reviewer_comment are ignored.
  3. python3 -I tools/drug_table_csv.py import drug_table_review.csv           (dry run: validates, prints a change summary)
     python3 -I tools/drug_table_csv.py import drug_table_review.csv --write   (rewrites the DRUG_INFO block in data.py)
  4. Review `git diff data.py`, run `python3 -I -m unittest discover -s tests -v`, then commit.

Options: `export [OUT_DIR]` (default: project root) and `--project DIR` to run against a copy of the project.
Import refuses (and changes nothing) on: duplicate drugs, a blank generic or category, an alias used by two
drugs, or a drug with a hand-written Tab 1 analysis (DRUG_INSIGHTS) missing from the CSV.
Typing "Other" as the category means "not categorized yet".
"""
import csv, json, re, sys, os, importlib, unicodedata

SEP = " | "
EDITABLE = ["section", "generic", "aliases", "categories", "confirm"]
INFO_COLS = ["has_hand_written_tab1_analysis", "info_tab1_risk_label", "info_tab1_rating", "reviewer_comment"]
SMART = {"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-", "…": "...", " ": " "}
BLOCK = re.compile(r"^DRUG_INFO = \{\n.*?^\}\n", re.S | re.M)


def load(project):
    sys.path.insert(0, project)
    for m in ("data", "drug_logic"):
        sys.modules.pop(m, None)
    return importlib.import_module("data"), importlib.import_module("drug_logic")


def sections_from_source(src):
    block = BLOCK.search(src).group(0)
    sec, out = "", {}
    for line in block.splitlines():
        m = re.match(r"^\s+# --- (.+) ---\s*$", line)
        if m: sec = m.group(1); continue
        m = re.match(r'^\s+"([^"]+)": \{', line)
        if m: out[m.group(1)] = sec
    return out


def export(project, out_dir):
    data, dl = load(project)
    src = open(os.path.join(project, "data.py"), encoding="utf-8").read()
    secs = sections_from_source(src)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "drug_table_review.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(EDITABLE + INFO_COLS)
        for key, row in data.DRUG_INFO.items():
            ins = dl.hand_written_insight([key]) or dl.category_insight([key])
            w.writerow([secs.get(key, ""), key, SEP.join(row["aliases"]), SEP.join(row["categories"]), row.get("confirm", ""),
                        "yes" if key in data.DRUG_INSIGHTS else "no",
                        ins["risk"] if ins else "(none yet - shows 'General / Maintenance')", ins["rating"] if ins else "", ""])
    # category reference
    rules = {"Diabetes": "Diabetes + Cardiac = HIGH RISK warning; Diabetes + Hypertension + Cholesterol = metabolic-syndrome note",
             "Cardiac": "Diabetes + Cardiac = HIGH RISK warning", "Hypertension": "part of the metabolic-syndrome trio",
             "Cholesterol": "part of the metabolic-syndrome trio", "Other": "MEANS NOT CATEGORIZED: named in Tab 2 and the 'no combinations' message is qualified"}
    counts = {}
    for row in data.DRUG_INFO.values():
        for c in row["categories"]: counts[c] = counts.get(c, 0) + 1
    cats = list(dict.fromkeys(list(counts) + list(data.CATEGORY_DEFAULTS)))
    cpath = os.path.join(out_dir, "drug_table_categories.csv")
    with open(cpath, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["category", "drugs_in_table", "combination_rule_it_drives", "tab1_default_rating_source"])
        for c in cats:
            d = data.CATEGORY_DEFAULTS.get(c)
            src_ = f"IMPAIRMENT_DATA: {d}" if isinstance(d, str) else ("inline draft: " + d["risk"] if isinstance(d, dict) else "none yet")
            w.writerow([c, counts.get(c, 0), rules.get(c, "none yet (recorded only)"), src_])
    print(f"wrote {path} ({len(data.DRUG_INFO)} rows) and {cpath} ({len(cats)} categories)")


def clean(s):
    s = (s or "")
    for k, v in SMART.items(): s = s.replace(k, v)
    s = "".join("-" if unicodedata.category(ch) == "Pd" else ch for ch in s)   # every Unicode dash/hyphen -> "-"
    return re.sub(r"\s+", " ", s).strip()


def split_list(s):
    return [clean(x) for x in re.split(r"\s*\|\s*", s or "") if clean(x)]


def format_block(rows):
    lines, cur = ["DRUG_INFO = {"], None
    for r in rows:
        if r["section"] != cur:
            cur = r["section"]
            if cur: lines.append(f"    # --- {cur} ---")
        parts = f'"aliases": {json.dumps(r["aliases"], ensure_ascii=False)}, "categories": {json.dumps(r["categories"], ensure_ascii=False)}'
        if r["confirm"]: parts += f', "confirm": {json.dumps(r["confirm"], ensure_ascii=False)}'
        lines.append(f'    {json.dumps(r["generic"])}: {{{parts}}},')
    lines.append("}")
    return "\n".join(lines) + "\n"


def do_import(project, csv_path, write):
    data, dl = load(project)
    path = os.path.join(project, "data.py")
    src = open(path, encoding="utf-8").read()
    known = {c for r in data.DRUG_INFO.values() for c in r["categories"]} | set(data.CATEGORY_DEFAULTS)
    known_ci = {c.lower(): c for c in known}
    errors, warns, rows, seen = [], [], [], {}
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        missing = [c for c in EDITABLE if c not in (reader.fieldnames or [])]
        if missing: sys.exit(f"ERROR: CSV is missing required column(s): {missing}")
        for n, raw in enumerate(reader, start=2):
            generic = clean(raw["generic"]).lower()
            if not generic and not any(clean(v) for v in raw.values() if v): continue   # blank spreadsheet line
            if not generic: errors.append(f"row {n}: empty 'generic'"); continue
            if generic in seen: errors.append(f"row {n}: duplicate drug '{generic}' (also row {seen[generic]})"); continue
            seen[generic] = n
            cats = []
            for c in split_list(raw["categories"]):
                fixed = known_ci.get(c.lower(), c)
                if fixed != c: warns.append(f"row {n} ({generic}): category '{c}' -> '{fixed}' (matched ignoring case)")
                elif c not in known: warns.append(f"row {n} ({generic}): NEW category '{c}' - it has no Tab 1 default and drives no combination rule")
                if fixed not in cats: cats.append(fixed)
            if not cats: errors.append(f"row {n} ({generic}): no category (use 'Other' for uncategorized)"); continue
            confirm = clean(raw["confirm"])
            for label_, text_ in (("generic", generic), ("confirm", confirm), ("aliases", " ".join(split_list(raw["aliases"])))):
                if not text_.isascii(): warns.append(f"row {n} ({generic}): non-ASCII character left in '{label_}' - the PDF drops these")
            if confirm != (raw["confirm"] or "").strip(): warns.append(f"row {n} ({generic}): tidied spacing/smart punctuation in 'confirm'")
            rows.append({"section": clean(raw["section"]), "generic": generic, "aliases": split_list(raw["aliases"]), "categories": cats, "confirm": confirm})
    # alias clashes (same normalization the app uses)
    owner = {}
    for r in rows:
        for name in [r["generic"]] + r["aliases"]:
            p = " ".join(dl._tokens(name))
            if not p: errors.append(f"{r['generic']}: name '{name}' has no usable letters"); continue
            if owner.setdefault(p, r["generic"]) != r["generic"]:
                errors.append(f"'{name}' (in {r['generic']}) is already used by {owner[p]}")
    keys = {r["generic"] for r in rows}
    for k in data.DRUG_INSIGHTS:
        if k not in keys: errors.append(f"'{k}' has a hand-written Tab 1 analysis in data.py but is not in the CSV (rename/delete would orphan it)")
    # suggestion-list coverage
    for d in data.COMMON_DRUGS_LIST:
        if not any(" ".join(dl._tokens(d)) in {" ".join(dl._tokens(n)) for n in [r["generic"]] + r["aliases"]} for r in rows):
            warns.append(f"suggestion-list name '{d}' no longer resolves to any table row")
    # diff
    old = {k: v for k, v in data.DRUG_INFO.items()}
    new = {r["generic"]: r for r in rows}
    added = [k for k in new if k not in old]; removed = [k for k in old if k not in new]
    changed = []
    for k in new:
        if k in old:
            o, n_ = old[k], new[k]
            d = [f for f, a, b in (("aliases", o["aliases"], n_["aliases"]), ("categories", o["categories"], n_["categories"]), ("confirm", o.get("confirm", ""), n_["confirm"])) if a != b]
            if d: changed.append((k, d, o, n_))
    print(f"rows: {len(rows)} (was {len(old)}) | added {len(added)} | removed {len(removed)} | changed {len(changed)}")
    for k in added: print(f"  + {k}: {new[k]['categories']}")
    for k in removed: print(f"  - {k}")
    for k, d, o, n_ in changed:
        for f in d: print(f"  ~ {k}.{f}: {o.get(f, '') if f != 'confirm' else o.get('confirm', '')!r} -> {n_[f]!r}")
    for w in warns: print("  WARN:", w)
    for e in errors: print("  ERROR:", e)
    if errors: print(f"\nNOT imported: {len(errors)} error(s)."); return 1
    new_src = BLOCK.sub(lambda m: format_block(rows), src, count=1)
    if write:
        open(path, "w", encoding="utf-8").write(new_src); print(f"\nwrote {path}")
    else:
        print("\nvalid (dry run; add --write to apply)")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if "--project" in args:
        i = args.index("--project"); project = os.path.abspath(args[i + 1]); del args[i:i + 2]
    write = "--write" in args
    args = [a for a in args if a != "--write"]
    if not args or args[0] not in ("export", "import") or (args[0] == "import" and len(args) < 2):
        sys.exit(__doc__)
    if args[0] == "export":
        export(project, os.path.abspath(args[1]) if len(args) > 1 else project)
    else:
        sys.exit(do_import(project, args[1], write))
