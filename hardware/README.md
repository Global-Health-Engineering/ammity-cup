# hardware

Licensed **CERN-OHL-P v2** (see `../LICENSE-CERN-OHL-P-2.0.md`).

## Variants

| Variant | Mechanism | Status | Bench score | Folder |
|---|---|---|---|---|
| flower-low | Five flexible petals, each joined by a silicone string to a pull mechanism in the stem, that close together to seal the opening (thesis p.10) | flown (Asclepios VI) | 24/25 | [`flower-low/`](flower-low/) |
| flower-high | The same petal-and-string mechanism as Flower Low, with the petals' base moved closer to the rim for further reach against fluid pooled above the cup (thesis p.10) | bench-tested | 24/25 | [`flower-high/`](flower-high/) |
| twister | A thin membrane skin that forms a hyperboloid seal when the cup's bottom part is rotated against the top (thesis p.10) | bench-tested | 21/25 | [`twister/`](twister/) |
| umbrella | An inverted-umbrella structure that expands into a seal when a central element is pulled downward (thesis p.10) | bench-tested | 16/25 | [`umbrella/`](umbrella/) |
| balloon | An inflatable membrane on the cup wall that rotates upward to seal the opening when a stem-integrated balloon is compressed (thesis p.10) | not reliably manufacturable | not scored (excluded, thesis p.20) | [`balloon/`](balloon/) |
| duckbill | A pressure-difference valve between an upper and lower chamber, opened by squeezing the cup before removal (thesis p.10) | bench-tested | 22/25 | [`duckbill/`](duckbill/) |
| drawstring | A flexible lid, folded against the inner wall, drawn across the opening by a stem-integrated pull string (thesis p.10) | bench-tested | 18/25 | [`drawstring/`](drawstring/) |
| extraction-valve | A valve-and-button assembly intended to withdraw fluid through a port while the cup stays inserted; an eighth, later concept, not one of the thesis's seven mechanisms and not tested or described in the thesis (see [`../docs/design.md`](../docs/design.md)) | untested concept | not scored | [`extraction-valve/`](extraction-valve/) |
| artificial-vagina | Two test models: the self-made model here, cast from the printed mould, was used for the 1 G bench tests (thesis pp.14-15); the flights used a separate, store-bought model, not shipped in this repository (thesis p.17). The file names ("parabolicflight_vagina") are the author's own and predate the flight/bench distinction | test equipment | not applicable | [`artificial-vagina/`](artificial-vagina/) |

Bench scores are the `overall` column of [`../data/ground-test-scores.csv`](../data/ground-test-scores.csv) (out of 25); see [`../docs/design.md`](../docs/design.md) for the full breakdown by criterion.

## What is in each folder

- `step/` holds the cup and mould B-rep, editable.
- `stl/` holds the whole cup and whole mould as single meshes, for viewing and CAM; print from `mould-stl/`, which holds the split, print-ready pieces.
- `mould-stl/` holds the print-ready mould pieces.

## Which files are the cup and which are the mould

STEP files with `mould` in the name are moulds. The rest are the cast parts. Some cast parts are modelled as halves rather than a single closed solid: `umbrella/menstrual-cup-medium-without-umbrella.step` and `duckbill/duckbill-half-withrim.step`.

## Known gaps

