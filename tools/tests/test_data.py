import csv, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def rows(name):
    with open(os.path.join(ROOT, "data", name), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

CRITERIA = ["sealing", "fluid_containment", "structural_reliability", "usability", "manufacturing"]

def test_scores_overall_is_the_sum_of_criteria():
    for r in rows("ground-test-scores.csv"):
        assert int(r["overall"]) == sum(int(r[c]) for c in CRITERIA), r["variant"]
        assert all(1 <= int(r[c]) <= 5 for c in CRITERIA)

def test_headline_scores():
    s = {r["variant"]: r for r in rows("ground-test-scores.csv")}
    assert set(s) == {"flower-low", "flower-high", "drawstring", "twister", "umbrella", "duckbill"}
    assert s["flower-low"]["overall"] == s["flower-high"]["overall"] == "24"
    assert s["flower-low"]["containment_ml"] == "18" and s["flower-high"]["containment_ml"] == "30"
    assert max(int(r["overall"]) for r in s.values()) == 24

def test_cleaning_grid_is_complete_and_ipa_is_best():
    r = rows("cleaning-colony-counts.csv")
    assert len(r) == 15
    assert {x["method"] for x in r} == {"ipa-70", "microwave", "boiling"}
    total = {m: sum(int(x["colonies"]) for x in r if x["method"] == m) for m in ("ipa-70", "microwave", "boiling")}
    assert min(total, key=total.get) == "ipa-70"
    approx = {(x["method"], x["cup"]) for x in r if x["approximate"] == "true"}
    assert approx == {("microwave", "flower-low"), ("microwave", "flower-high"),
                      ("boiling", "twister"), ("boiling", "reference")}

def test_questionnaire_is_anonymised_and_uses_the_scales():
    r = rows("flight-questionnaire.csv")
    assert [x["participant"] for x in r] == ["P1", "P2", "P3"]
    ease = {"very easy", "easy", "neutral", "moderate", "difficult", "very difficult", "NA"}
    for x in r:
        for col in ("overall_experience", "activation", "insertion", "extraction", "task_difficulty"):
            assert x[col] in ease, (x["participant"], col, x[col])
        assert x["containment"] in {"very well", "minor leakage", "moderate leakage", "significant leakage", "NA"}
        assert x["felt_safe"] in {"yes", "no", "NA"}

def test_codebook_covers_every_column():
    book = {(r["file_name"], r["variable_name"]) for r in rows("codebook.csv")}
    for name in ("ground-test-scores.csv", "cleaning-colony-counts.csv", "flight-questionnaire.csv"):
        for col in rows(name)[0].keys():
            assert (name, col) in book, (name, col)
