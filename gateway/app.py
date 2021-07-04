'''
WARNING: Baaad implementations left right and center here,
Need to have more robust error handling, schema verifications etc...
'''

from flask import Flask, request, jsonify
from requests import get, exceptions

# Grading function -> it's access point, would probably be in a database somewhere
FUNCTION_ADDRS = {
    "isExactEqual":"https://4jhmt8ysc5.execute-api.eu-west-2.amazonaws.com/default/isExactEqual"
}

#### Grading reponse logic
def grade_response(block):
    # We can directly send standalone responses to their grading scripts
    if block['isStandalone']:
        function_addr = FUNCTION_ADDRS[block['gradeFunction']]
        payload = {
            "command": "grade",
            "response": block["response"],
            "answer": block["answer"]
        }

        raw = get(function_addr, json=payload, headers={"Content-Type": "application/json"})
        return raw.json()

    # We first have to compute an algorithm, before grading
    else:
        algorithm_addr = f"http://{block['algorithmFunction']}:8888/algorithm"
        payload = {
            "prev_response": block["prev_response"],
        }

        raw = get(algorithm_addr, json=payload, headers={"Content-Type": "application/json"})

        try:
            body = raw.json()
            answer = body['answer']
        except Exception as e:
            return jsonify({"error": f"Couldnt parse json from algorithm function ({str(e)})"})

        # Now, we can grade
        function_addr = FUNCTION_ADDRS[block['gradeFunction']]
        payload = {
            "command": "grade",
            "response": block["response"],
            "answer": answer
        }

        raw = get(function_addr, json=payload, headers={"Content-Type": "application/json"})
        return raw.json()


#### API SETUP
app = Flask(__name__)

'''
MAIN ENDPOINT: requires a json body
{
    "responses": <list of responses>
}
'''
@app.route("/grade")
def main_grade_route():
    try:
        body = request.get_json()
    except ValueError:
        return jsonify({"error": f"Couldnt parse json from request ({str(e)})"}), 400

    if 'payload' not in body:
        return jsonify({"error": f"payload not in body", "received_body": body}), 400

    # Iterate through provided blocks
    grades = []
    for block in body['payload']:
        # Would probably verify the block against a schema here
        grades += [grade_response(block)]
        print(grades)

    return jsonify({"grades": grades}), 200

# Main route for health checks
@app.route("/")
def home():
    return "Welcome to the grading api gateway! Send in Response objects for grading..."

# Testing/debug route
@app.route("/testing")
def testing():
    try:
        body = request.get_json()
        selectAlias = body['test_internal_service']
        payload = body['payload']
    except Exception as e:
        return jsonify({"raw": str(e), "error": "test_internal_service and payload are required in json body"}), 400

    try:
        algoUrl = f"http://{body['test_internal_service']}"
        response = get(algoUrl, params=payload)
    except Exception as e:
        return jsonify({"error": str(e)})

    try:
        res = response.json()
    except ValueError as e:
        return jsonify({"error": f"Couldnt parse json from response ({str(e)})"}), 400

    return jsonify({"status:": f"Issued ping to {algoUrl} Algorithm [{response.status_code}]", "answer": res})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True)
