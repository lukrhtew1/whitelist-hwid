from flask import Flask, request, jsonify, send_file
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv('host'),
            database=os.getenv('database'),
            user=os.getenv('user'),
            password=os.getenv('password')
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {str(e)}")
        raise

@app.route('/verify', methods=['POST'])
def verify_serial():
    data = request.get_json()
    serial_key = data.get('serialKey')
    hwid = data.get('hwid')

    if not serial_key or not hwid:
        return jsonify({"message": "Serial Key and HWID are required"}), 400

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('SET search_path TO my_schema;')
            cursor.execute('SELECT hwid FROM my_schema.serials WHERE serial_key = %s', (serial_key,))
            result = cursor.fetchone()

            if not result:
                cursor.execute('INSERT INTO my_schema.serials (serial_key, hwid) VALUES (%s, %s)', (serial_key, hwid))
                conn.commit()
                return jsonify({"message": "Verification successful, HWID registered for new serial key"}), 200

            registered_hwid = result[0]
            if registered_hwid:
                if registered_hwid == hwid:
                    return jsonify({"message": "HWID successfully verified", "provided_hwid": hwid, "registered_hwid": registered_hwid}), 200
                else:
                    return jsonify({"message": "HWID mismatch, cannot register this HWID for the serial key"}), 400

            cursor.execute('UPDATE my_schema.serials SET hwid = %s WHERE serial_key = %s', (hwid, serial_key))
            conn.commit()

    return jsonify({"message": "Verification successful, HWID registered"}), 200

@app.route('/')
def index():
    return send_file('index.html')

if __name__ == '__main__':
    # Run the app on the host and port defined by the environment variables
    app.run(host=os.getenv('FLASK_HOST', '0.0.0.0'), port=int(os.getenv('FLASK_PORT', 8000)))
