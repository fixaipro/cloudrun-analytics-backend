import re, io, base64
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm

def run(file_url):
    """
    1) Normalize Drive URLs
    2) Load CSV or Excel
    3) Fit OLS regression pre/post
    4) Compute summary & CI
    5) Plot and embed in HTML
    """
    # ————— 1) If this is a Drive link, convert to direct download —————
    if "drive.google.com" in file_url:
        m = re.search(r"/d/([-\w]+)", file_url) or re.search(r"id=([-\w]+)", file_url)
        if not m:
            raise ValueError(f"Could not extract Drive file ID from {file_url}")
        fid = m.group(1)
        file_url = f"https://drive.google.com/uc?export=download&id={fid}"

    # ————— 2) Load data — CSV vs Excel — including ?output=csv —————
    if (
        file_url.lower().endswith(".csv")
        or "export?format=csv" in file_url
        or "output=csv" in file_url
    ):
        df = pd.read_csv(file_url, parse_dates=['date'])
    else:
        df = pd.read_excel(file_url, engine='openpyxl', parse_dates=['date'])
    df.set_index('date', inplace=True)

    # ————— 3) Split pre/post and fit OLS —————
    pre  = df.iloc[:40]
    post = df.iloc[40:]
    X_pre     = sm.add_constant(pre['control'])
    y_pre     = pre['conversions']
    model     = sm.OLS(y_pre, X_pre).fit()
    X_post    = sm.add_constant(post['control'])
    predicted = model.predict(X_post)
    actual    = post['conversions']
    impact    = actual - predicted

    # ————— 4) Summary stats & 95% CI —————
    avg_lift  = impact.mean()
    cum_lift  = impact.sum()
    stderr    = impact.std() / np.sqrt(len(impact))
    ci_low    = avg_lift - 1.96 * stderr
    ci_high   = avg_lift + 1.96 * stderr

    # ————— 5) Plot into PNG → base64 —————
    plt.figure(figsize=(10,4))
    plt.plot(df.index, df['conversions'], label='Actual', linewidth=2)
    plt.plot(post.index, predicted,    '--', label='Predicted', linewidth=2)
    plt.axvline(df.index[39], color='red', linestyle='--', label='Intervention')
    plt.fill_between(post.index,
                     predicted - stderr,
                     predicted + stderr,
                     color='gray', alpha=0.3,
                     label='95% CI')
    plt.legend(loc='upper left')
    plt.title('Causal Impact Analysis')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode('utf-8')

    # ————— 6) Assemble final HTML —————
    html = f"""
    <html>
      <head>
        <title>Causal Impact Analysis</title>
        <style>
          body {{ font-family: Arial,sans-serif; padding:20px; }}
          table {{ border-collapse: collapse; width:50%; margin-bottom:20px; }}
          th, td {{ border:1px solid #ccc; padding:8px; text-align:right; }}
          th {{ background:#f5f5f5; }}
        </style>
      </head>
      <body>
        <h1>Causal Impact Analysis</h1>
        <table>
          <tr><th>Metric</th><th>Value</th></tr>
          <tr><td>Avg. Lift</td><td>{avg_lift:.2f}</td></tr>
          <tr><td>Cumulative Lift</td><td>{cum_lift:.2f}</td></tr>
          <tr><td>95% CI</td><td>[{ci_low:.2f}, {ci_high:.2f}]</td></tr>
        </table>
        <h2>Time Series Plot</h2>
        <img src="data:image/png;base64,{img_b64}" alt="Causal Impact Plot"/>
      </body>
    </html>
    """
    return html
