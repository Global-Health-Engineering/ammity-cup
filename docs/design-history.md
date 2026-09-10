# Design history

Where the SpaceCup's base geometry came from, the concept path from seven mechanisms to a single flown prototype, and the future work the thesis recommends. Sourced from Keller, K. (2026). *AMMITY*. MSc thesis, ETH Zurich, Global Health Engineering. Not published with this repository.

## The base cup

The base cup's geometry, wall thickness, stem length, rim diameter, length and capture volume (see [`design.md`](design.md)) were defined by a 2025 BSc thesis of the same title, by S. Pfeiffer, at ETH Zurich (thesis p.9, p.31). That thesis is unpublished and is cited here only; it is not part of this repository.

## Earlier internal work

Dugué, M. (2024). *Menstrual blood collection in micro-gravity: Parabolic flight results* [Internal document]. This internal document supplied the ingredient selection behind the artificial menstrual fluid recipe used throughout bench and flight testing (thesis p.15); it is not part of this repository.

## The concept path

Seven mechanisms were designed on the shared base cup: Flower Low, Flower High, Twister, Umbrella, Balloon, Duckbill and Drawstring (thesis p.9). All but Balloon, which could not be manufactured reliably, went through the functional bench-test scoring described in [`design.md`](design.md). Of those, only Flower Low was carried forward to reduced-gravity flight testing, as the only fully functional prototype available at the time of the parabolic-flight campaign (thesis p.17); see [`validation.md`](validation.md) and [`flight-protocol.md`](flight-protocol.md). The extraction valve, in [`../hardware/extraction-valve/`](../hardware/extraction-valve/), sits outside this path: it is an early, untested take on one of the alternative collection principles the thesis recommends for future comparison, described below.

## Future work

From the thesis's discussion and conclusions (thesis pp.26-30):

- Simplify the Flower mechanism, with particular emphasis on cleanability, manufacturability, and operation with medical-grade silicone.
- Run longer, more representative reduced-gravity tests, using the more transparent, anatomically representative artificial vagina model developed in this thesis (see [`../hardware/artificial-vagina/`](../hardware/artificial-vagina/)).
- Before further optimising a cup geometry, first study how menstrual-like fluid is transported and distributed within the vagina during prolonged reduced gravity, since the current concept assumes the fluid reaches the cup in a predictable way, which is not yet established.
- Compare the SpaceCup approach against fundamentally different collection principles: a reusable sponge-like absorbent system, a suction-based system, and a cup with a syringe or extraction port that lets fluid be removed while the cup stays inserted. The extraction-valve files in this repository are an early, untested take on the last of these.
- For cleaning, try combining shaking with microwave treatment: placing the cup in a closed container with a small amount of water, shaking it, then microwaving, to loosen trapped residue before heating.
- For manufacturing, sand the mould cavities to reduce transferred layer lines, and avoid very thin features, which were more prone to manufacturing defects and damage.
