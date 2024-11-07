from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# Set the path to the serials.json file
documents_folder = os.path.join(os.path.expanduser('~'), 'Documents')
json_file_path = os.path.join(documents_folder,'serials.json')

# Load serial keys
def load_serial_keys():
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
            print("Loaded serials:", data)  # Print the loaded serials
            return data
    except FileNotFoundError:
        with open(json_file_path, 'w') as f:
            json.dump({}, f)
        return {}

# Save serial keys
def save_serial_keys(data):
    try:
        # Save the data to the serials.json file
        with open(json_file_path, 'w') as f:
            json.dump(data, f, indent=4)
        
        # Create a JSON response to return as a string
        json_data = json.dumps(data, indent=4)
        print(f"Saved updated serials: {json_data}")  # Print the saved data as JSON
        
        return jsonify({"message": "Serials updated successfully"}), 200  # Return a successful response

    except Exception as e:
        print(f"Error saving serials: {e}")
        return jsonify({"message": f"Error occurred: {str(e)}"}), 500
        
# Endpoint for HWID verification
@app.route('/verify', methods=['POST'])
def verify_serial():
    try:
        data = request.get_json()  # Get JSON data from the POST request
        serial_key = data.get('serialKey')
        hwid = data.get('hwid')

        if not serial_key or not hwid:
            return jsonify({"message": "Serial Key and HWID are required"}), 400

        # Load serial keys from the file
        serials = load_serial_keys()

        # Check if serial key exists in the loaded serials
        if serial_key not in serials:
            print(f"Serial key {serial_key} not found!")
            return jsonify({"message": "Invalid serial key"}), 400

        # If the serial key is already registered with an HWID, check if it matches
        if serials[serial_key]:
            if serials[serial_key] == hwid:
                return jsonify({"message": "HWID already registered with this serial key"}), 200
            else:
                return jsonify({"message": "HWID mismatch, cannot register this HWID for the serial key"}), 400
        
        # Register the HWID for the serial key
        serials[serial_key] = hwid
        print(f"Registered HWID for serial {serial_key}: {hwid}")  # Debug line

        # Save the updated serials to the JSON file
        return save_serial_keys(serials)

    except Exception as e:
        return jsonify({"message": f"Error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
