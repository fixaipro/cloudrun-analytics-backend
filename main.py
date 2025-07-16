import os
import io
import base64
import pandas as pd
from flask import Flask, request, jsonify, make_response
import matplotlib.pyplot as plt
from causalimpact import CausalImpact

app = Flask(__name__)

@app.route("/run-analysis", methods=["POST"])
def run_analysis():
    data = request.get_json(silent=True)
    if not data or "file_url" not in data:
        return jsonify({"error": "`file_url` is required"}), 400

    url = data["file_url"]
    report_title = data.get("report_type", "Causal Impact Analysis")

    # 1) Load CSV from Google Sheets
    try:
        df = pd.read_csv(url)
    except Exception as e:
        return jsonify({"error": f"Failed to read CSV at `{url}`: {e}"}), 400

    # 2) Force first column → datetime index, second column → metric
    df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0])
    df.set_index(df.columns[0], inplace=True)
    ts = df.iloc[:, 1]  # <— dynamic pick of 2nd column

    # 3) Split half pre / half post
    n = len(ts)
    pre_period  = [ts.index[0],       ts.index[n//2 - 1]]
    post_period = [ts.index[n//2],     ts.index[-1]]

    # 4) Run CausalImpact
    ci = CausalImpact(ts, pre_period, post_period)

    # 5) Pull numbers out
    summary   = ci.summary_data
    avg_lift  = summary.loc["Average causal effect",    "Average"]
    cum_lift  = summary.loc["Cumulative causal effect", "Cumulative"]
    lower_ci  = ci.summary_output["report"]["Cumulative causal effect"]["0.025"]
    upper_ci  = ci.summary_output["report"]["Cumulative causal effect"]["0.975"]

    # 6) Plot → PNG → Base64
    fig = ci.plot()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode("ascii")

    # 7) Build HTML
    html = f"""
    <html>
      <head>
        <title>{report_title}</title>
        <style>
          body {{ font-family: Arial,sans-serif; padding:20px; }}
          table {{ border-collapse: collapse; width:50%; margin-bottom:20px; }}
          th, td {{ border:1px solid #ccc; padding:8px; text-align:right; }}
          th {{ background:#f5f5f5; }}
        </style>
      </head>
      <body>
        <h1>{report_title}</h1>
        <table>
          <tr><th>Metric</th><th>Value</th></tr>
          <tr><td>Avg. Lift</td><td>{avg_lift:.2f}</td></tr>
          <tr><td>Cumulative Lift</td><td>{cum_lift:.2f}</td></tr>
          <tr><td>95% CI</td><td>[{lower_ci:.2f}, {upper_ci:.2f}]</td></tr>
        </table>
        <h2>Time Series Plot</h2>
        <img src="data:image/png;base64,{img_b64}" />
      </body>
    </html>
    """

    resp = make_response(html)
    resp.headers["Content-Type"] = "text/html"
    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
