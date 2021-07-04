from flask import Flask, jsonify, request
import numpy as np

info = {
    "name": "simpleMatrixInvert",
    "description": "Takes in a list of lists (matrix), and inverts it",
    "version": "0.1",
    "valid_commands": ["function_info", "algorithm"],
    "algorithm_schema": {
        "prev_response": {"type": ["string", "number"]}
    }
}

###### Algorithm Function, what this whole mini-app is made for
def algorithm(prev_response):
    A = np.array(prev_response)
    B = np.linalg.inv(A)
    B = np.round(B, decimals=3)
    return B.tolist()

###### Wrap with API
app = Flask(__name__)

# Base route (for health)
@app.route('/')
def home():
    return jsonify(f"Service {info['name']} is Online!")

# Return this function's info
@app.route('/function_info')
def get_info():
    return jsonify(info)

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": str(e), "valid_commands": info["valid_commands"]}), 404

# The prev_response should be send in the Request body (just like a Lambda Function)
@app.route('/algorithm')
def get_algorithm():
    body = request.get_json()

    # Security checks
    if "prev_response" not in body:
        return jsonify({"error": "prev_response was not supplied"}), 400

    # Probably validate the 'prev_response' against a schema here

    # Actually carry out the algorithm
    answer = algorithm(body['prev_response'])

    return jsonify({"answer": answer, "moredata": "here!"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True)
