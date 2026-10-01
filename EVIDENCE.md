# Local build evidence

Measured on 2026-10-01, Windows, Python 3.12.10, CPU only.

- `python -m pytest -q`: 31 passed in 0.28 seconds.
- Installed `kee2` entry point, fixture generation + run + Markdown report: 0.651391 seconds, measured with a PowerShell Stopwatch.
- JSON report command: 0.2160836 seconds, measured separately.
- Data: 200 SYNTHETIC planted records, not real trials.
- Exact counts: 130 successes, 70 failures, 5 accepted, 5 rejected, 0 insufficient.
- Accepted IDs equal planted truth exactly: h0, h1, h2, h3, h4. Zero synthetic false positives; all planted accepted cases found.
- Exact rates: 9/10 for first five hypotheses, 2/5 for last five.
- Model-derived posterior means: 19/22 for first five, 9/22 for last five.
- Corruption test changes 18 planted successes to failures and verifies 112 successes, four accepted, and posterior mean 1/22 for h0.

Full synthetic report artifacts are in `evidence/`. Timings measure local execution, not time saved. No real-use accuracy, savings, revenue or buyer interest has been measured. These measurements validate the local synthetic acceptance criterion only. The two-week review and final operational verdict remain pending in REVIEW.md.
