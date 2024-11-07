from flask import Flask, request, jsonify, send_file
import psycopg2
import os

app = Flask(__name__)

# Connect to the PostgreSQL database
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="21-4v.h.filess.io",  # Database host
            database="serials_composedgo",  # Your database name
            user="serials_composedgo",  # Database username
            password="3d381eb8f8533e99451f20db3e2e81f84ac60126"  # Database password
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {str(e)}")
        raise

# Endpoint for HWID verification
@app.route('/verify', methods=['POST'])
def verify_serial():
    try:
        data = request.get_json()  # Get JSON data from the POST request
        serial_key = data.get('serialKey')
        hwid = data.get('hwid')

        if not serial_key or not hwid:
            return jsonify({"message": "Serial Key and HWID are required"}), 400

        # Connect to the database using context manager
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Set the search path to the 'my_schema' schema
                cursor.execute('SET search_path TO my_schema;')

                # Check if serial key exists in the database
                cursor.execute('SELECT hwid FROM my_schema.serials WHERE serial_key = %s', (serial_key,))
                result = cursor.fetchone()

                if not result:
                    # Serial key does not exist, insert it with the HWID
                    cursor.execute('INSERT INTO my_schema.serials (serial_key, hwid) VALUES (%s, %s)', (serial_key, hwid))
                    conn.commit()
                    return jsonify({"message": "Verification successful, HWID registered for new serial key"}), 200

                # If the serial key is already registered with an HWID, check if it matches
                registered_hwid = result[0]
                if registered_hwid:
                    if registered_hwid == hwid:
                        # HWID matches, verification successful
                        return jsonify({"message": "HWID successfully verified"}), 200
                    else:
                        # HWID mismatch, return the appropriate error
                        return jsonify({"message": "HWID mismatch, cannot register this HWID for the serial key"}), 400

                # If the HWID field is empty, update it
                cursor.execute('UPDATE my_schema.serials SET hwid = %s WHERE serial_key = %s', (hwid, serial_key))
                conn.commit()

        return jsonify({"message": "Verification successful, HWID registered"}), 200

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({"message": f"Error occurred: {str(e)}"}), 500

# Optional: Serve an HTML front end if it exists
@app.route('/')
def index():
    return send_file('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
