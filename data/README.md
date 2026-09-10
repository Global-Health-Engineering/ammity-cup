# data

Bench-test scores, cleaning-assessment colony counts, and anonymised parabolic-flight questionnaire results for the SpaceCup menstrual cup. Every column of every file is documented in [`codebook.csv`](codebook.csv).

## Files

| File                          | Contents                                                                 |
| ------------------------------ | ------------------------------------------------------------------------ |
| `ground-test-scores.csv`      | Functional bench-test scores for 6 prototypes across 5 criteria (6 rows) |
| `cleaning-colony-counts.csv`  | Post-cleaning agar-plate colony counts for 3 methods x 5 cups (15 rows)  |
| `flight-questionnaire.csv`    | Anonymised post-flight questionnaire results for 3 participants (3 rows) |
| `codebook.csv`                | One row per column of every file above: name, type, observed values, description, unit |

## Provenance

All values were transcribed by hand from the author's MSc thesis (Keller, 2026, not published with this repository):

- `ground-test-scores.csv`: Table 2, p.20.
- `cleaning-colony-counts.csv`: Table 3, p.23.
- `flight-questionnaire.csv`: the three post-flight questionnaires completed by the parabolic-flight test participants.

## Anonymisation

Questionnaire participants are identified only as P1-P3. Free-text answers are summarised into the `notes` column in paraphrase, never quoted verbatim, and never name a participant. The original completed questionnaire forms are not published in this repository.

## Headline results

- Both Flower designs (low and high petal count) scored 24/25 in the functional bench test, the highest of any prototype.
- 70 % isopropanol (`ipa-70`) gave the lowest total colony counts of the three cleaning methods, i.e. the best disinfection performance.
- No fluid volumes were measured during the parabolic-flight tests; the flight results are qualitative observations only.

## Flight results are qualitative

The parabolic-flight tests provided a first, qualitative evaluation of the Flower mechanism under reduced gravity. The small test-fluid volume and the limited transparency of the artificial-vagina model prevented reliable quantitative measurement of fluid containment, so no volumes were recorded (thesis p.22).
