import sys

from flask import Flask, request, jsonify

from neurons.fake_miner import FakeMiner

app = Flask(__name__)
fm = None


@app.route("/")
def hello_world():
    return "Hello, miners!"


@app.route('/fake-miner', methods=['POST'])
def fake_miner():
    if request.is_json:
        data = request.get_json()
        input = data['input_data']
        fm.fake_miner(input_data=input)
        return jsonify({"message": "check exists successfully", "result": 'OK'}), 200
    else:
        return jsonify({"error": "Request must be JSON"}), 400


if __name__ == '__main__':
    arg = sys.argv
    port = int(arg[1])
    fm = FakeMiner(str(arg[2]).strip())

    app.run(host='0.0.0.0', debug=True, port=port)
