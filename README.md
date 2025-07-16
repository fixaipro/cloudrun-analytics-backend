# Cloud Run Analytics Backend (Dynamic Dispatch)

This repository contains a Flask service deployed to Google Cloud Run. It dynamically dispatches analysis
modules based on the `report_type` parameter, loading `analytics_modules.<slug>.run(file_url)`.

## Files

- `main.py`: Flask app with `GET /` health-check and `POST /run-analysis`.
- `functions_dispatcher.py`: Dynamic dispatcher using slugs.
- `analytics_modules/`: Contains 9 analysis scripts:
  - causal_impact_analysis.py
  - multi_cell_testing.py
  - budget_optimizer.py
  - scenario_planner.py
  - creative_fatigue_testing.py
  - point_of_diminishing_returns.py
  - b2b_prospects_predictor.py
  - modelled_analysis.py
  - mmm_lite.py
- `requirements.txt`: Python dependencies (`flask`).
- `Dockerfile`: Container build instructions.
- `cloudbuild.yaml`: Cloud Build config (CLOUD_LOGGING_ONLY).
- `README.md`: This guide.
- `.gitignore`: Ignore Python cache and environment files.

## Deploy via Cloud Build Trigger

1. Push this repo to GitHub (`cloudrun-analytics-backend`).
2. Create a Cloud Build trigger on `main` branch using `cloudbuild.yaml`.
3. On each push, Cloud Build will build, push, and deploy to Cloud Run.
4. Service URL: `https://<service>-<hash>-europe-west1.run.app`.

## Usage

```bash
curl -X POST https://<service-url>/run-analysis \
  -H "Content-Type: application/json" \
  -d '{"report_type":"Scenario Planner","file_url":"https://example.com/data.csv"}'
```
