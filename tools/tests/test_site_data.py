import csv, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = json.load(open(os.path.join(ROOT, "site", "src", "data", "site.json"), encoding="utf-8"))

def test_no_oshwa_no_doi_no_onshape():
    text = json.dumps(SITE).lower()
    for banned in ("oshwa", "doi", "onshape", "plausible"):
        assert banned not in text, banned

def test_repo_and_names():
    assert SITE["repo"] == "https://github.com/Global-Health-Engineering/ammity-cup"
    assert SITE["name"] == "SpaceCup" and SITE["project"] == "AMMITY"

def test_bench_numbers_match_data():
    with open(os.path.join(ROOT, "data", "ground-test-scores.csv"), newline="") as f:
        s = {r["variant"]: r for r in csv.DictReader(f)}
    assert SITE["bench"]["flower_score"] == int(s["flower-low"]["overall"]) == int(s["flower-high"]["overall"])
    assert SITE["bench"]["flower_low_ml"] == int(s["flower-low"]["containment_ml"])
    assert SITE["bench"]["flower_high_ml"] == int(s["flower-high"]["containment_ml"])
