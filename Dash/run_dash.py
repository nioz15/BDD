import os
import io
import zipfile
import json
import subprocess
import re
import html
from flask import Flask, render_template, jsonify, send_from_directory, request, url_for, send_file

app = Flask(__name__)
app.secret_key = 'CHANGE_THIS_SECRET_KEY'

# Directory for downloaded reports
DOWNLOAD_DIR = "/home/ubuntu/BDD/Dash/static/downloaded-reports"

# Virtual environment Python
VENV_PYTHON = "/home/ubuntu/BDD/Dash/venv/bin/python3"

# BDD Tests data
with open('bdd_tests.json', 'r') as file:
    BDD_TESTS = json.load(file)

# Test data (farm status)
DATA_JSON_PATH = os.path.join('static', 'data.json')

@app.route('/')
def index():
    # Main dashboard page
    return render_template('dashboard.html')

@app.route('/download/<string:filename>', methods=['GET'])
def download_report(filename):
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(file_path):
        return send_from_directory(DOWNLOAD_DIR, filename)
    else:
        script_path = '/home/ubuntu/BDD/Dash/s3.py'
        result = subprocess.run(['sudo', '-u', 'www-data', VENV_PYTHON, script_path, filename],
                                capture_output=True, text=True)
        if result.returncode != 0:
            return jsonify({"error": result.stderr}), 500
        if os.path.exists(file_path):
            return send_from_directory(DOWNLOAD_DIR, filename)
        else:
            return jsonify({"error": "File not found after download"}), 404

@app.route('/bdd_search', methods=['GET'])
def bdd_search():
    return render_template('bdd_search.html')

@app.route('/search_bdd', methods=['GET'])
def search_bdd():
    query = request.args.get('query', '').lower()
    matching_tests = []
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    for test in BDD_TESTS:
        full_test_text = " ".join(test["steps"]).lower()
        if query in full_test_text:
            highlighted_steps = []
            for step in test["steps"]:
                escaped_step = html.escape(step)
                highlighted_step = pattern.sub(
                    lambda m: f"<span class='highlight'>{m.group(0)}</span>",
                    escaped_step
                )
                highlighted_steps.append(highlighted_step)
            escaped_examples = {}
            for key, values in test["examples"].items():
                escaped_values = [html.escape(str(value)) for value in values]
                escaped_examples[key] = escaped_values
            matching_tests.append({
                "highlighted_steps": highlighted_steps,
                "examples": escaped_examples
            })
    return jsonify(matching_tests)

@app.route('/farm_status', methods=['GET'])
def farm_status():
    with open(DATA_JSON_PATH) as f:
        data = json.load(f)
    farm_names = set()
    for test_group in data.values():
        for test in test_group:
            filename = test['filename']
            farm_name = filename.split('_')[0]
            farm_names.add(farm_name)
    farm_names = sorted(farm_names)
    return render_template('farm_status.html', farm_names=farm_names)

@app.route('/get_farm_data', methods=['GET'])
def get_farm_data():
    farm_name = request.args.get('farm')
    if not farm_name:
        return jsonify({'error': 'No farm specified'}), 400
    with open(DATA_JSON_PATH) as f:
        data = json.load(f)
    farm_data = []
    for test_group in data.values():
        for test in test_group:
            filename = test['filename']
            test_farm_name = filename.split('_')[0]
            if test_farm_name == farm_name:
                farm_data.append(test)
    return jsonify(farm_data)

@app.route('/customers', methods=['GET'])
def integration():
    return render_template('integration.html')

@app.route('/download_bdd_ahz', methods=['GET'])
def download_bdd_ahz():
    # Directory to zip
    base_path = "/home/ubuntu/BDD/Dash/ahz"


    import io
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(base_path):
            for file in files:
                file_path = os.path.join(root, file)
                zf.write(file_path, os.path.relpath(file_path, base_path))

    memory_file.seek(0)

    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name='BDD_Dash_ahz_Files.zip'
    )

if __name__ == '__main__':
    app.run(debug=True, port=8000, host='0.0.0.0')
