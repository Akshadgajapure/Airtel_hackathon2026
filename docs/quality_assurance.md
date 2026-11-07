# Quality assurance record

QA performed against the packaged source on 7 November 2026.

## Automated checks

| Check | Result | Evidence |
|---|---|---|
| Python unit + API integration tests | **34 passed, 0 failed** | `python -m pytest -q` |
| JavaScript syntax | **Passed** | `node --check app/static/app.js` |
| FastAPI smoke checks | **8/8 HTTP 200** | `/`, health, catalogue, analytics, lead queue, assignments, KYC applicants, hand-offs |
| Analysis reproduction | **Passed** | `python analysis/run_analysis.py`; holdout ROC-AUC 0.6598 |
| KYC specimen audit | **47 images / 12 applicants** | `python analysis/run_kyc_audit.py`; transcripts and results CSV regenerated |
| Data integrity | **5,000 leads / 25 catalogue products / 47 KYC images** | source files in `data/` |
| ZIP integrity | Verified on final archive build | `unzip -t` |

## What the tests cover

- Deterministic product eligibility, dependencies, quote calculations and GSTIN checksum rules.
- Dataset-backed analytics and funnel metrics.
- Lead search filters, score ranking, pagination and full-filter CSV export.
- Assignment validation, SQLite persistence and assignment event history.
- Masked lead detail endpoint and identifier omission.
- Consent gate, upload content validation, OCR preview masking and review-required status.
- Advisor → quote → consent → mock e-sign → order creation → tracker milestone progression.
- Expected specimen KYC exceptions: K01, K04, K05, K11 and K12.

## Verification boundary

The API and JavaScript were tested in the build environment. Automated Chromium navigation to localhost was blocked by the execution environment, so no claim is made that a full visual browser regression suite passed. Before submission, launch the app on the target laptop and perform the 3-minute demo once. The app uses synthetic data and mocked third-party services; it is not production-ready for real customer PII.
