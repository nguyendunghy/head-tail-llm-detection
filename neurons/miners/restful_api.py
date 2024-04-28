import sys
import time
import traceback

from flask import Flask, request, jsonify
import bittensor as bt

from neurons.miners.redis_utils import check_exists, verify_raw_text_exists, set_cache_preds, get_cache_preds

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route('/check-exists', methods=['POST'])
def check_exists_in_db():
    start_time = time.time_ns()
    if request.is_json:
        data = request.get_json()
        input_arr = data['input']
        input_redis = []
        for element in input_arr:
            tmp_data = [element['head_db'], element['head'], element['tail_db'], element['tail']]
            input_redis.append(tmp_data)

        result = check_exists(input_redis)
        bt.logging.info(f"time loading {int(time.time_ns() - start_time):,} nanosecond")
        return jsonify({"message": "check exists successfully", "result": result}), 200
    else:
        return jsonify({"error": "Request must be JSON"}), 400


@app.route('/verify-data', methods=['POST'])
def verify_data():
    start_time = time.time_ns()
    if request.is_json:
        data = request.get_json()
        input_arr = data['texts']
        result = []
        for element in input_arr:
            isEx = verify_raw_text_exists(element)
            result.append(isEx)

        bt.logging.info(f"time loading {int(time.time_ns() - start_time):,} nanosecond")
        return jsonify({"message": "check exists successfully", "result": result}), 200
    else:
        return jsonify({"error": "Request must be JSON"}), 400


@app.route('/get_cached', methods=['POST'])
def get_cached():
    start_time = time.time_ns()
    if request.is_json:
        data = request.get_json()
        hash_key = data['hash_key']
        preds = get_cache_preds(hash_key)
        bt.logging.info(f"time loading {int(time.time_ns() - start_time):,} nanosecond")
        return jsonify({"message": "check exists successfully", "result": preds}), 200
    else:
        return jsonify({"error": "Request must be JSON"}), 400


@app.route('/save_cached', methods=['POST'])
def save_cached():
    start_time = time.time_ns()
    if request.is_json:
        data = request.get_json()
        hash_key = data['hash_key']
        preds = data['preds']
        set_cache_preds(hash_key, preds)
        bt.logging.info(f"time loading {int(time.time_ns() - start_time):,} nanosecond")
        return jsonify({"message": "check exists successfully", "result": "OK"}), 200
    else:
        return jsonify({"error": "Request must be JSON"}), 400


if __name__ == '__main__':
    try:
        arg1 = sys.argv[1]
    except Exception as e:
        bt.logging.error(e)
        traceback.print_exc()
        arg1 = '8080'

    app.run(host='0.0.0.0', debug=True, port=int(arg1))
