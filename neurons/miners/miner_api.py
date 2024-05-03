from flask import Flask, request, jsonify

from neurons.fake_miner import FakeMiner

app = Flask(__name__)
fake_miner = FakeMiner()


@app.route('/fake-miner', methods=['POST'])
def fake_miner():
    if request.is_json:
        data = request.get_json()
        input = data['input_data']
        fake_miner.fake_miner(input_data=input)
        return jsonify({"message": "check exists successfully", "result": 'OK'}), 200
    else:
        return jsonify({"error": "Request must be JSON"}), 400