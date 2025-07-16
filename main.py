import io
import base64
from flask import Flask, request, jsonify
import pandas as pd
import matplotlib.pyplot as plt
from causalimpact import CausalImpact

app = Flask(__name__)

@app.route("/run-analysis", methods=["POST"])
def run_analysis():
    payload = request.get_json(force=True)
    file_url = payload.get("file_url")
    if not file_url:
        return jsonify({"error": "Missing required key: file_url"}), 400

    try:
        # load CSV
        df = pd.read_csv(file_url)
    except Exception as e:
        return jsonify({"error": f"Could not read CSV at {file_url}: {e}"}), 400

    # assume first column is date, second is metric
    df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0])
    df.set_index(df.columns[0], inplace=True)
    series = df.iloc[:, 0]

    # split pre & post period
    # TODO: customize these dates or accept them in payload
    pre_period = [series.index.min(), series.index[int(len(series) * 0.6)]]
    post_period = [series.index[int(len(series) * 0.6) + 1], series.index.max()]

    ci = CausalImpact(series, pre_period, post_period)

    # metrics summary
    summary = {
        "average_lift": round(ci.summary_data["average"]["effect"], 2),
        "cumulative_lift": round(ci.summary_data["cumulative"]["effect"], 2),
        "95_ci": [
            round(ci.summary_data["average"]["lower"], 2),
            round(ci.summary_data["average"]["upper"], 2),
        ],
    }

    # render HTML + plot
    html = ci.summary("report")
    # add the plot onto the HTML
    fig = ci.plot()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    data_uri = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)

    html += f'<h2>Time Series Plot</h2><img src="data:image/png;base64,{data_uri}"/>'

    return jsonify({"summary": summary, "html": html})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
