# Design

Engineering reference for the SpaceCup base geometry, the eight mechanism concepts, and the bench-test scoring behind them. Numbers here are transcribed from Keller, K. (2026). *AMMITY*. MSc thesis, ETH Zurich, Global Health Engineering. Not published with this repository. Page references are given as `(thesis p.N)`.

## Base cup requirements

All eight mechanisms share the same base cup geometry, taken from the 2025 BSc thesis that preceded this project (thesis p.9; see [`design-history.md`](design-history.md)).

| Parameter | Value |
|---|---|
| Wall thickness | 2 mm (+/- 0.3 mm) |
| Pull-out stem | at least 15 mm |
| Size | medium, for adult menstruators |
| Rim outer diameter | 41 to 44 mm |
| Length, excluding stem | 45 to 55 mm |
| Capture volume | 20 to 30 mL |
| Air holes | 2 |
| Operation | one-handed, two-finger |

(thesis p.9)

## Mechanisms

Eight mechanism concepts were designed on the base cup. Seven were evaluated in the thesis's functional bench test and reduced-gravity flights (thesis pp.10-11, pp.20-21); the extraction valve is an untested concept documented separately below. Bench scores are the `overall` column of [`../data/ground-test-scores.csv`](../data/ground-test-scores.csv), out of 25.

### Flower Low

Five flexible petals close over the opening, each joined by a silicone string to a pull mechanism integrated into the stem; pulling the strings closes the petals and seals the cup (thesis p.10). Bench score 24/25: sealing 4/5 (minor leakage under extreme handling), containment 18 mL, structural reliability 5/5, usability 5/5, manufacturing 5/5. Its only limitation was minor sealing leakage under extreme handling (thesis pp.20-21). Flower Low was the only prototype flown in reduced gravity; see [`validation.md`](validation.md). Folder: [`../hardware/flower-low/`](../hardware/flower-low/).

### Flower High

The same petal-and-string mechanism as Flower Low, with the petals' base moved closer to the rim for further reach against fluid that pools above the cup before entering it (thesis p.10). Bench score 24/25: sealing 5/5, containment 30 mL, structural reliability 5/5, usability 4/5, manufacturing 5/5. Its main limitation was usability: minor friction during insertion into the artificial vagina (thesis pp.20-21). Folder: [`../hardware/flower-high/`](../hardware/flower-high/).

### Twister

A thin membrane skin, fused to the cup's top and bottom parts, closes into a hyperboloid seal when the bottom part is rotated relative to the top (thesis p.10). Bench score 21/25: sealing 5/5, containment 15 mL, structural reliability 5/5, usability 2/5, manufacturing 4/5. Its main limitation was usability: as the cup is removed, the upper and lower sections pull apart, untwisting the mechanism and reopening the cup (thesis pp.20-21). Folder: [`../hardware/twister/`](../hardware/twister/).

### Umbrella

An inverted-umbrella structure expands into a seal when a central element is pulled downward (thesis p.10). Bench score 16/25: sealing 4/5, containment 22 mL, structural reliability 1/5, usability 3/5, manufacturing 3/5. Its main limitation was structural reliability: the thin umbrella structure failed within the first few activations, after which it could no longer close the cup (thesis pp.20-21). Folder: [`../hardware/umbrella/`](../hardware/umbrella/).

### Balloon

An inflatable membrane attached to the inner wall of the cup rotates upward, to approximately 90 degrees, and seals the opening when a second, stem-integrated balloon is compressed (thesis p.10). The balloon's thin membrane structures could not be manufactured reliably and it was excluded from bench testing (thesis p.20). Folder: [`../hardware/balloon/`](../hardware/balloon/).

### Duckbill

A pressure-difference valve between an upper and a lower chamber opens when the cup is squeezed before removal, transferring fluid to the lower chamber for containment (thesis p.10). Bench score 22/25: sealing 3/5, containment 14 mL, structural reliability 5/5, usability 5/5, manufacturing 4/5. Its main limitation was sealing performance: leakage under moderate disturbance, because the mechanism opens whenever the cup is squeezed (thesis pp.20-21). Folder: [`../hardware/duckbill/`](../hardware/duckbill/).

### Drawstring

A flexible circular lid, folded in half against the inner wall of the cup, is connected to a pull string in the stem; pulling the string draws the lid across the opening, unfolding it to seal the cup (thesis p.10). Bench score 18/25: sealing 1/5, containment 27 mL, structural reliability 5/5, usability 4/5, manufacturing 3/5. Its main limitation was sealing performance, the lowest possible score: the lid's position was too high to close adequately, letting fluid leak out (thesis pp.20-21). Folder: [`../hardware/drawstring/`](../hardware/drawstring/).

### Extraction valve

Not one of the thesis's seven bench-tested mechanisms. The thesis discusses a cup with a syringe or extraction port, letting fluid be removed while the cup stays inserted, as a fundamentally different collection principle worth comparing against the closing-cup approach in future work (thesis p.28; see [`design-history.md`](design-history.md)). The files under [`../hardware/extraction-valve/`](../hardware/extraction-valve/) are an untested concept: they have no bench-test or flight data.

## Scoring

Each bench-tested mechanism was scored on 5 criteria, each on a 1 (not met) to 5 (fully met) scale (thesis Table 1, p.16):

| Criterion | 1 (not met) | 5 (fully met) |
|---|---|---|
| Sealing performance | Immediate, uncontrolled leakage | No leakage observed under any conditions |
| Fluid containment | Well below the 12 mL target volume | Meets or exceeds the 12 mL target volume |
| Structural reliability | Mechanism failed or cracked within the first few activations | No cracks, deformation, or failure after 30 cycles |
| Usability | Insertion, extraction, or reset could not be completed | Full cycle completed easily and intuitively |
| Manufacturability | Could not be fabricated with available methods or materials | Fabricated reliably and consistently with no notable issues |

(thesis Table 1, p.16)

Full score table, from [`../data/ground-test-scores.csv`](../data/ground-test-scores.csv):

| Variant | Sealing | Fluid containment | Containment (mL) | Structural reliability | Usability | Manufacturing | Overall |
|---|---|---|---|---|---|---|---|
| flower-low | 4 | 5 | 18 | 5 | 5 | 5 | 24 |
| flower-high | 5 | 5 | 30 | 5 | 4 | 5 | 24 |
| drawstring | 1 | 5 | 27 | 5 | 4 | 3 | 18 |
| twister | 5 | 5 | 15 | 5 | 2 | 4 | 21 |
| umbrella | 4 | 5 | 22 | 1 | 3 | 3 | 16 |
| duckbill | 3 | 5 | 14 | 5 | 5 | 4 | 22 |

The balloon concept is absent from this table because it could not be manufactured reliably (thesis Table 2, p.20; see [`../data/README.md`](../data/README.md)).

## Why the Flower designs

The functional evaluation identified the two Flower concepts as the most promising designs: both performed well enough, despite room for improvement in sealing and usability, to justify continued development and reduced-gravity testing, while the alternative mechanisms showed more fundamental limitations (thesis p.26). The Flower mechanism is described as the most mature design investigated in the thesis, and its successful operation during the initial reduced-gravity experiments is given as the justification for further development, with future work pursuing two directions: simplifying the Flower for cleanability, manufacturability and operation with medical-grade silicone, and evaluating both Flower Low and Flower High under longer, more representative reduced-gravity conditions (thesis p.30). See [`design-history.md`](design-history.md) for the fuller future-work list.