- The balloon membrane exists only as a mould (`balloon-top-mould.step`); the balloon part itself could not be manufactured reliably and was excluded from bench testing (thesis p.20).
- The drawstring lid is modelled flat, as moulded, not folded against the inner wall as it sits in the cup. The concept render shows it that way: flat, beside the cup.
- `flower-high/step/flower-cup-withrim-higher.step` is one fused solid (cup, petal disc, petals and strings together). The renders colour its petals and strings by a geometric rule calibrated on Flower Low's separate solids (`tools/parts.py`, `FaceSplit`), not by solids in the file.
- `flower-low/step/flower-cup-withrim-part.step` holds 6 solids: two cup-body halves split at the mould parting plane, two small rim pieces, a petal disc, and the petals-with-strings solid.
- `flower-low` also contains a `flower-stopper` (`flower-stopper.step`, `flower-stopper-mould.step`), which the thesis does not describe.
- The extraction valve is an eighth, later concept: it is not one of the thesis's seven designed mechanisms, was not tested, and is not described in the thesis; it has no bench-test or flight data.
- In the Flower Low and Flower High CAD, the pull strings are modelled straight, as cast (the mould cores run to the same length). In the cast cup, each petal's string joins the pull mechanism in the stem (thesis p.10). The renders show this as-cast, straight-string geometry, not the strings pulled taut.
- The drawstring's pull-string tabs are small and sit inside the rim, so they are barely visible in the render.

## Printing the moulds

The moulds print in ASA when the silicone needs a heated, 100 °C cure (medical-grade ELASTOSIL), or in PLA, PETG or ABS for room-temperature-cured silicones such as Smooth-Sil and Rebound. See [`../docs/manufacturing.md`](../docs/manufacturing.md) for material selection, mould features, mixing, injection, curing times and known defects.

## Units

Every STL and STEP file here is in millimetres, checked in CI:

```bash
python3 tools/verify_units.py "hardware/*/mould-stl/*.stl" "hardware/*/stl/*.stl"
```

STEP files declare `SI_UNIT(.MILLI.,.METRE.)` and need no conversion.

## Rename map

The thesis uses the author's original names. This repository renames every shipped file to a consistent, lower-case, hyphenated scheme. The table below is the full old to new mapping.

