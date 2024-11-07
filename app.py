from flask import Flask, request, jsonify, send_file
import json
import os

app = Flask(__name__)

# Load path to serials.json from environment variable or use default
json_file_path = os.getenv('SERIAL_KEYS_FILE_PATH', 'serials.json')

# Load serial keys
def load_serial_keys():
    with open(json_file_path, 'r') as f:
        return json.load(f)

# Save serial keys
def save_serial_keys(data):
    with open(json_file_path, 'w') as f:
        json.dump(data, f, indent=4)

# Endpoint for HWID verification
@app.route('/verify', methods=['POST'])
def verify():
    data = request.json
    serial_key = data.get('serial_key')
    hwid = data.get('hwid')

    if not serial_key or not hwid:
        return jsonify({"error": "Serial key and HWID are required"}), 400

    serial_keys = load_serial_keys()
    if serial_key not in serial_keys:
        return jsonify({"error": "Invalid serial key"}), 404

    if serial_keys[serial_key] == "":
        serial_keys[serial_key] = hwid
        save_serial_keys(serial_keys)
        return jsonify({"message": "HWID registered successfully"}), 201

    if serial_keys[serial_key] == hwid:
        return jsonify({"message": "HWID verified successfully"}), 200
    else:
        return jsonify({"error": "HWID mismatch"}), 403

# Optional: Serve an HTML front end if it exists
@app.route('/')
def index():
    return send_file('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
