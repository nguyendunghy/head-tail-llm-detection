import hashlib

import bittensor as bt
import requests

from neurons.miners import index_data
from neurons.miners.utils import hash_code


def head_tail_api_pred_ai(list_text):
    bt.logging.info("start head_tail_api_pred")
    final_ai_pred = [True for _ in range(len(list_text))]
    not_touch_index_list = []
    input = []
    for i in range(len(list_text)):
        text = list_text[i]
        if len(text) <= 250:
            final_ai_pred[i] = False  # Human text < 250 chars
            continue
        list_token = index_data.cut_head_tail(text)
        if len(list_token) == 1:
            final_ai_pred[i] = False  # Human text is short
        else:
            not_touch_index_list.append(i)
            tmp_data = []
            for token in list_token:
                m = hashlib.sha256(token.encode('UTF-8'))
                sha256_hex = m.hexdigest()
                hash_value = hash_code(sha256_hex)
                db = hash_value % 10_000
                key = sha256_hex[:8]
                tmp_data.append(db)
                tmp_data.append(key)
            tmp_dic = {
                "head_db": tmp_data[0],
                "head": str(tmp_data[1]),
                "tail_db": tmp_data[2],
                "tail": str(tmp_data[3]),
            }
            input.append(tmp_dic)
    body_data = {"input": input}
    headers = {
        'Content-Type': 'application/json'
    }
    url = "http://65.108.33.125:8080/check-exists"
    response = requests.request("POST", url, headers=headers, data=body_data)
    if response.status_code == 200:
        data = response.json()
        human_pred_result = data['result']
        for i in range(len(not_touch_index_list)):
            human_pred = human_pred_result[i]
            not_touch_ind = not_touch_index_list[i]
            final_ai_pred[not_touch_ind] = not human_pred
        return final_ai_pred
    else:
        print('Failed to post data:status_code', response.status_code)
        print('Failed to post data:', response.content)
        return []
if __name__ == '__main__':
    input_text = []
    result = head_tail_api_pred_ai(input_text)
    print(result)