| Original name (thesis, CAD export) | In this repository |
|---|---|
| `Flower Low Cup/Print Flower/flower_cup_withrim_mold_bottomleft_m.stl` | `flower-low/mould-stl/flower-cup-withrim-mould-bottomleft.stl` |
| `Flower Low Cup/Print Flower/flower_cup_withrim_mold_bottomright_m.stl` | `flower-low/mould-stl/flower-cup-withrim-mould-bottomright.stl` |
| `Flower Low Cup/Print Flower/flower_cup_withrim_mold_middleleft_m.stl` | `flower-low/mould-stl/flower-cup-withrim-mould-middleleft.stl` |
| `Flower Low Cup/Print Flower/flower_cup_withrim_mold_middleright_m.stl` | `flower-low/mould-stl/flower-cup-withrim-mould-middleright.stl` |
| `Flower Low Cup/Print Flower/flower_cup_withrim_mold_topleft_m.stl` | `flower-low/mould-stl/flower-cup-withrim-mould-topleft.stl` |
| `Flower Low Cup/Print Flower/flower_cup_withrim_mold_topright_m.stl` | `flower-low/mould-stl/flower-cup-withrim-mould-topright.stl` |
| `Flower Low Cup/Print Flower/flower_stopper_mold_bottom_m.stl` | `flower-low/mould-stl/flower-stopper-mould-bottom.stl` |
| `Flower Low Cup/Print Flower/flower_stopper_mold_top_m.stl` | `flower-low/mould-stl/flower-stopper-mould-top.stl` |
| `Flower Low Cup/Step files/flower_cup_withrim_mold_m.stp` | `flower-low/step/flower-cup-withrim-mould.step` |
| `Flower Low Cup/Step files/flower_cup_withrim_part_m.stp` | `flower-low/step/flower-cup-withrim-part.step` |
| `Flower Low Cup/Step files/flower_stopper_m.stp` | `flower-low/step/flower-stopper.step` |
| `Flower Low Cup/Step files/flower_stopper_mold_m.stp` | `flower-low/step/flower-stopper-mould.step` |
| `Flower Low Cup/Stl files/flower_cup_withrim_mold_m.stl` | `flower-low/stl/flower-cup-withrim-mould.stl` |
| `Flower Low Cup/Stl files/flower_cup_withrim_part_m.stl` | `flower-low/stl/flower-cup-withrim-part.stl` |
| `Flower Low Cup/Stl files/flower_stopper_m.stl` | `flower-low/stl/flower-stopper.stl` |
| `Flower Low Cup/Stl files/flower_stopper_mold_m.stl` | `flower-low/stl/flower-stopper-mould.stl` |
| `Flower High Cup/Print Flower high/flower_cup_withrim_higher_mold_inleft.stl` | `flower-high/mould-stl/flower-cup-withrim-higher-mould-inleft.stl` |
| `Flower High Cup/Print Flower high/flower_cup_withrim_higher_mold_inright.stl` | `flower-high/mould-stl/flower-cup-withrim-higher-mould-inright.stl` |
| `Flower High Cup/Print Flower high/flower_cup_withrim_higher_mold_outbottomleft.stl` | `flower-high/mould-stl/flower-cup-withrim-higher-mould-outbottomleft.stl` |
| `Flower High Cup/Print Flower high/flower_cup_withrim_higher_mold_outbottomright.stl` | `flower-high/mould-stl/flower-cup-withrim-higher-mould-outbottomright.stl` |
| `Flower High Cup/Print Flower high/flower_cup_withrim_higher_mold_outtopleft.stl` | `flower-high/mould-stl/flower-cup-withrim-higher-mould-outtopleft.stl` |
| `Flower High Cup/Print Flower high/flower_cup_withrim_higher_mold_outtopright.stl` | `flower-high/mould-stl/flower-cup-withrim-higher-mould-outtopright.stl` |
| `Flower High Cup/Step files/flower_cup_withrim_higher_m.stp` | `flower-high/step/flower-cup-withrim-higher.step` |
| `Flower High Cup/Step files/flower_cup_withrim_higher_mold_m.stp` | `flower-high/step/flower-cup-withrim-higher-mould.step` |
| `Flower High Cup/Stl files/flower_cup_withrim_higher_m.stl` | `flower-high/stl/flower-cup-withrim-higher.stl` |
| `Flower High Cup/Stl files/flower_cup_withrim_higher_mold_m.stl` | `flower-high/stl/flower-cup-withrim-higher-mould.stl` |
| `Twister Cup/Print Twister/Twister_Cup_Top2_bottom.stl` | `twister/mould-stl/twister-cup-top2-bottom.stl` |
| `Twister Cup/Print Twister/Twister_Cup_Top2_middle.stl` | `twister/mould-stl/twister-cup-top2-middle.stl` |
| `Twister Cup/Print Twister/Twister_Cup_Top2_middleoutside.stl` | `twister/mould-stl/twister-cup-top2-middleoutside.stl` |
| `Twister Cup/Print Twister/Twister_Cup_Top2_top.stl` | `twister/mould-stl/twister-cup-top2-top.stl` |
| `Twister Cup/Print Twister/twister_cup_bottom_3_withdent_inleft.stl` | `twister/mould-stl/twister-cup-bottom-3-withdent-inleft.stl` |
| `Twister Cup/Print Twister/twister_cup_bottom_3_withdent_inright.stl` | `twister/mould-stl/twister-cup-bottom-3-withdent-inright.stl` |
| `Twister Cup/Print Twister/twister_cup_bottom_3_withdent_outleft.stl` | `twister/mould-stl/twister-cup-bottom-3-withdent-outleft.stl` |
| `Twister Cup/Print Twister/twister_cup_bottom_3_withdent_outright.stl` | `twister/mould-stl/twister-cup-bottom-3-withdent-outright.stl` |
| `Twister Cup/Print Twister/twister_skin_mold_1.stl` | `twister/mould-stl/twister-skin-mould-1.stl` |
| `Twister Cup/Print Twister/twister_skin_mold_2.stl` | `twister/mould-stl/twister-skin-mould-2.stl` |
| `Twister Cup/Print Twister/twister_skin_mold_3.stl` | `twister/mould-stl/twister-skin-mould-3.stl` |
| `Twister Cup/Print Twister/twister_skin_mold_4.stl` | `twister/mould-stl/twister-skin-mould-4.stl` |
| `Twister Cup/Print Twister/twister_skin_mold_5.stl` | `twister/mould-stl/twister-skin-mould-5.stl` |
| `Twister Cup/Print Twister/twister_skin_mold_6.stl` | `twister/mould-stl/twister-skin-mould-6.stl` |
| `Twister Cup/Print Twister/twister_skin_mold_insideleft.stl` | `twister/mould-stl/twister-skin-mould-insideleft.stl` |
| `Twister Cup/Print Twister/twister_skin_mold_insideright.stl` | `twister/mould-stl/twister-skin-mould-insideright.stl` |
| `Twister Cup/Step files/Twister_Cup_Top_m.stp` | `twister/step/twister-cup-top.step` |
| `Twister Cup/Step files/Twister_Cup_Top_mold.stp` | `twister/step/twister-cup-top-mould.step` |
| `Twister Cup/Step files/twister_cup_bottom_withdent.stp` | `twister/step/twister-cup-bottom-withdent.step` |
| `Twister Cup/Step files/twister_cup_bottom_withdent_mold.stp` | `twister/step/twister-cup-bottom-withdent-mould.step` |
| `Twister Cup/Step files/twister_skin.stp` | `twister/step/twister-skin.step` |
| `Twister Cup/Step files/twister_skin_mold.stp` | `twister/step/twister-skin-mould.step` |
| `Twister Cup/Stl files/Twister_Cup_Top_m.stl` | `twister/stl/twister-cup-top.stl` |
| `Twister Cup/Stl files/Twister_Cup_Top_mold.stl` | `twister/stl/twister-cup-top-mould.stl` |
| `Twister Cup/Stl files/twister_cup_bottom_withdent.stl` | `twister/stl/twister-cup-bottom-withdent.stl` |
| `Twister Cup/Stl files/twister_cup_bottom_withdent_mold.stl` | `twister/stl/twister-cup-bottom-withdent-mould.stl` |
| `Twister Cup/Stl files/twister_skin.stl` | `twister/stl/twister-skin.stl` |
| `Twister Cup/Stl files/twister_skin_mold.stl` | `twister/stl/twister-skin-mould.stl` |
| `Umbrella Cup/Print Umbrella/menstrual_cup_medium_without_umbrella_mold_insideleft.stl` | `umbrella/mould-stl/menstrual-cup-medium-without-umbrella-mould-insideleft.stl` |
| `Umbrella Cup/Print Umbrella/menstrual_cup_medium_without_umbrella_mold_insideright.stl` | `umbrella/mould-stl/menstrual-cup-medium-without-umbrella-mould-insideright.stl` |
| `Umbrella Cup/Print Umbrella/menstrual_cup_medium_without_umbrella_mold_outsideleft_m.stl` | `umbrella/mould-stl/menstrual-cup-medium-without-umbrella-mould-outsideleft.stl` |
| `Umbrella Cup/Print Umbrella/menstrual_cup_medium_without_umbrella_mold_outsideright_m.stl` | `umbrella/mould-stl/menstrual-cup-medium-without-umbrella-mould-outsideright.stl` |
| `Umbrella Cup/Print Umbrella/umbrella_contain_silicone_mold_inside.stl` | `umbrella/mould-stl/umbrella-contain-silicone-mould-inside.stl` |
| `Umbrella Cup/Print Umbrella/umbrella_contain_silicone_mold_outsideleft.stl` | `umbrella/mould-stl/umbrella-contain-silicone-mould-outsideleft.stl` |
| `Umbrella Cup/Print Umbrella/umbrella_contain_silicone_mold_outsideright.stl` | `umbrella/mould-stl/umbrella-contain-silicone-mould-outsideright.stl` |
| `Umbrella Cup/Print Umbrella/umbrella_top_2_open_Full_mold_top_m.stl` | `umbrella/mould-stl/umbrella-top-2-open-full-mould-top.stl` |
| `Umbrella Cup/Print Umbrella/umbrella_top_2_open_Full_mold_u1_m.stl` | `umbrella/mould-stl/umbrella-top-2-open-full-mould-u1.stl` |
| `Umbrella Cup/Print Umbrella/umbrella_top_2_open_Full_mold_u2_m.stl` | `umbrella/mould-stl/umbrella-top-2-open-full-mould-u2.stl` |
| `Umbrella Cup/Print Umbrella/umbrella_top_2_open_Full_mold_u3_m.stl` | `umbrella/mould-stl/umbrella-top-2-open-full-mould-u3.stl` |
| `Umbrella Cup/Print Umbrella/umbrella_top_2_open_Full_mold_u4_m.stl` | `umbrella/mould-stl/umbrella-top-2-open-full-mould-u4.stl` |
| `Umbrella Cup/Step files/menstrual_cup_medium_without_umbrella_m.stp` | `umbrella/step/menstrual-cup-medium-without-umbrella.step` |
| `Umbrella Cup/Step files/menstrual_cup_medium_without_umbrella_mold_m.stp` | `umbrella/step/menstrual-cup-medium-without-umbrella-mould.step` |
| `Umbrella Cup/Step files/umbrella_contain_silicone.stp` | `umbrella/step/umbrella-contain-silicone.step` |
| `Umbrella Cup/Step files/umbrella_contain_silicone_mold.stp` | `umbrella/step/umbrella-contain-silicone-mould.step` |
| `Umbrella Cup/Step files/umbrella_top_open_Full_m.stp` | `umbrella/step/umbrella-top-open-full.step` |
| `Umbrella Cup/Step files/umbrella_top_open_Full_mold_m.stp` | `umbrella/step/umbrella-top-open-full-mould.step` |
| `Umbrella Cup/Step files/umbrella_top_open_Full_wings_mold.stp` | `umbrella/step/umbrella-top-open-full-wings-mould.step` |
| `Umbrella Cup/Stl files/menstrual_cup_medium_without_umbrella_m.stl` | `umbrella/stl/menstrual-cup-medium-without-umbrella.stl` |
| `Umbrella Cup/Stl files/menstrual_cup_medium_without_umbrella_mold_m.stl` | `umbrella/stl/menstrual-cup-medium-without-umbrella-mould.stl` |
| `Umbrella Cup/Stl files/umbrella_contain_silicone.stl` | `umbrella/stl/umbrella-contain-silicone.stl` |
| `Umbrella Cup/Stl files/umbrella_contain_silicone_mold.stl` | `umbrella/stl/umbrella-contain-silicone-mould.stl` |
| `Umbrella Cup/Stl files/umbrella_top_open_Full_m.stl` | `umbrella/stl/umbrella-top-open-full.stl` |
| `Umbrella Cup/Stl files/umbrella_top_open_Full_mold_m.stl` | `umbrella/stl/umbrella-top-open-full-mould.stl` |
| `Umbrella Cup/Stl files/umbrella_top_open_Full_wings_mold.stl` | `umbrella/stl/umbrella-top-open-full-wings-mould.stl` |
| `Drawstring Cup/Stl files/Drawsting.stl` | `drawstring/stl/drawstring.stl` |
| `Drawstring Cup/Stl files/Drawsting_mold.stl` | `drawstring/stl/drawstring-mould.stl` |
| `Drawstring Cup/Print Drawstring/Drawsting2_mold_bottom.stl` | `drawstring/mould-stl/drawstring2-mould-bottom.stl` |
| `Drawstring Cup/Print Drawstring/Drawsting2_mold_top.stl` | `drawstring/mould-stl/drawstring2-mould-top.stl` |
| `Drawstring Cup/Print Drawstring/menstrual_cup_medium_drawstring5_inbottomleft.stl` | `drawstring/mould-stl/menstrual-cup-medium-drawstring5-inbottomleft.stl` |
| `Drawstring Cup/Print Drawstring/menstrual_cup_medium_drawstring5_inbottomright.stl` | `drawstring/mould-stl/menstrual-cup-medium-drawstring5-inbottomright.stl` |
| `Drawstring Cup/Print Drawstring/menstrual_cup_medium_drawstring5_inmiddle.stl` | `drawstring/mould-stl/menstrual-cup-medium-drawstring5-inmiddle.stl` |
| `Drawstring Cup/Print Drawstring/menstrual_cup_medium_drawstring5_intopleft.stl` | `drawstring/mould-stl/menstrual-cup-medium-drawstring5-intopleft.stl` |
| `Drawstring Cup/Print Drawstring/menstrual_cup_medium_drawstring5_intopright.stl` | `drawstring/mould-stl/menstrual-cup-medium-drawstring5-intopright.stl` |
| `Drawstring Cup/Print Drawstring/menstrual_cup_medium_drawstring5_outleft.stl` | `drawstring/mould-stl/menstrual-cup-medium-drawstring5-outleft.stl` |
| `Drawstring Cup/Print Drawstring/menstrual_cup_medium_drawstring5_outright.stl` | `drawstring/mould-stl/menstrual-cup-medium-drawstring5-outright.stl` |
| `Drawstring Cup/Step files/Drawsting.stp` | `drawstring/step/drawstring.step` |
| `Drawstring Cup/Step files/Drawsting_mold.stp` | `drawstring/step/drawstring-mould.step` |
| `Drawstring Cup/Step files/menstrual_cup_medium_drawstring.stp` | `drawstring/step/menstrual-cup-medium-drawstring.step` |
| `Drawstring Cup/Step files/menstrual_cup_medium_drawstring_mold.stp` | `drawstring/step/menstrual-cup-medium-drawstring-mould.step` |
| `Drawstring Cup/Stl files/menstrual_cup_medium_drawstring.stl` | `drawstring/stl/menstrual-cup-medium-drawstring.stl` |
| `Drawstring Cup/Stl files/menstrual_cup_medium_drawstring_mold.stl` | `drawstring/stl/menstrual-cup-medium-drawstring-mould.stl` |
| `Duckbill Cup/Print Duckbill/duckbill2_half_withrim_insidebottom.stl` | `duckbill/mould-stl/duckbill2-half-withrim-insidebottom.stl` |
| `Duckbill Cup/Print Duckbill/duckbill2_half_withrim_insidetop.stl` | `duckbill/mould-stl/duckbill2-half-withrim-insidetop.stl` |
| `Duckbill Cup/Print Duckbill/duckbill2_half_withrim_outsideleft.stl` | `duckbill/mould-stl/duckbill2-half-withrim-outsideleft.stl` |
| `Duckbill Cup/Print Duckbill/duckbill2_half_withrim_outsideright.stl` | `duckbill/mould-stl/duckbill2-half-withrim-outsideright.stl` |
| `Duckbill Cup/Step files/duckbill_half_withrim.stp` | `duckbill/step/duckbill-half-withrim.step` |
| `Duckbill Cup/Step files/duckbill_half_withrim_mold.stp` | `duckbill/step/duckbill-half-withrim-mould.step` |
| `Duckbill Cup/Stl files/duckbill_half_withrim.stl` | `duckbill/stl/duckbill-half-withrim.stl` |
| `Duckbill Cup/Stl files/duckbill_half_withrim_mold.stl` | `duckbill/stl/duckbill-half-withrim-mould.stl` |
| `Balloon Cup/Stl files/Balloon_Top_mold.stl` | `balloon/stl/balloon-top-mould.stl` |
| `Balloon Cup/Print Balloon (with pipe)/Balloon_Top_1_Mold1_outsideleft.stl` | `balloon/mould-stl/balloon-top-1-mould1-outsideleft.stl` |
| `Balloon Cup/Print Balloon (with pipe)/Balloon_Top_1_Mold1_outsideright.stl` | `balloon/mould-stl/balloon-top-1-mould1-outsideright.stl` |
| `Balloon Cup/Print Balloon (with pipe)/Balloon_Top_2_Mold_insideleft.stl` | `balloon/mould-stl/balloon-top-2-mould-insideleft.stl` |
| `Balloon Cup/Print Balloon (with pipe)/Balloon_Top_2_Mold_insidemiddle.stl` | `balloon/mould-stl/balloon-top-2-mould-insidemiddle.stl` |
| `Balloon Cup/Print Balloon (with pipe)/Balloon_Top_2_Mold_insideright.stl` | `balloon/mould-stl/balloon-top-2-mould-insideright.stl` |
| `Balloon Cup/Print Balloon (with pipe)/balloon_pipe1_mold_inside.stl` | `balloon/mould-stl/balloon-pipe1-mould-inside.stl` |
| `Balloon Cup/Print Balloon (with pipe)/balloon_pipe1_mold_outsideleft.stl` | `balloon/mould-stl/balloon-pipe1-mould-outsideleft.stl` |
| `Balloon Cup/Print Balloon (with pipe)/balloon_pipe1_mold_outsideright.stl` | `balloon/mould-stl/balloon-pipe1-mould-outsideright.stl` |
| `Balloon Cup/Print Balloon (with pipe)/menstrual_cup_medium_without_balloon_mold_inbottomleft.stl` | `balloon/mould-stl/menstrual-cup-medium-without-balloon-mould-inbottomleft.stl` |
| `Balloon Cup/Print Balloon (with pipe)/menstrual_cup_medium_without_balloon_mold_inbottomright.stl` | `balloon/mould-stl/menstrual-cup-medium-without-balloon-mould-inbottomright.stl` |
| `Balloon Cup/Print Balloon (with pipe)/menstrual_cup_medium_without_balloon_mold_intopleft.stl` | `balloon/mould-stl/menstrual-cup-medium-without-balloon-mould-intopleft.stl` |
| `Balloon Cup/Print Balloon (with pipe)/menstrual_cup_medium_without_balloon_mold_intopright.stl` | `balloon/mould-stl/menstrual-cup-medium-without-balloon-mould-intopright.stl` |
| `Balloon Cup/Print Balloon (with pipe)/menstrual_cup_medium_without_balloon_mold_ousideleft.stl` | `balloon/mould-stl/menstrual-cup-medium-without-balloon-mould-outsideleft.stl` |
| `Balloon Cup/Print Balloon (with pipe)/menstrual_cup_medium_without_balloon_mold_outsideright.stl` | `balloon/mould-stl/menstrual-cup-medium-without-balloon-mould-outsideright.stl` |
| `Balloon Cup/Step files/Balloon_Top_mold.stp` | `balloon/step/balloon-top-mould.step` |
| `Balloon Cup/Step files/balloon_pipe.stp` | `balloon/step/balloon-pipe.step` |
| `Balloon Cup/Step files/balloon_pipe_mold.stp` | `balloon/step/balloon-pipe-mould.step` |
| `Balloon Cup/Step files/menstrual_cup_medium_without_balloon.stp` | `balloon/step/menstrual-cup-medium-without-balloon.step` |
| `Balloon Cup/Step files/menstrual_cup_medium_without_balloon_mold.stp` | `balloon/step/menstrual-cup-medium-without-balloon-mould.step` |
| `Balloon Cup/Stl files/balloon_pipe.stl` | `balloon/stl/balloon-pipe.stl` |
| `Balloon Cup/Stl files/balloon_pipe_mold.stl` | `balloon/stl/balloon-pipe-mould.stl` |
| `Balloon Cup/Stl files/menstrual_cup_medium_without_balloon.stl` | `balloon/stl/menstrual-cup-medium-without-balloon.stl` |
| `Balloon Cup/Stl files/menstrual_cup_medium_without_balloon_mold.stl` | `balloon/stl/menstrual-cup-medium-without-balloon-mould.stl` |
| `Extraction Valve/Print valve and button/cup_valve_button_left2.stl` | `extraction-valve/mould-stl/cup-valve-button-left2.stl` |
| `Extraction Valve/Print valve and button/cup_valve_button_right2.stl` | `extraction-valve/mould-stl/cup-valve-button-right2.stl` |
| `Extraction Valve/Print valve and button/menstrual_cup_valve_inside.stl` | `extraction-valve/mould-stl/menstrual-cup-valve-inside.stl` |
| `Extraction Valve/Print valve and button/menstrual_cup_valve_outleft.stl` | `extraction-valve/mould-stl/menstrual-cup-valve-outleft.stl` |
| `Extraction Valve/Print valve and button/menstrual_cup_valve_outright.stl` | `extraction-valve/mould-stl/menstrual-cup-valve-outright.stl` |
| `Extraction Valve/Step files/cup_valve_button.stp` | `extraction-valve/step/cup-valve-button.step` |
| `Extraction Valve/Step files/cup_valve_button_mold.stp` | `extraction-valve/step/cup-valve-button-mould.step` |
| `Extraction Valve/Step files/menstrual_cup_valve.stp` | `extraction-valve/step/menstrual-cup-valve.step` |
| `Extraction Valve/Step files/menstrual_cup_valve_mold.stp` | `extraction-valve/step/menstrual-cup-valve-mould.step` |
| `Extraction Valve/Stl files/cup_valve_button.stl` | `extraction-valve/stl/cup-valve-button.stl` |
| `Extraction Valve/Stl files/cup_valve_button_mold.stl` | `extraction-valve/stl/cup-valve-button-mould.stl` |
| `Extraction Valve/Stl files/menstrual_cup_valve.stl` | `extraction-valve/stl/menstrual-cup-valve.stl` |
| `Extraction Valve/Stl files/menstrual_cup_valve_mold.stl` | `extraction-valve/stl/menstrual-cup-valve-mould.stl` |
| `Artificial Vagina/Print Vagina/parabolicflight_vagina2_inleft.stl` | `artificial-vagina/mould-stl/parabolicflight-vagina2-inleft.stl` |
| `Artificial Vagina/Print Vagina/parabolicflight_vagina2_inright.stl` | `artificial-vagina/mould-stl/parabolicflight-vagina2-inright.stl` |
| `Artificial Vagina/Print Vagina/parabolicflight_vagina2_outsideleft.stl` | `artificial-vagina/mould-stl/parabolicflight-vagina2-outsideleft.stl` |
| `Artificial Vagina/Print Vagina/parabolicflight_vagina2_outsideright.stl` | `artificial-vagina/mould-stl/parabolicflight-vagina2-outsideright.stl` |
| `Artificial Vagina/Step files/parabolicflight_vagina.stp` | `artificial-vagina/step/parabolicflight-vagina.step` |
| `Artificial Vagina/Step files/parabolicflight_vagina_mold.stp` | `artificial-vagina/step/parabolicflight-vagina-mould.step` |
| `Artificial Vagina/Stl files/parabolicflight_vagina.stl` | `artificial-vagina/stl/parabolicflight-vagina.stl` |
| `Artificial Vagina/Stl files/parabolicflight_vagina_mold.stl` | `artificial-vagina/stl/parabolicflight-vagina-mould.stl` |
