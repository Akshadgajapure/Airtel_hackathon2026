# Build information

**Project:** Project Udyam Digital — YTL Hackathon 2026, Enterprise Track A  
**Build:** Final refined submission package  
**Build date:** 7 November 2026  
**Reference date used for synthetic case checks:** 15 July 2026

## Run

- Windows: double-click `run.bat` (creates `.venv`, installs dependencies, starts the app).
- macOS/Linux: `./run.sh`.
- Open `http://127.0.0.1:8000`.
- Run tests: Windows `run_tests.bat`; macOS/Linux `./run_tests.sh`.

## Verified in build environment

- 34 automated tests passed.
- JavaScript syntax check passed.
- FastAPI smoke checks: 8 of 8 endpoints returned HTTP 200.
- Analysis pipeline reproduced a holdout ROC-AUC of 0.6598.
- KYC audit processed all 47 supplied specimen images across 12 applicants.
- The final archive passed ZIP integrity validation.

## Important boundaries

Synthetic exercise data only. GSTIN/Udyam lookups, consent audit, OTP e-sign, order notifications and installation milestone advancement are mocked. The advisor uses a deterministic fallback unless an optional LLM endpoint is explicitly configured. The dashboard's assignment store is local SQLite; the prototype has no authentication or multi-user synchronization. Do not use real customer PII or expose this prototype publicly.
