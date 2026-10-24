"""Integrity checks for the drug table (data.DRUG_INFO) and the name resolver (drug_logic).

Run from the project root, e.g. after editing the table or importing a CSV:
    python3 -I -m unittest discover -s tests -v

These check that the table is internally consistent, not what any drug's category *should* be
(that is underwriting content and is expected to change).
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import data
import drug_logic as dl

RULE_CATEGORIES = ("Diabetes", "Hypertension", "Cholesterol", "Cardiac")   # used by check_med_combinations()
STYLES = ("risk-safe", "risk-med", "risk-high")


def phrases(row_key, row):
    return [" ".join(dl._tokens(n)) for n in [row_key] + row["aliases"]]


class TableIntegrity(unittest.TestCase):
    def test_every_suggestion_list_name_resolves(self):
        missing = [d for d in data.COMMON_DRUGS_LIST if not dl.resolve_drugs(d)]
        self.assertEqual(missing, [], "names in COMMON_DRUGS_LIST that match no drug-table row")

    def test_no_alias_is_claimed_by_two_drugs(self):
        owners = {}
        for key, row in data.DRUG_INFO.items():
            for p in phrases(key, row):
                owners.setdefault(p, set()).add(key)
        clashes = {p: sorted(k) for p, k in owners.items() if len(k) > 1}
        self.assertEqual(clashes, {})

    def test_every_name_has_usable_letters(self):
        empty = [(k, n) for k, r in data.DRUG_INFO.items() for n in [k] + r["aliases"] if not dl._tokens(n)]
        self.assertEqual(empty, [])

    def test_keys_are_lowercase_and_rows_well_formed(self):
        for key, row in data.DRUG_INFO.items():
            self.assertEqual(key, key.strip().lower(), f"key {key!r} should be lowercase with no stray spaces")
            self.assertIsInstance(row["aliases"], list, key)
            self.assertTrue(row["categories"] and isinstance(row["categories"], list), f"{key}: needs at least one category ('Other' = uncategorized)")
            self.assertLessEqual(set(row), {"aliases", "categories", "confirm"}, f"{key}: unexpected field")

    def test_text_is_ascii(self):
        # the PDF writer drops non-ASCII characters, so catch them at the source
        for key, row in data.DRUG_INFO.items():
            for text in [key] + row["aliases"] + [row.get("confirm", "")]:
                self.assertTrue(text.isascii(), f"{key}: non-ASCII text {text!r} would be mangled in PDFs")

    def test_category_spelling_is_consistent(self):
        cats = {c for r in data.DRUG_INFO.values() for c in r["categories"]}
        by_lower = {}
        for c in cats:
            by_lower.setdefault(c.strip().lower(), set()).add(c)
        variants = {k: v for k, v in by_lower.items() if len(v) > 1}
        self.assertEqual(variants, {}, "same category spelled two ways (capitalization/spacing)")
        self.assertEqual([c for c in cats if c != c.strip()], [])

    def test_combination_rule_categories_are_all_in_use(self):
        used = {c for r in data.DRUG_INFO.values() for c in r["categories"]}
        self.assertEqual([c for c in RULE_CATEGORIES if c not in used], [],
                         "a category that check_med_combinations() relies on has no drugs, so that rule can never fire")


class HandWrittenAndDefaults(unittest.TestCase):
    def test_hand_written_analyses_belong_to_table_rows(self):
        self.assertEqual([k for k in data.DRUG_INSIGHTS if k not in data.DRUG_INFO], [])

    def test_insight_shape(self):
        entries = dict(data.DRUG_INSIGHTS)
        entries.update({f"default:{c}": d for c, d in data.CATEGORY_DEFAULTS.items() if isinstance(d, dict)})
        for name, e in entries.items():
            self.assertEqual(set(e), {"risk", "style", "questions", "rating"}, name)
            self.assertIn(e["style"], STYLES, name)
            self.assertTrue(e["questions"] and all(isinstance(q, str) for q in e["questions"]), name)

    def test_category_defaults_reference_real_impairment_rows(self):
        bad = {c: v for c, v in data.CATEGORY_DEFAULTS.items() if isinstance(v, str) and v not in data.IMPAIRMENT_DATA}
        self.assertEqual(bad, {})

    def test_insights_come_back_as_copies(self):
        got = dl.hand_written_insight(["metformin"])
        got["questions"].append("mutated")
        self.assertNotIn("mutated", data.DRUG_INSIGHTS["metformin"]["questions"])


class Resolver(unittest.TestCase):
    R = staticmethod(dl.resolve_drugs)

    def test_brand_generic_pairs_resolve_to_the_same_row(self):
        # the original Gap 1: a brand and its generic must never be treated as different drugs
        for brand, generic in [("plavix", "clopidogrel"), ("xarelto", "rivaroxaban"), ("eliquis", "apixaban"),
                               ("coumadin", "warfarin"), ("lipitor", "atorvastatin"), ("synthroid", "levothyroxine"),
                               ("glucophage", "metformin"), ("zestril", "lisinopril")]:
            self.assertEqual(self.R(brand), self.R(generic), f"{brand} vs {generic}")
            self.assertEqual(len(self.R(brand)), 1, brand)

    def test_case_strength_and_form_are_ignored(self):
        self.assertEqual(self.R("METFORMIN 500 mg ER"), ["metformin"])
        self.assertEqual(self.R("Toprol-XL 50mg"), ["metoprolol"])

    def test_combinations_resolve_to_each_ingredient(self):
        self.assertEqual(self.R("lisinopril/HCTZ"), ["lisinopril", "hydrochlorothiazide"])
        self.assertEqual(self.R("lisinopril and hydrochlorothiazide"), ["lisinopril", "hydrochlorothiazide"])

    def test_longest_name_wins(self):
        self.assertEqual(self.R("fluticasone and salmeterol"), self.R("advair"))
        self.assertEqual(len(self.R("advair")), 1)

    def test_no_partial_word_matches(self):
        self.assertEqual(self.R("plavixx"), [])
        self.assertEqual(self.R("metforminx"), [])

    def test_unknown_or_empty_gives_nothing(self):
        self.assertEqual(self.R("definitely not a drug"), [])
        self.assertEqual(self.R(""), [])

    def test_fda_label_names_are_the_fallback_only(self):
        label = {"openfda": {"brand_name": ["Zestoretic"], "generic_name": ["LISINOPRIL AND HYDROCHLOROTHIAZIDE"]}}
        self.assertEqual(self.R("zestoretic", label), ["lisinopril", "hydrochlorothiazide"])
        other = {"openfda": {"generic_name": ["METFORMIN"]}}
        self.assertEqual(self.R("plavix", other), self.R("plavix"), "the typed name must win over the label")


if __name__ == "__main__":
    unittest.main(verbosity=2)
