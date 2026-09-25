import glob, os, re
from collections import Counter
import pytest
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DIST = os.path.join(ROOT, "site", "dist")
pytestmark = pytest.mark.skipif(not os.path.isdir(DIST), reason="run `npm run build` in site/ first")

def html():
    return open(os.path.join(DIST, "index.html"), encoding="utf-8").read()

def test_all_sections_present_in_nav_order():
    ids = ["hero", "background", "mechanisms", "device", "make", "use", "validation", "limits", "cite"]
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

def test_every_photo_opens_in_dialog_without_zoom():
    h = html()
    assert h.count('id="photo-dialog"') == 1
    photo_img_srcs = re.findall(r'<img\s+src="([^"]*?/photos/[^"]+)"', h)
    assert photo_img_srcs, "no photo <img> tags found"

    # Every photo <img> except the hero photo sits inside a
    # button.photo-open, whose data-full points at that same image,
    # whatever order the button's own attributes come in.
    openers = re.findall(r'<button\b([^>]*)>(.*?)</button>', h, re.S)
    photo_openers = [(attrs, inner) for attrs, inner in openers if 'class="photo-open"' in attrs]
    # One fewer opener than photo <img>s: the hero photo has no opener.
    assert len(photo_openers) == len(photo_img_srcs) - 1, (len(photo_openers), len(photo_img_srcs))
    for attrs, inner in photo_openers:
        full = re.search(r'data-full="([^"]+)"', attrs).group(1)
        img_src = re.search(r'<img\s+src="([^"]+)"', inner).group(1)
        assert full == img_src

    # The hero photo sits in id="hero" as a plain <img>, not inside any
    # link or button. (flower-low.webp appears twice in the page: once as
    # the hero photo, and again, wrapped, among the Mechanisms
    # prototypes, so this has to be a multiset difference, not a set
    # one.)
    wrapped_srcs = Counter(re.search(r'<img\s+src="([^"]+)"', inner).group(1) for _, inner in photo_openers)
    unwrapped = list((Counter(photo_img_srcs) - wrapped_srcs).elements())
    assert unwrapped == [s for s in photo_img_srcs if s.endswith('photos/flower-low.webp')][:1]
    hero_start = h.index('id="hero"')
    hero_end = h.index('</section>', hero_start)
    hero_html = h[hero_start:hero_end]
    fig_m = re.search(r'<figure\b[^>]*class="hero-photo"[^>]*>(.*?)</figure>', hero_html, re.S)
    assert fig_m, "hero-photo figure not found"
    fig_html = fig_m.group(1)
    assert 'photos/flower-low.webp' in fig_html
    assert '<a ' not in fig_html and '<button' not in fig_html

    # No zoom control anywhere: no id/class containing "zoom", and no
    # visible "Zoom" text (case sensitive: "zoom" also occurs, correctly,
    # in the 3D-model dialog's own scroll/pinch hints, which are out of
    # scope here and unrelated to photos).
    assert not re.search(r'\b(?:id|class)="[^"]*zoom[^"]*"', h, re.I)
    assert 'Zoom' not in h

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
