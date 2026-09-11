<!-- badges: start -->
[![Licence: CERN-OHL-P v2](https://img.shields.io/badge/hardware-CERN--OHL--P%20v2-873671)](LICENSE-CERN-OHL-P-2.0.md)
[![Licence: CC BY 4.0](https://img.shields.io/badge/docs%20%26%20data-CC%20BY%204.0-457ec1)](LICENSE-CC-BY-4.0.md)
[![Deploy site to GitHub Pages](https://github.com/Global-Health-Engineering/ammity-cup/actions/workflows/deploy-site.yml/badge.svg)](https://github.com/Global-Health-Engineering/ammity-cup/actions/workflows/deploy-site.yml)
<!-- badges: end -->

<br>
<p align="middle">
<img src="site/public/brand/ETH_GHE_logo.svg" width="480" alt="Global Health Engineering, ETH Zurich">
</p>

# SpaceCup (AMMITY)

- **Kim Keller** (ETH Zürich, Global Health Engineering) *design, construction, testing, writing*
- **Marion Dugué** (ETH Zürich, Global Health Engineering) *flight-experiment co-lead, supervision*
- **Jakub Tkaczuk** [![ORCID](https://info.orcid.org/wp-content/uploads/2019/11/orcid_16x16.png) 0000-0001-7997-9423](https://orcid.org/0000-0001-7997-9423) (ETH Zürich, Global Health Engineering) *supervision, page development & maintenance*
- **Elizabeth Tilley** [![ORCID](https://info.orcid.org/wp-content/uploads/2019/11/orcid_16x16.png) 0000-0002-2095-9724](https://orcid.org/0000-0002-2095-9724) (ETH Zürich, Global Health Engineering) *supervision*

**SpaceCup (AMMITY) is an open-source, cast-silicone menstrual cup that seals before extraction, designed for menstruation in reduced gravity.** Seven closing mechanisms were designed on a shared base cup geometry; six were scored in a 1 G bench test, with Flower Low and Flower High scoring highest at 24 out of 25, and Flower Low, the only fully functional prototype available at the time, was flown during the Asclepios VI parabolic-flight campaign. SpaceCup is a research prototype, bench-tested and flown for short reduced-gravity windows, not a certified medical device.

**Full site, with renders, 3D models and documentation, is available [here](https://global-health-engineering.github.io/ammity-cup/).**

## At a glance

| Characteristic           | Description                                                              |
| ------------------------- | -------------------------------------------------------------------------- |
| Mechanisms designed       | 7: Flower Low, Flower High, Twister, Umbrella, Duckbill, Drawstring, Balloon |
| Mechanisms bench-scored   | 6 (Balloon excluded, not reliably manufacturable)                         |
| Best bench score          | Flower Low and Flower High, 24/25                                         |
| Flown                     | Flower Low, Asclepios VI parabolic-flight campaign                        |
| Manufacture                | Cast silicone in 3D-printed moulds                                        |
| CAD                        | Siemens NX source, shipped as STEP                                        |
| Status                     | Research prototype                                                        |

## Quick start

1. Pick a variant in [`hardware/README.md`](hardware/README.md).
2. Print its `mould-stl/`.
3. Cast, following [`docs/manufacturing.md`](docs/manufacturing.md).
4. Use and clean, following [`docs/use.md`](docs/use.md).

## Repository layout

```
hardware/              CERN-OHL-P v2: the cup and mould geometry
├── README.md          Variant table, file map, rename map
├── nx.md              Siemens NX source CAD and the STEP editable format
├── flower-low/         Flown mechanism (step/, stl/, mould-stl/)
├── flower-high/        Bench-tested Flower variant
├── twister/             Bench-tested mechanism
├── umbrella/            Bench-tested mechanism
├── duckbill/            Bench-tested mechanism
├── drawstring/          Bench-tested mechanism
├── balloon/             Not reliably manufacturable, not scored
├── extraction-valve/    Untested concept, outside the bench-tested set
└── artificial-vagina/   Test equipment, not a cup design

docs/                  CC BY 4.0: design, manufacturing, use and validation
├── design.md           Base geometry, the seven mechanisms, bench scoring
├── manufacturing.md    Mould printing and silicone casting
├── use.md              Insertion, activation, extraction, cleaning
├── validation.md       Bench-test and parabolic-flight results
├── flight-protocol.md  The Asclepios VI flight test procedure
├── design-history.md   Where the base geometry and mechanisms came from
└── moulding-guide.pdf  The original injection-moulding guide

data/                  CC BY 4.0: bench, cleaning and flight-questionnaire data
tools/                 CC BY 4.0: scripts that regenerate every render and gate CI
site/                  CC BY 4.0: this repository's GitHub Pages site (Astro)
CITATION.cff           Machine-readable citation metadata
```

## Citation

If you use this hardware, please cite it; see [`CITATION.cff`](CITATION.cff) for the machine-readable record:

> SpaceCup (AMMITY): an open-source menstrual cup that seals before
> extraction, for menstruation in reduced gravity. Kim Keller, Marion
> Dugué, Jakub Tkaczuk, Elizabeth Tilley. ETH Zurich, Global Health
> Engineering. Version 1.0.0. https://github.com/Global-Health-Engineering/ammity-cup

## License

Different parts of this repository are released under different licenses, following standard practice for open-hardware projects:

| Component                                                    | License                                    |
| ------------------------------------------------------------ | ------------------------------------------ |
| Hardware design (STEP, whole-part STL, mould STL in [`hardware/`](hardware/)) | [CERN-OHL-P v2](LICENSE-CERN-OHL-P-2.0.md) |
| Documentation, data, site and tooling                          | [CC BY 4.0](LICENSE-CC-BY-4.0.md)          |

## Acknowledgements

The parabolic-flight experiments were flown by the analogue astronauts of the Asclepios VI mission. Medical-grade silicone was donated by WACKER Chemie AG. Medical input was provided by Dr. Cornelia Betschart. The team also thanks CNES for sharing their expertise in human spaceflight and space medicine.
