import hashlib
import traceback

import bittensor as bt
import requests

from neurons.miners import index_data
from neurons.miners.utils import hash_code


def head_tail_api_pred_human(list_text, urls):
    try:
        results = []
        for i in range(len(urls)):
            result = head_tail_api_pred_human_with_url(list_text, url=urls[i])
            results.append(result)

        preds = [False] * len(list_text)
        for i in range(len(results)):
            for j in range(len(preds)):
                preds[j] = preds[j] or results[i][j]

        return preds
    except Exception as e:
        bt.logging.error(e)
        traceback.print_exc()



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


if __name__ == '__main__':
    urls = ["http://69.67.150.21:8080/check-exists",
            "http://103.219.170.221:8080/check-exists"]
    list_text = [
        "This date is significant for researching energy consumption during the Great Depression era as it marks a milestone in the development of hydroelectric power generation and transmission in the United States. The Hoover Dam's electricity played a crucial role in meeting the growing demand for power in Los Angeles, which was rapidly expanding at the time, and helped alleviate energy shortages during the Depression era. This event also highlights the importance of public works projects like Boulder/Hoover Dam in promoting economic growth and providing critical infrastructure during times of crisis."
    ,"Get desktop- class graphics performance on your MacBook Pro with the Blackmagic eGPU. Featuring the Radeon Pro 580 graphics processor, the Blackmagic eGPU is built to make any Mac with Thunderbolt 3 ports  graphics powerhouse. You love the power of using code to create custom graphics and effects. Ask questions here about setup and installation. Shop for Adobe Photoshop, cartoon , edge aware smoothing, Corel Draw at ; your source for the best computer deals anywhere, detail enhancement, buy the best Graphics Software, Fine presents a new technique for performing selective sharpening pencil effects. Housed in a 2RU frame the Smart Videohub ideal for use in both large broadcast systems portable mini racks.",
        "One day while looking at a book of photographs he begins to remember his childhood visits to his grandmother. As he recalls the frightening events involving soldiers appearing, he opens his eyes and is stunned to find himself a middle aged man sitting at the kitchen table. The narrative arc is not much of an arc: Fintan's \"crisis\" doesn't cause the family any disruption. The mystery of Martina's abrupt return to Dublin from London is explained in the course of her unspoken rumination of the events. Time is speeded up in that the effects of the economic crash in Ireland on each member of the family is briefly summarized in a chapter near the end of the book."
    ]
    result = head_tail_api_pred_human(list_text, urls)
    print(result)
