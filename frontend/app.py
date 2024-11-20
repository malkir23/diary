from flask import Flask, jsonify
import requests


FASTAPI_URL = "http://fastapi_d:8000"

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify(message="Welcome to the Flask Service!")

@app.route('/sections')
def sections():
    return jsonify(sections=["Backlog", "In Progress", "Done"])

@app.route('/fetch-data')
def fetch_data():
    try:
        # Call the FastAPI endpoint
        response = requests.get(f"{FASTAPI_URL}/api/data")
        response.raise_for_status()  # Raise an exception for HTTP errors
        fastapi_data = response.json()  # Parse the JSON response
        return jsonify(fastapi_data)
    except requests.exceptions.RequestException as e:
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
