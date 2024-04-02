import json
from datetime import datetime
from flask import Flask, request, jsonify
import monitor_data_mysql
import requests

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route('/insert', methods=['POST'])
def insert():
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
        db_connection = monitor_data_mysql.get_db_connection('localhost', '8888')
        monitor_data_mysql.insert(db_connection, input_data)

        return jsonify({"insert success": True, "data": data}), 200
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
    # app.run(host='0.0.0.0', debug=True, port=8080)
    call_insert(text_hash="abcdef", model_type='standard', count_ai=100, count_human=100)
