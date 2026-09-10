import pytest
from tools.rename import kebab, VARIANT_DIRS

@pytest.mark.parametrize("src, dst", [
    ("flower_cup_withrim_part_m.stp", "flower-cup-withrim-part.step"),
    ("Twister_Cup_Top2_bottom.stl", "twister-cup-top2-bottom.stl"),
    ("Drawsting2_mold_bottom.stl", "drawstring2-mould-bottom.stl"),
    ("Drawsting.stp", "drawstring.step"),
    ("menstrual_cup_medium_without_balloon_mold_ousideleft.stl",
     "menstrual-cup-medium-without-balloon-mould-outsideleft.stl"),
    ("Balloon_Top_1_Mold1_outsideleft.stl", "balloon-top-1-mould1-outsideleft.stl"),
    ("umbrella_top_2_open_Full_mold_u1_m.stl", "umbrella-top-2-open-full-mould-u1.stl"),
    ("twister_skin_mold_1.stl", "twister-skin-mould-1.stl"),
])
def test_kebab(src, dst):
    assert kebab(src) == dst

def test_kebab_is_idempotent():
    for name in ["flower-cup-withrim-part.step", "twister-skin-mould-1.stl"]:
        assert kebab(name) == name

def test_all_nine_variants_mapped():
    assert sorted(VARIANT_DIRS.values()) == sorted([
        "flower-low", "flower-high", "twister", "umbrella", "drawstring",
        "duckbill", "balloon", "extraction-valve", "artificial-vagina"])
