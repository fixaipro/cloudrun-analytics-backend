from flask import Flask, request, jsonify
import functions_dispatcher

app = Flask(__name__)

@app.route('/run-analysis', methods=['POST'])
def index():
    return '🚀 Cloud Run analytics backend is live!', 200

@app.route('/run-analysis', methods=['POST'])
def run_analysis():
    data = request.get_json()
    report_type = data.get('report_type')
    file_url = data.get('file_url')
    try:
        html = functions_dispatcher.dispatch(report_type, file_url)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    return jsonify({'html': html})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(__import__('os').environ.get('PORT', 8080)))
