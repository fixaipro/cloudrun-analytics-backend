# main.py
import io
import os
import base64
import json
import urllib.request

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from flask import Flask, request, jsonify

app = Flask(__name__)

def fetch_csv(url: str) -> pd.DataFrame:
    """
    Fetch a published-CSV Google Sheet (or any CSV) at `url` into a DataFrame.
    """
    resp = urllib.request.urlopen(url)
    return pd.read_csv(io.TextIOWrapper(resp, 'utf-8'))

def compute_causal_impact(df: pd.DataFrame):
    """
    Given a DataFrame with columns ['date','control','conversions'], 
    index date, returns summary dict + Matplotlib fig.
    """
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date').sort_index()
    pre, post = df.iloc[:40], df.iloc[40:]

    # Fit on pre
    X0 = sm.add_constant(pre['control'])
    y0 = pre['conversions']
    model = sm.OLS(y0, X0).fit()

    # Predict post
    X1 = sm.add_constant(post['control'])
    pred = model.predict(X1)

    # Impact
    actual = post['conversions']
    impact = actual - pred
    avg_lift = impact.mean()
    cum_lift = impact.sum()
    se = impact.std() / np.sqrt(len(impact))
    ci_low, ci_high = avg_lift - 1.96*se, avg_lift + 1.96*se

    # Build the plot
    fig, ax = plt.subplots(figsize=(10,5))
    ax.plot(df.index, df['conversions'], label='Actual', lw=2)
    ax.plot(post.index, pred, '--', label='Predicted (counterfactual)', lw=2)
    ax.axvline(df.index[39], color='red', ls='--', label='Intervention')
    ax.fill_between(post.index,
                    pred - se,
                    pred + se,
                    color='gray', alpha=0.3,
                    label='Prediction CI')
    ax.legend(loc='upper left')
    ax.set_title('Causal Impact Analysis')
    ax.set_xlabel('Date')
    ax.set_ylabel('Conversions')
    ax.grid(True)

    return {
        'avg_lift': avg_lift,
        'cum_lift': cum_lift,
        'ci_low': ci_low,
        'ci_high': ci_high,
        'figure': fig
    }

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('ascii')

@app.route('/run-analysis', methods=['POST'])
def run_analysis():
    data = request.get_json()
    sheet_url = data['file_url']            # your published-CSV form responses
    report_type = data['report_type']       # e.g. "Causal Impact Analysis"

    # 1) pull the form-responses sheet
    resp_df = fetch_csv(sheet_url)

    # 2) assume the last row is the one just submitted
    last = resp_df.iloc[-1]
    csv_url = last['File upload']           # adjust if your column header differs

    # 3) pull the user’s data CSV
    df = fetch_csv(csv_url)
    #    ensure it has exactly three columns: date, control, conversions
    df = df.rename(columns={df.columns[0]:'date',
                            df.columns[1]:'control',
                            df.columns[2]:'conversions'})

    # 4) compute
    result = compute_causal_impact(df)

    # 5) build HTML
    plot_b64 = fig_to_base64(result['figure'])
    summary_html = f"""
      <table>
        <tr><th>Metric</th><th>Value</th></tr>
        <tr><td>Avg. Lift</td><td>{result['avg_lift']:.2f}</td></tr>
        <tr><td>Cumulative Lift</td><td>{result['cum_lift']:.2f}</td></tr>
        <tr><td>95% CI</td><td>[{result['ci_low']:.2f}, {result['ci_high']:.2f}]</td></tr>
      </table>
    """

    html = f"""
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>{report_type}</title>
        <style>
          body {{ font-family: Arial, sans-serif; padding: 20px; }}
          table {{ border-collapse: collapse; margin-bottom: 20px; }}
          th, td {{ border: 1px solid #ccc; padding: 8px; text-align: right; }}
          th {{ background: #f7f7f7; }}
          img {{ max-width: 100%; height: auto; }}
        </style>
      </head>
      <body>
        <h1>{report_type}</h1>
        {summary_html}
        <h2>Time Series Plot</h2>
        <img src="data:image/png;base64,{plot_b64}" />
      </body>
    </html>
    """

    return jsonify({'html': html})

if __name__ == '__main__':
    # for local testing
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
