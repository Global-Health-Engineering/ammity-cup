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
    for name in ["flower-sections", "flower-low-vs-high", "flower-low-mould",
                 "concept-flower-high", "concept-twister", "concept-umbrella", "concept-drawstring",
                 "concept-duckbill", "concept-balloon", "concept-extraction-valve", "rig-artificial-vagina"]:
        assert f"/models/{name}.glb" in h, name

def test_scores_rendered_from_data():
    h = html()
    assert h.count("24/25") >= 2 and "~130" in h and "~54" in h

def test_no_analytics_no_oshwa():
    h = html().lower()
    assert "plausible" not in h and "oshwa" not in h

def test_every_photo_is_referenced():
    photos_dir = os.path.join(ROOT, "site", "public", "photos")
    photos = sorted(f for f in os.listdir(photos_dir) if f.endswith(".webp"))
    assert photos, "no photos found in site/public/photos"
    h = html()
    for name in photos:
        assert f'/photos/{name}"' in h, name

def test_every_photo_is_zoomable():
    h = html()
    assert h.count('id="photo-dialog"') == 1
    photo_img_srcs = re.findall(r'<img\s+src="([^"]*?/photos/[^"]+)"', h)
    assert photo_img_srcs, "no photo <img> tags found"
    # Every button.photo-open wraps exactly one photo <img>, and its
    # data-full points at that same image, whatever order the button's
    # own attributes come in.
    openers = re.findall(r'<button\b([^>]*)>(.*?)</button>', h, re.S)
    photo_openers = [(attrs, inner) for attrs, inner in openers if 'class="photo-open"' in attrs]
    assert len(photo_openers) == len(photo_img_srcs), (len(photo_openers), len(photo_img_srcs))
    for attrs, inner in photo_openers:
        full = re.search(r'data-full="([^"]+)"', attrs).group(1)
        img_src = re.search(r'<img\s+src="([^"]+)"', inner).group(1)
        assert full == img_src

def test_bench_score_links():
    h = html()
    assert h.count("Bench score: 24/25") >= 2
    val_start = h.index('id="validation"')
    val_end = h.index('id="limits"')
    assert 'id="bench-scores"' in h[val_start:val_end]
    for m in re.finditer(r'Bench score: \d+/\d+', h):
        preceding = h[:m.start()]
        last_open = max(
            (a.start() for a in re.finditer(r'<a\b[^>]*href="#bench-scores"[^>]*>', preceding)),
            default=-1,
        )
        last_close = preceding.rfind('</a>')
        assert last_open != -1 and last_open > last_close, m.group(0)

def test_no_eyebrow_above_section_titles():
    h = html()
    for attrs, content in re.findall(r'<section\b([^>]*)>(.*?)</section>', h, re.S):
        m = re.search(r'id="([^"]+)"', attrs)
        if not m or m.group(1) == "hero":
            continue
        assert 'class="eyebrow"' not in content, m.group(1)

def test_use_section_scoped_to_flower():
    h = html()
    m = re.search(r'<section\b[^>]*id="use"[^>]*>(.*?)</section>', h, re.S)
    assert m, "id=\"use\" section not found"
    h2 = re.search(r'<h2[^>]*>(.*?)</h2>', m.group(1), re.S)
    assert h2 and "Flower" in h2.group(1)
