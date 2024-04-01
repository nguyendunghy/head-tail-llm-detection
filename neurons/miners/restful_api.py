from flask import Flask, request, jsonify
import monitor_data_mysql

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
        input_data = (id, text_hash, model_type, count_ai, count_human)
        print(input_data)
        db_connection = monitor_data_mysql.get_db_connection('localhost', '3306')
        monitor_data_mysql.insert(db_connection, input_data)

        return jsonify({"insert success": True, "data": data}), 200
    else:
        return jsonify({"error": "Request must be JSON"}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)
