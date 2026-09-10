import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def read(p): return open(os.path.join(ROOT, p), encoding="utf-8").read()
ORDER = ["Keller", "Dugué", "Tkaczuk", "Tilley"]

def test_author_order_everywhere():
    for p in ("README.md", "CITATION.cff"):
        text = read(p)
        pos = [text.index(n) for n in ORDER]
        assert pos == sorted(pos), p
    z = json.loads(read(".zenodo.json"))
    assert [c["name"].split(",")[0] for c in z["creators"]] == ORDER

def test_licences_and_no_deferred_items():
    z = json.loads(read(".zenodo.json"))
    assert z["license"] == "cern-ohl-p-2.0"
    cff = read("CITATION.cff")
    assert "license: CERN-OHL-P-2.0" in cff
    for p in ("README.md", "CITATION.cff", ".zenodo.json"):
        low = read(p).lower()
        assert "oshwa" not in low and "zenodo.org/badge" not in low and "doi:" not in low, p

def test_orcids_only_where_known():
    cff = read("CITATION.cff")
    assert "0000-0001-7997-9423" in cff and "0000-0002-2095-9724" in cff
    assert cff.count("orcid:") == 3   # Tkaczuk, Tilley, and Tkaczuk again as contact
