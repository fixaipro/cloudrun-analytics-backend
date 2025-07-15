# Cloud Run Analytics Backend (All 9 Functions)

This repository contains a Flask-based service for Google Cloud Run with nine analysis modules

## Files

- `main.py`: Flask entrypoint with `/run-analysis`.
- `functions_dispatcher.py`: Routes `report_type` to analysis functions.
- `analytics_modules/`: Contains nine analysis scripts (`analysis1.py` … `analysis9.py`) and a dispatch map.
- `requirements.txt`: Python dependencies.
- `Dockerfile`: Container build instructions.
- `cloudbuild.yaml`: Cloud Build config (with CLOUD_LOGGING_ONLY to avoid logs bucket error).
- `README.md`: This document.
- `.gitignore`: Python ignores.

## Usage

1. **Push** this repo to GitHub (`cloudrun-analytics-backend`).
2. **Create** a Cloud Build trigger on `main` using `cloudbuild.yaml`.
3. On **push**, Cloud Build will build, push, and deploy to Cloud Run.
4. **Test**:
   ```bash
   curl -X POST https://<region>-<PROJECT_ID>.run.app/run-analysis \
     -H "Content-Type: application/json" \
     -d '{"report_type":"type3","file_url":"https://example.com/data"}'
   ```
