import pytest
from tools.verify_scope import offending_reason, main

OUT = [
    "incoming/design/README.md",
    "docs/thesis.pdf",
    "docs/Master's_Thesis_AMMITY_2026_KimKeller.pdf",
    "data/post-flight-questionaire_P1.pdf",
    "docs/flight-questionnaire.pdf",
    "docs/AMMITY DR Training Slides_1.pptx",
    "hardware/flower-low/step/flower-stopper.log",
    "build/meshes/flower-low/index.json",
    ".superpowers/specs/x.md",
    "docs/superpowers/plans/x.md",
    "site/public/brand/certification-mark-CH000099-wide.svg",
    "site/public/video/raw.mp4",
    "hardware/flower-low/scene.blend",
]
IN = [
    "hardware/flower-low/nx/flower_cup_withrim_part_m.prt",
    "hardware/flower-low/step/flower-cup-withrim-part.step",
    "hardware/flower-low/mould-stl/flower-cup-withrim-mould-topleft.stl",
    "docs/moulding-guide.pdf",
    "docs/flight-protocol.md",
    "data/flight-questionnaire.csv",   # the anonymised CSV is the one allowed form
    "site/public/models/flower-low.glb",
    "site/public/renders/flower-low.png",
]

@pytest.mark.parametrize("path", OUT)
def test_out_of_scope_paths_are_rejected(path):
    assert offending_reason(path) is not None

@pytest.mark.parametrize("path", IN)
def test_release_paths_are_allowed(path):
    assert offending_reason(path) is None

def test_main_returns_1_when_any_offender(capsys):
    assert main(["README.md", "docs/thesis.pdf"]) == 1
    assert "docs/thesis.pdf" in capsys.readouterr().out

def test_main_returns_0_when_clean():
    assert main(["README.md", "data/flight-questionnaire.csv"]) == 0
