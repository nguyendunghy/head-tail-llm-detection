import time

import requests

URL = 'https://api.gptzero.me/v2/predict/text'


def post(document):
    start_time = time.time_ns()
    body = {
        "document": document
    }

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'x-api-key': '61b48856c4af45e8b36723b4135254b5'
    }

    response = requests.post(URL, json=body, headers=headers)

    # Checking if the request was successful
    if response.status_code == 200:
        data = response.json()
        print(data['documents'][0]['predicted_class'])
        print(data['documents'][0]['class_probabilities']['ai'])
        print(data['documents'][0]['class_probabilities']['human'])
        print(data['documents'][0]['class_probabilities']['mixed'])

    else:
        print('Failed to post data:', response.status_code)

    end_time = time.time_ns()
    print('time processing: ' + str(end_time - start_time) + " nanosecond")


if __name__ == '__main__':
    post(
        'World War II: During WWII, the demand for crude oil increased dramatically. This boosted the local oil production in Texas, including areas such as Midland County where Plateau is situated. The town experienced economic growth due to increased oil extraction and related activities. 3. Civil Rights Movement (1950s-1960s): While Texas was at the forefront of segregation and racial inequality during this time, small towns like Plateau were also affected. African Americans and Latino residents struggled for rights, and local events might have reflected these national movements. 4.')
