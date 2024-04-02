import threading
import time

import requests

WINSTON_AI_URL = 'https://api.gowinston.ai/functions/v1/predict'


def is_ai_generated(document):
    """Return true if document is ai generated text, false if human written text"""
    if len(document) < 300:
        return False

    body = {
        'language': 'en',
        'sentences': False,
        'text': document,
        'version': '3.0'
    }

    headers = {
        'Authorization': 'Bearer UTNYlilT1ZhRpvhdpxIZHJAcF4iDTa5A7y0trPc5f6bd3906',
        'Content-Type': 'application/json'
    }
    start_time = time.time_ns()
    response = requests.post(WINSTON_AI_URL, json=body, headers=headers)
    end_time = time.time_ns()
    print('time call api: ' + str(end_time - start_time) + " nanosecond")

    # Checking if the request was successful
    if response.status_code == 200:
        data = response.json()
        score = data['score']
        print("score = " + str(score))
        return float(score) < 50
    else:
        print('Failed to post data:', response.status_code, response.content)


def is_ai_generated_no_return(result, index, document):
    is_ai = is_ai_generated(document)
    result[index] = is_ai


def is_ai_generated_list(doc_list):
    length = len(doc_list)
    result = [None] * length
    thread_list = []
    for i in range(length):
        my_thread = threading.Thread(target=is_ai_generated_no_return, args=(result, i, doc_list[i]))
        thread_list.append(my_thread)

    for i in range(length):
        thread_list[i].start()

    while result.count(None) > 0:
        print("count: " + str(result.count(None)))
        time.sleep(0.1)

    return result


if __name__ == "__main__":
    doc = ""
    short_doc = ""

    doc1 = "The error message you're encountering indicates that blinker was installed using distutils, which is an older method of installing Python packages that doesn't support uninstalling in the same way that packages installed with pip do. This situation often arises when a package is installed as part of the system's Python environment or through a system package manager rather than through pip."
    doc2 = "Running this command will stop the UFW firewall and deactivate the rules it has enforced, but it won't remove those rules. If you decide to enable UFW again later, your previously set rules will still be there and will become active again.If you prefer netstat or are working on a system where it's already installed, you can achieve similar results. First, if netstat is not installed, you can install the net-tools package that includes it"
    doc3 = "The Flask development server will start, and you can test the /data endpoint by sending a POST request with JSON data in the body using tools like curl, Postman, or any HTTP client library in your preferred programming language.The ss command is included with iproute2, a collection of utilities for controlling networking in Linux. It's available by default on Ubuntu and can be used to display more detailed network statistics."
    doc4 = "Creating a RESTful API to receive data in the request body can be straightforward with the Flask web framework. Flask is a lightweight WSGI web application framework in Python, well-suited for creating RESTful APIs. Below is a simple example that demonstrates how to set up a Flask application with an endpoint that receives JSON data in the request body."
    doc5 = "In terms of the rate of increase, Rice University (ranked 17th) has the highest tuition hike compared to last year, from $57,200 to $62,800, an increase of 9.9%. This is followed by Stanford University (ranked 3rd) and John Hopkins University (ranked 9th), both of which increased by about 5%, to $62,900 and $65,900 a year, respectively."

    start_time = time.time_ns()
    input_data = [doc1, doc2, doc3, doc4, doc5] * 10
    re = is_ai_generated_list(input_data)
    end_time = time.time_ns()
    print("time processing millisecond: " + str((end_time - start_time)/1_000_000))
    print("result:" + str(re))

