import hashlib

import bittensor as bt
import requests

from neurons.miners import index_data
from neurons.miners.utils import hash_code


def head_tail_api_pred_human(list_text, urls):
    results = []
    for i in range(len(urls)):
        result = head_tail_api_pred_human_with_url(list_text, url=urls[i])
        results.append(result)

    preds = [False] * len(list_text)
    for i in range(len(results)):
        for j in range(len(preds)):
            preds[j] = preds[j] or results[i][j]

    return preds


def head_tail_api_pred_human_with_url(list_text, url):
    bt.logging.info("head_tail_api_pred_human list_text :" + str(list_text))
    final_human_pred = [False for _ in range(len(list_text))]
    not_touch_index_list = []
    input = []
    for i in range(len(list_text)):
        text = list_text[i]
        if len(text) <= 250:
            final_human_pred[i] = True  # Human text < 250 chars
            continue
        list_token = index_data.cut_head_tail(text)
        if len(list_token) == 1:
            final_human_pred[i] = True  # Human text is short
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
    if len(input) == 0:
        return final_human_pred
    body_data = {"input": input}
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, json=body_data)
    if response.status_code == 200:
        data = response.json()
        human_pred_result = data['result']
        for i in range(len(not_touch_index_list)):
            human_pred = human_pred_result[i]
            not_touch_ind = not_touch_index_list[i]
            final_human_pred[not_touch_ind] = human_pred
        return final_human_pred
    else:
        print('Failed to post data:status_code', response.status_code)
        print('Failed to post data:', response.content)
        return []
