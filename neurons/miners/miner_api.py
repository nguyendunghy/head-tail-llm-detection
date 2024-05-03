import sys

from flask import Flask, request, jsonify

from neurons.fake_miner import FakeMiner

app = Flask(__name__)
MODEL_TYPE = 'ppl'
fake_miner = FakeMiner(MODEL_TYPE)


@app.route("/")
def hello_world():
    return "Hello, miners!"


@app.route('/fake-miner', methods=['POST'])
def fake_miner():
    if request.is_json:
        data = request.get_json()
        input = data['input_data']
        fake_miner.fake_miner(input_data=input)
        return jsonify({"message": "check exists successfully", "result": 'OK'}), 200
    else:
        return jsonify({"error": "Request must be JSON"}), 400


if __name__ == '__main__':
    arg = sys.argv
    port = int(arg[0])
    MODEL_TYPE = str(arg[1])

    app.run(host='0.0.0.0', debug=True, port=port)
