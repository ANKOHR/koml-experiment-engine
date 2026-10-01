# KOML Experiment Engine

`kee2` formulates hypotheses, evaluates recorded binary trials and updates explicit beliefs. Python 3.10+, CPU only, standard library runtime, local files only. No network, language models or GPU packages.

## Quickstart

```powershell
python -m pip install --no-deps --no-build-isolation -e .
kee2 fixtures --out demo
kee2 run --input demo
kee2 report --format md
python -m pytest -q
```

If the Python user Scripts directory is outside PATH on Windows, use `python -m koml_experiment_engine.cli` in place of `kee2`, or add that Scripts directory to the current shell PATH.

The 200-record fixture plants ten hypotheses with 20 observations each. Five have 18 successes and five have eight. Hand arithmetic gives 130 successes, 70 failures, five accepted and five rejected. `demo/expectations.json` is separate hand-computed evidence, never read by the engine. No randomness is used, so a seed is not applicable. The same inputs produce byte-identical results and reports, without timestamps or machine-specific absolute source paths.

For the tiny five-record version: `kee2 run --input examples` then `kee2 report`. This example is synthetic, too. To try real data, copy its JSON into a separate directory, set document and record `synthetic` to false, set `entered_by` to `Henry`, and enter actual trials yourself. Do not ship real trial data in this repository.

## Commands and examples

- `kee2 fixtures --out demo`: writes labelled trials, independent expectations and a synthetic header in LABEL.md.
- `kee2 run --input demo --results results.json`: validates all input documents, evaluates acceptance and writes exact results atomically.
- `kee2 report --results results.json --format json --out report.json`: renders JSON or Markdown, including provenance. Without `--out`, writes to stdout.
- `kee2 hypothesis --id h1 --claim "Recorded success rate reaches 75 percent" --threshold 3/4 --minimum-trials 10`: emits a proposed, hypothetical hypothesis object to paste into an input document. It does not run an intervention.
- `kee2 belief --results results.json`: displays the stored belief updates with full provenance and model limits.

Each command has `--help` and an example. Default results are stored at `.kee2-results.json` in the working directory. Reports require a prior run. Re-running replaces the selected result file after successful validation.

## Input format reference

See `examples/five-records.json` for a complete editable document. Only UTF-8 JSON is accepted. A directory can hold multiple JSON documents; filenames are processed in sorted order. `expectations.json` and Markdown labelling files are excluded by documented convention. Other file formats are rejected, rather than silently parsed. Keep unrelated JSON outside the input directory.

Required document fields:

| Field | Meaning |
| --- | --- |
| synthetic | Boolean provenance declaration |
| entered_by | `fixture generator` for synthetic data, `Henry` for real data |
| as_of | Explicit ISO date, YYYY-MM-DD; maximum permitted trial date |
| hypotheses | Array of hypothesis objects |
| records | Array of recorded binary trial objects |

Hypothesis fields: `id`, `claim`, `threshold` (rational string between zero and one), `minimum_trials` (positive integer), `prior_alpha` and `prior_beta` (positive integers). All fields are required, unknown fields are errors. Each record requires `id`, `hypothesis_id`, `date`, `success` (strict boolean), `note` (text, may be empty), and `synthetic` (must match its document). Each record references a hypothesis declared in its own document. Hypothesis and record IDs must be globally unique.

Text supports Unicode and Windows paths. IDs and claims must be nonempty and at most 10,000 characters; notes have the same maximum. U+2014 is rejected in rendered text fields. Integers are limited to 1,000,000. Negative values, invalid dates, future dates beyond declared `as_of`, duplicate IDs, undeclared references and schema drift are errors. Dates use the explicit cutoff rather than today's clock, preserving determinism. Changing the cutoff is an operator action; the engine does not certify whether entered dates are truthful.

Acceptance uses recorded success fraction >= threshold with at least `minimum_trials`. Below that count the verdict is `insufficient`, including zero trials. Exact rates and beliefs use rational strings, without floating-point rounding. Zero trials have displayed rate `0` by convention, with an insufficient verdict. Under the declared Beta-Bernoulli model, posterior mean = (prior_alpha + successes) / (prior_alpha + prior_beta + trials). This is a model assumption, not empirical calibration. Reports list contributing record IDs so figures can be traced to input records.

There are no amount fields, savings fields or automatic data collection. Such fields are rejected as schema drift. A run evaluates supplied trial results; it does not execute external interventions.

## Architecture

```text
local JSON -> CLI loader -> core validation and exact arithmetic
                                     |
                                     v
                           atomic local results JSON
                                     |
                                     v
                          report renderer -> stdout/file
fixture generator -> labelled inputs + independent expectations
```

`core.py` contains pure functions with no I/O. `fixtures.py` builds synthetic data. `cli.py` owns parsing, filesystem operations and named failures. `report.py` formats deterministic Markdown and JSON.

## Honesty boundary

All counts and rates are computed from supplied observations. Input provenance is declared, not independently verified. Synthetic observations are illustrative, never evidence of real intervention effectiveness. Posterior means are explicitly model-derived beliefs, not measured probabilities, predictions or discoveries. Proposed hypotheses are hypothetical and unmeasured. Time saved and money saved are unmeasured and not reported. The local runtime benchmark measures execution duration only; it is not a savings claim. Real input accuracy requires a hand-checked baseline outside the engine.

Fixture files carry `synthetic: true` wherever JSON allows it, including every trial and the expectations file. JSON does not permit header comments; LABEL.md supplies the explicit synthetic header for the fixture directory. The five-record JSON example also carries document and record labels. Every report includes a provenance banner and per-input provenance, including mixed real and synthetic sets. Mixed aggregate figures must not be interpreted as real-only results.

## Failure modes

Malformed JSON produces `ParseError` with filename and exact parser line. Semantic schema errors name the file and field, with line 1 denoting document-level validation, not a precise token location. Missing inputs produce `MissingInput` with a usage hint. Duplicate record IDs across documents produce a schema error. Read and write failures are named. Errors return exit code 2 without traceback. Report writes use a temporary sibling file and atomic replacement, cleaning up on failure; an existing output survives a failed write. Generated fixture files are individually atomic, not a transactional directory operation. Very large directories can exhaust memory; this engine is intended for local operator-scale trial sets.

## Acceptance evidence and improvement hook

The pytest suite tests planted truth, false positives, corruption sensitivity, malformed and missing inputs, empty directories, adversarial values, Unicode, long strings, deterministic bytes, provenance and atomic report failures. Local demo timing and test evidence are recorded in `EVIDENCE.md`. These validate synthetic behavior, not real-world usefulness.

After two weeks of real use, Henry records in `REVIEW.md`: window dates, number of actual runs, the hand-checked sample size, incorrect core outputs and error rate (incorrect / checked). With no checked observations, accuracy is unmeasured, never zero. If error rate exceeds 10 percent, fix the largest observed failure cause and rerun that sample, or kill with a recorded reason. If no real use occurs, record the finding and kill. Time saved may be used instead only with recorded paired baseline and engine durations for the same work.

The final project verdict is pending this evidence window. Record one of: expand for daily use or revenue; integrate for heavy sibling overlap; commercialise for an actual buyer willing to pay as-is; maintain for portfolio evidence; kill for no use or failed acceptance. No daily use, revenue or buyer demand is claimed by this build.
