from flask import Flask, request, jsonify
import logging
import functions_dispatcher

app = Flask(__name__)
# configure logging
logging.basicConfig(level=logging.INFO)

@app.route('/', methods=['GET'])
def index():
    return '🚀 Cloud Run analytics backend is live!', 200

@app.route('/run-analysis', methods=['POST'])
def run_analysis():
    data = request.get_json(silent=True) or {}
    report_type = data.get('report_type')
    file_url    = data.get('file_url')

    logging.info(f"▶ Received request: report_type={report_type}, file_url={file_url}")

    if not report_type or not file_url:
        return jsonify({'error': 'Both report_type and file_url are required'}), 400

    try:
        html = functions_dispatcher.dispatch(report_type, file_url)
    except ValueError as e:
        logging.error(f"Dispatch error: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.exception("Unexpected error in dispatch")
        return jsonify({'error': 'Internal server error'}), 500

    # log first 200 chars of HTML for verification
    logging.info(f"◀ Returning HTML snippet: {html[:200]!r}")

    return jsonify({'html': html})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
