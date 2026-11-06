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

CONCEPT_DOI = "10.5281/zenodo.24010364"

def test_licences_and_no_oshwa_claim():
    z = json.loads(read(".zenodo.json"))
    assert z["license"] == "cern-ohl-p-2.0"
    cff = read("CITATION.cff")
    assert "license: CERN-OHL-P-2.0" in cff
    for p in ("README.md", "CITATION.cff", ".zenodo.json"):
        assert "oshwa" not in read(p).lower(), p

def test_concept_doi_everywhere():
    assert f"doi: {CONCEPT_DOI}" in read("CITATION.cff")
    readme = read("README.md")
    assert f"zenodo.org/badge/DOI/{CONCEPT_DOI}.svg" in readme
    assert f"https://doi.org/{CONCEPT_DOI}" in readme
    site = json.loads(read("site/src/data/site.json"))
    assert site["doi"] == CONCEPT_DOI
    # Zenodo assigns the DOI itself; .zenodo.json must not carry one.
    assert "doi" not in json.loads(read(".zenodo.json"))

ORCIDS = {
    "Keller": "0009-0001-5506-8729",
    "Dugué": "0000-0001-9188-8321",
    "Tkaczuk": "0000-0001-7997-9423",
    "Tilley": "0000-0002-2095-9724",
}

def test_orcids_for_every_author():
    cff = read("CITATION.cff")
    for orcid in ORCIDS.values():
        assert f"orcid: https://orcid.org/{orcid}" in cff
    assert cff.count("orcid:") == 5   # four authors, plus Tkaczuk again as contact
    z = json.loads(read(".zenodo.json"))
    assert {c["name"].split(",")[0]: c.get("orcid") for c in z["creators"]} == ORCIDS
    readme = read("README.md")
    for orcid in ORCIDS.values():
        assert f"(https://orcid.org/{orcid})" in readme
