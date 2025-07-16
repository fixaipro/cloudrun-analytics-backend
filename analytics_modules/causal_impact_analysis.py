import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
import io, base64

def run(file_url):
    # 1) Load data from CSV or Excel
    if file_url.lower().endswith('.csv') or 'output=csv' in file_url:
        df = pd.read_csv(file_url, parse_dates=['date'])
    else:
        df = pd.read_excel(file_url, engine='openpyxl', parse_dates=['date'])
    df.set_index('date', inplace=True)

    # 2) Split into pre/post periods
    pre  = df.iloc[:40]
    post = df.iloc[40:]

    # 3) Fit OLS on control → predict conversions
    X_pre  = sm.add_constant(pre['control'])
    y_pre  = pre['conversions']
    model  = sm.OLS(y_pre, X_pre).fit()
    X_post     = sm.add_constant(post['control'])
    predicted  = model.predict(X_post)
    actual     = post['conversions']
    impact     = actual - predicted

    # 4) Compute summary
    avg_impact = impact.mean()
    cum_impact = impact.sum()
    stderr     = impact.std() / np.sqrt(len(impact))
    ci_low     = avg_impact - 1.96 * stderr
    ci_high    = avg_impact + 1.96 * stderr

    # 5) Plot into PNG → base64
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

    # 6) Build final HTML
    html = f"""
    <html>
      <head>
        <title>Causal Impact Analysis</title>
        <style>
          body {{ font-family: Arial, sans-serif; padding: 20px; }}
          table {{ border-collapse: collapse; width:50%; margin-bottom:20px; }}
          th,td {{ border:1px solid #ccc; padding:8px; text-align:right; }}
          th {{ background: #f5f5f5; }}
        </style>
      </head>
      <body>
        <h1>Causal Impact Analysis</h1>
        <table>
          <tr><th>Metric</th><th>Value</th></tr>
          <tr><td>Avg. Lift</td><td>{avg_impact:.2f}</td></tr>
          <tr><td>Cumulative Lift</td><td>{cum_impact:.2f}</td></tr>
          <tr><td>95% CI</td><td>[{ci_low:.2f}, {ci_high:.2f}]</td></tr>
        </table>
        <h2>Time Series Plot</h2>
        <img src="data:image/png;base64,{img_b64}" alt="Causal Impact Plot"/>
      </body>
    </html>
    """
    return html
