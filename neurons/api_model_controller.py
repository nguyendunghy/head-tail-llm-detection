import sys
import time

import bittensor as bt
from flask import Flask, request, jsonify

from neurons.request_handler import RequestHandler

app = Flask(__name__)
request_handlers = [RequestHandler()]


@app.route("/")
def hello_world():
    return "Hello! I am model service"


@app.route('/predict', methods=['POST'])
def predict1():
    start_time = time.time_ns()
    if request.is_json:
        data = request.get_json()
        input_data = data['list_text']
        result = request_handlers[0].handle(input_data=input_data)
        result = [1 if val else 0 for val in result]
        bt.logging.info(f"time loading {int(time.time_ns() - start_time):,} nanosecond")
        return jsonify({"message": "predict successfully", "result": result}), 200
    else:
        return jsonify({"error": "Request must be JSON"}), 400


@app.route('/predict-result', methods=['POST'])
def predict2():
    start_time = time.time_ns()
    if request.is_json:
        data = request.get_json()
        input_data = data['list_text']
        result = request_handlers[0].handle(input_data=input_data)
        bt.logging.info(f"time loading {int(time.time_ns() - start_time):,} nanosecond")
        return jsonify({"message": "predict result successfully", "result": result}), 200
    else:
        return jsonify({"error": "Request must be JSON"}), 400


if __name__ == '__main__':
    arg1 = sys.argv[1]
    app.run(host='0.0.0.0', debug=True, port=int(arg1))
