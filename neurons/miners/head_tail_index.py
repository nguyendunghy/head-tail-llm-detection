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

if __name__ == '__main__':
    urls =["http://69.67.150.21:8080/verify-data",
           "http://103.219.170.221:8080/verify-data"]
    list_text = ['As of now, there is no definitive answer to how many international tries James Hook has scored in his career as try scoring statistics are not always consistently recorded or easily accessible for all players. According to some sources, Hook has scored a total of 10 tries in 74 appearances for the Welsh national team between 2006 and 2017 (RugbyPass, 2021). However, this information may not be up-to-date or complete, as it is always possible that new tries have been scored since then.',
                 'Formula:\n\n```\nLoss Percentage = (CP - SP) / CP *\n\n1. Calculate the loss amount: Loss = CP - SP\n   - CP = 605\n   - SP = 330\n   - Loss = 605 - 330 = 275\n\n2. Calculate the loss percentage:\n   - Loss Percentage = 275 / 605  100%\n```\n\n2. Ratio Method:\n\n- Calculate the ratio of SP to CP: 330 / 605 = 0.547\n- Multiply the ratio by 100 to express as a percentage: 0.547 * 100 = 54.7%\n- Prefix the result with a negative sign to inicate a loss: -54.7%\n\nNote:\n\n- Both alternative methods yield the same result as the original formula. - The percentage change formula is more concise and efficient for calculating losses. - The ratio method can be helpful in understanding the relationship between CP and SP visually.',
                 'If your vehicle is involved in an accident, stolen or set. Explore Shropshire Council\u2019s new website, giving you the tools and information you need for the services we provide. Tom.co.uk helps dads find the right life insurance, for free. It\u2019s quick and easy, and means your family is protected financially if anything happened to you.']
    result = head_tail_api_pred_human(list_text,urls)
    print(result)