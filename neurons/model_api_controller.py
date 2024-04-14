import time
from flask import Flask, request, jsonify
import bittensor as bt

from neurons.model_api_service import ModelService

app = Flask(__name__)
model_service = ModelService()


@app.route("/")
def hello_world():
    return "Hello! I am model service"


@app.route('/predict', methods=['POST'])
def predict():
    start_time = time.time_ns()
    if request.is_json:
        data = request.get_json()
        input_data = data['list_text']
        result = model_service.predict(input_data=input_data)
        bt.logging.info(f"time loading {int(time.time_ns() - start_time):,} nanosecond")
        return jsonify({"message": "predict successfully", "result": result}), 200
    else:
        return jsonify({"error": "Request must be JSON"}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)
