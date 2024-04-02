import asyncio
import os
import shutil
import time

import requests

GPT_ZERO_URL = 'https://api.gptzero.me/v2/predict/text'


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
    response = requests.post(GPT_ZERO_URL, json=body, headers=headers)
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

    pre_list = []
    for data in input_data:
        pred = mydict.get(data)
        pre_list.append(pred)
    return pre_list


def gen_file(input_data):
    current_time = time.time_ns()
    dir_path = "/root/head-tail-llm-detection/test_data/" + str(current_time) + "/"
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    for i in range(len(input_data)):
        file_name = 'doc_' + str(i) + ".txt"
        file_path = dir_path + file_name
        with open(file_path, 'w') as file:
            file.write(input_data[i])
            print(f"Content written to {file_name}")

    return dir_path


def is_ai_generated_files(input_data):
    dir_path = gen_file(input_data)
    try:
        files = []
        for i in range(len(input_data)):
            key = 'doc_' + str(i) + ".txt"
            file_path = dir_path + key
            file = ('files', (key, open(file_path, 'rb'), 'text/plain'))
            files.append(file)

        payload = {'version': ''}
        headers = {
            'Accept': 'application/json',
            'x-api-key': '61b48856c4af45e8b36723b4135254b5'
        }
        response = requests.request("POST", 'https://api.gptzero.me/v2/predict/files', headers=headers, data=payload,
                                    files=files)
        if response.status_code == 200:
            data = response.json()
            result_list = []
            for i in range(len(input_data)):
                document = data['documents'][i]
                predicted_class = document['predicted_class']
                if predicted_class == 'ai':
                    result_list.append(True)
                elif predicted_class == 'human':
                    result_list.append(False)
                else:
                    ai_prob = document['class_probabilities']['ai']
                    human_prob = document['class_probabilities']['human']
                    result_list.append(float(ai_prob) > float(human_prob))
            return result_list
        else:
            print('Failed to post data:status_code', response.status_code)
            print('Failed to post data:', response.content)
            return []
    except Exception as e:
        print('Exception:' + str(e))
        return []
    finally:
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            shutil.rmtree(dir_path)


if __name__ == '__main__':
    document1 = 'It first checks whether the specified path exists and is indeed a directory (and not, for example, a symbolic link or a file) to avoid unintended deletion'
    document2 = 'If the check passes, shutil.rmtree() removes the directory and everything contained within it, including subdirectories and files'
    document3 = 'Be very careful when using shutil.rmtree() because it irreversibly deletes data. Always ensure that the path is correct and that you indeed want to delete the directory and its contents'
    # document4 = 'Civil Rights Movement (1950s-1960s): While Texas was at the forefront of segregation and racial inequality during this time, small towns like Plateau were also affected'
    # document5 = 'African Americans and Latino residents struggled for rights, and local events might have reflected these national movements'
    input_data = [document1, document2, document3]
    start_time = time.time_ns()
    result = is_ai_generated_files(input_data)
    end_time = time.time_ns()
    print('time call async: ' + str(end_time - start_time) + " nanosecond")
    print("result::" + str(result))
