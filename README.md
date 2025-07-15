# Cloud Run via Cloud Build Starter

Push this entire repo to GitHub and configure a Cloud Build trigger on **main** branch
using the **cloudbuild.yaml** at the root.

## How it works

1. **Cloud Build trigger** detects push to `main`.
2. **cloudbuild.yaml** builds Docker image, pushes to Container Registry, and deploys to Cloud Run.
3. The service `cloudrun-analytics-backend` will be live at:
   ```
   https://<region>-<PROJECT_ID>.run.app/run-analysis
   ```

## Files

- `main.py`: Flask entrypoint with `/run-analysis`.
- `functions_dispatcher.py`: Dispatches report_type to analysis functions.
- `analytics_modules/`: Contains your analysis logic.
- `requirements.txt`: Python dependencies.
- `Dockerfile`: Container build.
- `cloudbuild.yaml`: Cloud Build config.
- `README.md`: This guide.
