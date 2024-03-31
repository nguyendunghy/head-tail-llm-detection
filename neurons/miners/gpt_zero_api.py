import asyncio
import time

import requests

URL = 'https://api.gptzero.me/v2/predict/text'


async def is_ai_generated(document):
    """Return true if document is ai generated text, false if human written text"""

    body = {
        "document": document
    }

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'x-api-key': '61b48856c4af45e8b36723b4135254b5'
    }
    start_time = time.time_ns()
    response = requests.post(URL, json=body, headers=headers)
    end_time = time.time_ns()
    print('time call api: ' + str(end_time - start_time) + " nanosecond")

    # Checking if the request was successful
    if response.status_code == 200:
        data = response.json()
        predicted_class = data['documents'][0]['predicted_class']
        if predicted_class == 'ai':
            return document, True
        elif predicted_class == 'human':
            return document, False
        else:
            ai_prob = data['documents'][0]['class_probabilities']['ai']
            human_prob = data['documents'][0]['class_probabilities']['human']
            return document, float(ai_prob) > float(human_prob)
    else:
        print('Failed to post data:', response.status_code)


async def is_ai_generated_concurrent(input_data):
    coroutines = [is_ai_generated(data) for data in input_data]
    result_list = await asyncio.gather(*coroutines)
    mydict = {}
    for re in result_list:
        mydict[re[0]] = re[1]
    return mydict


if __name__ == '__main__':
    document1 = 'World War II: During WWII, the demand for crude oil increased dramatically.'
    document2 = 'This boosted the local oil production in Texas, including areas such as Midland County where Plateau is situated.'
    document3 = 'The town experienced economic growth due to increased oil extraction and related activities'
    document4 = 'Civil Rights Movement (1950s-1960s): While Texas was at the forefront of segregation and racial inequality during this time, small towns like Plateau were also affected'
    document5 = 'African Americans and Latino residents struggled for rights, and local events might have reflected these national movements'
    input_data = [document1, document2, document3, document4, document5]
    result = asyncio.run(is_ai_generated_concurrent(input_data))
    print("result::" + str(result))
