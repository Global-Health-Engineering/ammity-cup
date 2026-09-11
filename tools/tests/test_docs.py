import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCS = ["design.md", "manufacturing.md", "use.md", "validation.md", "flight-protocol.md", "design-history.md"]

def read(p): return open(os.path.join(ROOT, p), encoding="utf-8").read()

def test_all_docs_exist_and_have_no_em_dash():
    for d in DOCS + ["../hardware/README.md", "../hardware/nx.md"]:
        text = read(os.path.join("docs", d))
        assert "—" not in text, d

def test_every_repo_link_in_docs_resolves():
    for d in DOCS + ["../hardware/README.md", "../hardware/nx.md"]:
        path = os.path.normpath(os.path.join("docs", d))
        for target in re.findall(r"\]\((?!https?:|#|mailto:)([^)#]+)", read(path)):
            assert os.path.exists(os.path.join(ROOT, os.path.dirname(path), target)), (path, target)

def test_disclaimer_present():
    assert "not a certified medical device" in read("docs/manufacturing.md")
    assert "not a certified medical device" in read("docs/use.md")

def test_hardware_readme_lists_every_shipped_file():
    readme = read("hardware/README.md")
    for root, _, files in os.walk(os.path.join(ROOT, "hardware")):
        for f in files:
            if f.endswith((".step", ".stl")):
                assert f in readme, f
