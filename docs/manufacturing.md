# Manufacturing

How the SpaceCup prototypes were cast, rewritten from the author's injection-moulding guide (`Injection_moulding_guide_AMMITY_KimKeller.pdf`, shipped as [`moulding-guide.pdf`](moulding-guide.pdf)) and from Keller, K. (2026). *AMMITY*. MSc thesis, ETH Zurich, Global Health Engineering. Not published with this repository, thesis pp.11-13 and p.25. This is a laboratory casting process, not the precision-machined, cleanroom moulding a commercial medical device would use.

## Printing the mould

Mould halves are 3D-printed, not machined. Material choice depends on the cure the mould has to survive:

| Cure | Suitable filament |
|---|---|
| Room-temperature cure (Smooth-Sil, Rebound) | PLA, PETG or ABS |
| Heated, 100 °C cure (medical-grade ELASTOSIL) | ASA, to resist thermal deformation at that temperature |

Print settings: 15 % infill, 0.15 to 0.2 mm layer height, 5 wall lines (moulding guide, section B).

## Mould features

- Parting line on the cup's symmetry plane, typically a vertical split.
- A short sprue or funnel at the cup stem, used as the silicone injection channel.
- 2 to 3 vent holes, about 0.5 mm in diameter, near the rim or wherever air is likely to be trapped.
- 3 mm hemispherical alignment keys, to position the mould halves accurately.
- Complex geometries may need additional mould separations to ease demoulding; every internal mould component must be secured against displacement during casting (moulding guide, section A; thesis p.11).

## Silicones used

| Silicone | Role |
|---|---|
| Smooth-Sil 945 | Main cup body |
| Rebound 25 | Flexible components |
| Smooth-Sil 960 | Rigid structural elements |
| ELASTOSIL LR 5040/45 | Medical-grade final prototype, Shore A approximately 45 |

(thesis p.11, p.12)

## Mixing and degassing

Determine the Part A to Part B mixing ratio from the silicone manufacturer's technical data sheet; the ratio varies between materials and must not be assumed to be 1:1. Mix slowly to avoid incorporating air, then transfer to a vacuum chamber and degas until the bubbles have collapsed. Complete mixing, degassing and casting within the silicone's pot life (moulding guide, section D; thesis p.11).

## Injection by syringe

The degassed silicone is transferred to a syringe, about 20 to 50 mL depending on the required volume, and injected slowly and continuously into the sprue, filling the cavity from the injection point toward the vents. Silicone appearing at a vent indicates that region has filled and displaced its air (moulding guide, section E; thesis p.11).

## Curing

| Silicone | Curing time and temperature |
|---|---|
| Smooth-Sil 945 | 6 h |
| ELASTOSIL LR 5040/45 | Manufacturer's rating: 15 min at 165 °C, for a heated industrial mould. The lab used 3D-printed ASA moulds limited to about 100 °C, and found about 2 h at 100 °C sufficient by trial and error |

(thesis p.11, p.12)

## Mixed hardness by cut-and-refill

To combine silicones of different hardness in one SpaceCup, the whole cup was first cast in one silicone. After initial curing, the mould was opened, the sections meant to have a different hardness were cut out, and fresh silicone of the desired hardness was introduced into the resulting cavities before closing the mould again to cure and bond the new material to the existing part (thesis p.12).

## Demoulding

Let the mould and silicone cool before handling, remove the clamps, and separate the mould components carefully. Demould gradually, with particular attention to thin membranes and strings, then remove excess silicone from the sprue, vents and parting lines, and inspect for trapped air, incomplete filling, tears, surface defects and dimensional inconsistencies (moulding guide, section F).

## Epoxy mould coating

A thin epoxy coating can seal microcracks and layer lines in the printed mould cavity, giving a smoother silicone surface, but it needs about 48 h to cure. Because of that curing time, this step was mostly skipped in prototyping (thesis p.11).

## Known defects

From Fig. 9 (thesis p.25): air entrapment during the transfer of silicone from the mixing plate to the injection syringe, demoulding tears from complex enclosed geometries, layer lines and surface irregularities transferred from the 3D-printed mould, and fragile, thin membrane structures (notably the Balloon) that were highly sensitive to material distribution and mould alignment.

The medical-grade ELASTOSIL silicone was too viscous to inject with the syringe setup; it was instead spread by hand directly onto the mould surfaces before the mould halves were clamped together, which limited how completely trapped air could be removed and left more air bubbles in the cured part (thesis p.25).

## Disclaimer

The use of medical-grade silicone does not make the resulting prototype a certified medical device. Medical-device production would require additional controls, validated manufacturing processes, biocompatibility assessment, and appropriate quality-management documentation. The SpaceCup is a research prototype, manufactured in a standard laboratory environment, not a certified medical device.

## Full guide

The full moulding guide is shipped as [`moulding-guide.pdf`](moulding-guide.pdf).
