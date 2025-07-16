# main.py

import io
import base64
import pandas as pd
from flask import Flask, request, jsonify, make_response
import matplotlib.pyplot as plt
from causalimpact import CausalImpact

app = Flask(__name__)

@app.route("/run-analysis", methods=["POST"])
def run_analysis():
    # 1) Grab the JSON payload
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"error": "Invalid JSON"}), 400

    report_type = payload.get("report_type")
    file_url    = payload.get("file_url")
    if not file_url:
        return jsonify({"error": "`file_url` is required"}), 400

    # 2) Fetch the CSV directly from the published Google Sheet
    try:
        df = pd.read_csv(file_url)
    except Exception as e:
        return jsonify({"error": f"Could not read CSV at `{file_url}`: {e}"}), 400

    # assume the first column is a date, second column is the metric
    df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0])
    df.set_index(df.columns[0], inplace=True)
    ts = df.iloc[:, 0]

    # 3) Choose your pre/post split — here I do first 50% / second 50%
    n = len(ts)
    pre_period  = [ts.index[0],            ts.index[n//2 - 1]]
    post_period = [ts.index[n//2],         ts.index[-1]]

    # 4) Run CausalImpact
    ci = CausalImpact(ts, pre_period, post_period)

    # 5) Pull out the key numbers
    summary = ci.summary_data
    avg_lift       = summary.loc["Average causal effect", "Average"]
    cum_lift       = summary.loc["Cumulative causal effect", "Cumulative"]
    lower, upper   = ci.summary_output["report"]["Cumulative causal effect"]["0.975"], \
                     ci.summary_output["report"]["Cumulative causal effect"]["0.025"]

    # 6) Render the time-series plot to a PNG and base64 it
    fig = ci.plot()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode("ascii")

    # 7) Build the final HTML
    html = f"""
    <html>
      <head>
        <title>{report_type}</title>
        <style>
          body {{ font-family: Arial,sans-serif; padding:20px; }}
          table {{ border-collapse: collapse; width:50%; margin-bottom:20px; }}
          th, td {{ border:1px solid #ccc; padding:8px; text-align:right; }}
          th {{ background:#f5f5f5; }}
        </style>
      </head>
      <body>
        <h1>{report_type}</h1>
        <table>
          <tr><th>Metric</th><th>Value</th></tr>
          <tr><td>Avg. Lift</td><td>{avg_lift:.2f}</td></tr>
          <tr><td>Cumulative Lift</td><td>{cum_lift:.2f}</td></tr>
          <tr><td>95% CI</td>
              <td>[{lower:.2f}, {upper:.2f}]</td></tr>
        </table>
        <h2>Time Series Plot</h2>
        <img src="data:image/png;base64,{img_b64}" alt="Causal Impact Plot"/>
      </body>
    </html>
    """

    resp = make_response(html)
    resp.headers["Content-Type"] = "text/html"
    return resp

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
