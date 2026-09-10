import pytest
from tools.verify_copy import scan_file, find_files, main

def write(p, text):
    p.write_text(text); return str(p)

@pytest.mark.parametrize("text", [
    "The SpaceCup is FDA-approved.",
    "a CE marked device",
    "It is clinically tested.",
    "clinically proven containment",
    "The cup is safe for human use.",
    "A leak-proof seal.",
    "leakproof in microgravity",
    "space-qualified hardware",
    "Certified by OSHWA.",
    "It is a certified medical device.",
])
def test_unsupported_claims_are_caught(tmp_path, text):
    assert scan_file(write(tmp_path / "p.md", text + "\n"))

@pytest.mark.parametrize("text", [
    "The SpaceCup is a research prototype, not a certified medical device.",
    "Medical-grade silicone does not make the prototype a certified medical device.",
    "Only minor leakage was reported.",
    "Tested on a parabolic flight.",
])
def test_the_required_disclaimers_pass(tmp_path, text):
    assert scan_file(write(tmp_path / "p.md", text + "\n")) == []

def test_line_numbers(tmp_path):
    hits = scan_file(write(tmp_path / "p.md", "ok\nis leak-proof\n"))
    assert [h[0] for h in hits] == [2]

def test_find_files_filters_suffixes(tmp_path):
    write(tmp_path / "a.md", "x"); write(tmp_path / "b.png", "x")
    assert [f.endswith("a.md") for f in find_files([str(tmp_path / "*")])] == [True]

def test_main_exit_codes(tmp_path):
    good = write(tmp_path / "g.md", "research prototype\n")
    bad = write(tmp_path / "b.md", "FDA approved\n")
    assert main([good]) == 0
    assert main([bad]) == 1
