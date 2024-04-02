import time

import requests

WINSTON_AI_URL = 'https://api.gowinston.ai/functions/v1/predict'


def is_ai_generated(document):
    """Return true if document is ai generated text, false if human written text"""

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


if __name__ == "__main__":
    doc = "In his remarks at a conference on sustainable marine aquaculture with a view from Quang Ninh held on April 1 in the northern province, Hoan said marine aquaculture will create new economic opportunities, livelihoods, and biodiversity, adding that it holds a leading role, contributing significantly to economic growth, state budget revenue, and employment"
    is_ai = is_ai_generated(doc)
    print("is_ai:" + str(is_ai))
