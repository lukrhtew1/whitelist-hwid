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
def verify_serial():
    try:
        data = request.get_json()  # Get JSON data from the POST request
        serial_key = data.get('serialKey')
        hwid = data.get('hwid')

        if not serial_key or not hwid:
            return jsonify({"message": "Serial Key and HWID are required"}), 400

        # Load the serial keys from the JSON file
        serial_keys = load_serial_keys()

        # Check if the serial key exists in the loaded keys
        if serial_key not in serial_keys:
            return jsonify({"message": "Invalid serial key"}), 400
        
        # If the serial key exists, check if there is a registered HWID
        registered_hwid = serial_keys[serial_key]

        # If no HWID is registered yet for this serial key, register the new HWID
        if not registered_hwid:
            serial_keys[serial_key] = hwid
            save_serial_keys(serial_keys)  # Save the updated serial keys with the new HWID
            return jsonify({"message": f"HWID registered successfully for serial key {serial_key}"}), 200
        
        # If a HWID is registered, verify that it matches the one sent by the client
        if registered_hwid != hwid:
            return jsonify({"message": "HWID does not match for the given serial key"}), 400

        # Otherwise, success
        return jsonify({"message": "Verification successful"}), 200

    except Exception as e:
        return jsonify({"message": f"Error occurred: {str(e)}"}), 500

# Optional: Serve an HTML front end if it exists
@app.route('/')
def index():
    return send_file('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
