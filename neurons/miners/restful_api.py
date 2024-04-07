import json
from datetime import datetime
from flask import Flask, request, jsonify
import requests
from neurons.miners.monitor_data_mysql import get_db_connection, insert, check_exists

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route('/insert', methods=['POST'])
def insert_api():
    if request.is_json:
        data = request.get_json()
        id = data['id']
        text_hash = data['text_hash']
        model_type = data['model_type']
        count_ai = data['count_ai']
        count_human = data['count_human']

        if id is None:
            now = datetime.now()
            id = now.strftime('%Y%m%d%H%M%S%f')[:17]

        input_data = (id, text_hash, model_type, count_ai, count_human)
        print(input_data)
        db_connection = get_db_connection('localhost', '8888')
        insert(db_connection, input_data)

        return jsonify({"insert success": True, "data": data}), 200
    else:
        return jsonify({"error": "Request must be JSON"}), 400


@app.route('/check-exists', methods=['POST'])
def check_exists_in_db():
    if request.is_json:
        data = request.get_json()
        input_arr = data['input']
        query_data = []
        for element in input_arr:
            tmp_data = [element['head_db'], element['head'], element['tail_db'], element['tail']]
            query_data.append(tmp_data)

        db_connection = get_db_connection('localhost', '3306')
        result = check_exists(db_connection, query_data)
        return jsonify({"message": "check exists successfully", "result": result}), 200
    else:
        return jsonify({"error": "Request must be JSON"}), 400


def call_insert(text_hash, model_type, count_human, count_ai):
    url = "http://70.48.87.64:41365/insert"

    headers = {
        'Content-Type': 'application/json'
    }
    payload = json.dumps({
        "id": None,
        "text_hash": text_hash,
        "model_type": model_type,
        "count_ai": count_ai,
        "count_human": count_human
    })

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        ...
    else:
        print('Failed to post data:', response.status_code, response.content)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)
    # call_insert(text_hash="abcdef", model_type='standard', count_ai=100, count_human=100)
