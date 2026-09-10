# Validation

What the SpaceCup prototypes were tested against, at 1 G on the bench and in reduced gravity in flight, and what remains untested. Sourced from Keller, K. (2026). *AMMITY*. MSc thesis, ETH Zurich, Global Health Engineering. Not published with this repository, and from [`../data/`](../data/README.md).

## Bench tests at 1 G

All seven mechanisms (the balloon excluded, see [`design.md`](design.md)) were evaluated under standard laboratory conditions, using an anatomical vaginal model injection-moulded from a soft silicone (thesis p.14).

**Fluid recipe:** egg white 30 mL, ketchup 50 mL, sucrose solution (30 % sugar in water) 20 mL. Ketchup gives base viscosity and shear-thinning behaviour, egg white simulates clot-like structures, and the sucrose solution adjusts density (thesis p.15).

**Sealing performance and fluid containment:** each cup was filled with the artificial fluid to capacity, inverted, and visually inspected for leakage at the rim and the sealing mechanism (thesis p.15). The target containment volume was 12 mL, based on the average menstrual fluid volume collected over an 8-hour period, reported in the literature as approximately 2 to 12 mL (thesis p.15, citing Hallberg et al., 1966).

**Structural reliability:** each mechanism was activated repeatedly, 30 cycles, with varying applied force (thesis p.15).

**Usability cycle:** insert the prototype into the vaginal model, fill with artificial fluid, extract, remove the fluid with a syringe, clean the cup, and reset the closing mechanism for the next cycle (thesis p.15).

Each criterion was scored 1 (not met) to 5 (fully met) against the definitions in Table 1 (thesis p.16); see [`design.md`](design.md) for the full scale and the score table from [`../data/ground-test-scores.csv`](../data/ground-test-scores.csv). Both Flower designs scored highest, 24/25.

## Parabolic flight

Reduced-gravity testing was conducted during the Asclepios VI parabolic-flight campaign; see [`flight-protocol.md`](flight-protocol.md) for the full protocol. Only the Flower Low mechanism was flown, because it was the only fully functional prototype available at the time of the campaign (thesis p.17).

The results are qualitative: no fluid volumes were measured in flight (thesis p.22; [`../data/README.md`](../data/README.md)). Summarised from [`../data/flight-questionnaire.csv`](../data/flight-questionnaire.csv) (3 participants):

- 2 of 3 participants reported minor leakage on containment; the third (P2) could not observe containment or fluid behaviour, because the artificial vagina leaked before the parabola began.
- All 3 participants rated activation of the sealing mechanism easy or very easy.
- 2 of 3 rated insertion easy, and 1 rated it moderate; 2 of 3 rated extraction very easy, and 1 rated it easy.
- All 3 reported the procedure felt safe and well controlled.
- 2 of 3 (the ones who could observe it) reported the fluid mostly stable in reduced gravity.

Limitations, from the thesis's own discussion of the flight results (thesis p.22):

- The available reduced-gravity time per parabola was too short for a detailed characterisation of fluid behaviour.
- The small test-fluid volume made fluid movement hard to visualise and prevented a reliable quantitative comparison of containment between the SpaceCup and the tampon.
- The artificial vagina's limited transparency and simplified geometry restricted direct observation of the interaction between fluid, vaginal walls and the SpaceCup.
- Each parabola's short window provided only a limited observation period and did not represent the conditions of wearing a cup for an extended period in continuous microgravity.

## Cleaning

The cleaning assessment (thesis p.23) is summarised in [`use.md`](use.md#cleaning), with colony counts in [`../data/cleaning-colony-counts.csv`](../data/cleaning-colony-counts.csv).

## What is not established

The testing performed does not establish: long-duration wear (all tests were single activation-and-removal cycles, not extended wear), performance under continuous microgravity (parabolic flight gives only short, repeated windows of reduced gravity, not sustained microgravity), or quantitative containment (the flight tests produced qualitative observations, with no measured fluid volumes; thesis p.22).
