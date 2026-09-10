import glob, hashlib, os
import pytest
from tools.rename import kebab, VARIANT_DIRS

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HW = os.path.join(ROOT, "hardware")
INCOMING = os.path.join(ROOT, "incoming", "design")

def files(pattern):
    return sorted(glob.glob(os.path.join(HW, pattern)))

@pytest.mark.parametrize("slug", sorted(VARIANT_DIRS.values()))
def test_every_variant_has_step_nx_and_mould_stl(slug):
    for sub in ("step", "nx", "mould-stl"):
        assert os.listdir(os.path.join(HW, slug, sub)), f"{slug}/{sub} is empty"

def test_counts():
    assert len(files("*/step/*.step")) == 36
    assert len(files("*/nx/*.prt")) == 36
    assert len(files("*/mould-stl/*.stl")) == 78

def test_step_and_stl_names_follow_the_rule():
    for p in files("*/step/*") + files("*/mould-stl/*"):
        assert kebab(os.path.basename(p)) == os.path.basename(p), p

def test_step_files_declare_millimetres():
    for p in files("*/step/*.step"):
        with open(p, encoding="latin-1") as f:
            assert "SI_UNIT(.MILLI.,.METRE.)" in f.read(), p

def test_no_stray_file_types():
    for p in glob.glob(os.path.join(HW, "*", "*", "*")):
        assert os.path.splitext(p)[1] in (".step", ".prt", ".stl"), p

@pytest.mark.skipif(not os.path.isdir(INCOMING), reason="incoming/ not present (CI)")
def test_byte_identical_to_the_supplied_files():
    def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
    shipped = {sha(p) for p in files("*/*/*")}
    for folder in VARIANT_DIRS:
        for p in glob.glob(os.path.join(INCOMING, folder, "**", "*"), recursive=True):
            if p.lower().endswith((".prt", ".stp", ".stl")):
                assert sha(p) in shipped, p
