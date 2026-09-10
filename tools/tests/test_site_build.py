import glob, os, re
import pytest
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DIST = os.path.join(ROOT, "site", "dist")
pytestmark = pytest.mark.skipif(not os.path.isdir(DIST), reason="run `npm run build` in site/ first")

def html():
    return open(os.path.join(DIST, "index.html"), encoding="utf-8").read()

def test_all_sections_present_in_nav_order():
    ids = ["hero", "background", "device", "mechanisms", "make", "use", "validation", "limits", "cite"]
    pos = [html().index(f'id="{i}"') for i in ids]
    assert pos == sorted(pos)

def test_every_referenced_asset_exists():
    for ref in re.findall(r'(?:src|data-model)="/ammity-cup/([^"]+)"', html()):
        # Astro's own build output (ModelDialog's TS-using script is not
        # is:inline, so it is bundled to a content-hashed chunk under
        # _astro/, which lives only in site/dist/, never in the committed
        # site/public/). That reference is guaranteed to resolve by the
        # bundler itself, not hand-authored, so it is out of scope for
        # this check, which is about renders/models/etc. actually
        # committed under site/public/.
        if ref.startswith("_astro/"):
            continue
        assert os.path.exists(os.path.join(ROOT, "site", "public", ref)), ref

def test_one_dialog_and_every_scene_linked():
    h = html()
    assert h.count('id="model-dialog"') == 1
    for name in ["flower-low", "flower-low-section", "flower-low-vs-high", "flower-low-mould",
                 "concept-flower-high", "concept-twister", "concept-umbrella", "concept-drawstring",
                 "concept-duckbill", "concept-balloon", "concept-extraction-valve", "rig-artificial-vagina"]:
        assert f"/models/{name}.glb" in h, name

def test_scores_rendered_from_data():
    h = html()
    assert h.count("24/25") >= 2 and "~130" in h and "~54" in h

def test_no_analytics_no_oshwa():
    h = html().lower()
    assert "plausible" not in h and "oshwa" not in h
