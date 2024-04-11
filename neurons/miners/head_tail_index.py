import hashlib
import json

import bittensor as bt
import requests
from neurons.miners import index_data
from neurons.miners.utils import hash_code


def head_tail_api_pred_human(list_text):
    url1 = "http://69.67.150.21:8080/check-exists"
    url2 = 'http://103.219.170.221:8080/check-exists'

    result1 = head_tail_api_pred_human_with_url(list_text, url=url1)
    result2 = head_tail_api_pred_human_with_url(list_text, url=url2)

    result = [result1[i] or result2[i] for i in range(len(result1))]
    return result


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


def get_line(file, line_number):
    with open(file, 'r') as file:
        for current_line_number, line in enumerate(file, start=1):
            if current_line_number == line_number:
                return line.strip()
    return None


def verify():
    file_path = '/root/c4_dataset/c4/extracted/c4-train.00001-of-01024.json'
    with open(file_path, 'r') as file:
        for current_line_number, line in enumerate(file, start=1):
            my_dict = json.loads(line)
            input = [my_dict['text']]
            result = head_tail_api_pred_human(input)
            if not result[0]:
                bt.logging.info("indexing fail: " + str(current_line_number) + ":" + str(line))
    return None


if __name__ == '__main__':
    # text = '''British lawmakers are to question the country's financial regulator about whether it was lobbied by ministers to change its rules and lure the $2tn flotation of Saudi's Aramco to London.\nThe fears come amid claims that UK Prime Minister Theresa May and senior government ministers actively attempted to lobby Riyadh for the UK to host the sell-off of the world's biggest energy company.\nAndrew Bailey, head of the Financial Conduct Authority, will be questioned by MPs Nicky Morgan, who chairs the Treasury Committee, and Rachel Reeves, who chairs the Business, Energy and Industrial Strategy Committee. A date has yet to be set for the hearings.\nOn Friday, Morgan made public a joint letter that the two MPs sent to Bailey. In it they asked seven questions, including whether the FCA was \"aware of any interest shown by Saudi Aramco in obtaining a UK listing, and if known, how far that interest influenced the consultation?\"\nMorgan told City AM that the FCA had to maintain its role as the body that preserves the reputation of Britain's financial institution.\n“The UK has a world-class reputation for upholding strong corporate governance,” she said. “The FCA must protect this reputation, especially as the City looks to remain competitive and thrive post-Brexit.” The pair plan to discuss Bailey's response with their fellow committee members.\nRiyadh is selling a five percent portion of Aramco as part of its Vision 2030 strategy, which aims to cut the kingdom's reliance on oil - which has suffered reduced prices in recent years - and raise $200bn during the next several years.\nThe FCA is a regulatory body which operates independently of the UK government. It did not mention Aramco when it announced the rule change in July, nor asked during the consultation period whether the flotations by a sovereign state should have a separate category.\nBoth New York and London have vied for Aramco to host its flotation at their respective stock exchanges.\nIn April, UK Prime Minister Theresa May, visited Riyadh to meet Aramco's chief executive, Khalid al-Falih, who is also the kingdom's energy minister.\nAccompanied by Nikhil Rathi, the head of the London Stock Exchange, May attempted to lure Falih to allow London to host Aramco's flotation.\nDowning Street sources also told the Guardian that London's plans to host the flotation were specifically mentioned during several meetings between May and Saudi ministers in April.\nThe FCA confirmed that it received the letter and said it would reply in due course. It expects to complete its rule change consultation next month.\nA survey by the Chartered Institute for Securities and Investment (CISI) of more than 200 financial service professionals has found that a majority are opposed to the rule changes.'''
    # el = {"text": text}
    # ind_lst = index_data(el)
    # print(ind_lst)

    # aug = DataAugmentator()
    # sentences = aug.subsample_sentences(text)['text']
    # print(sentences['text'])

    # print(get_hash_and_db(ind_lst[0]))
    # print(get_hash_and_db(ind_lst[1]))

    # verify_text = 'MellodyFountaine. xxwantedbabyxx. MelissaColt. CARADEMENINOHappyVikkiXtremCockAnastasiaStele .Stefano86PIERCeCUmFUCKjeanexxx0MizzWendy .AmberKush0MizzWendyOrrianaxLovelyTeachr .0MizzWendyblackVScatleticSweetAylineeMikiAble .claudiaangel4uAmberKushblackVSatleticXElizaX .blackVSatleticjeanexxxAdelineAd3AnastasiaStele .GoddesssOfLoveeTiaCyrusdimemoletayrasensualxxx .JustUniqueNiceJohnXxxxninacpxxxDania1 .PIERCeCUmFUCKLeylaDelice1PrettyyBaby19kinkyrochellexx1 .NinaCrystalTylorLeeSweetAylineeAnastasiaStele .xxAriaxxDania1AnnaDiamondXXAmberKush .'
    # cut_list = cut_head_tail(verify_text)
    # print(cut_list)

    # input_text = [text,
    #               "ten toi la dung,ten toi la dung,ten toi la dung,ten toi la dung,ten toi la dung  ten toi la tao ten toi la tao ten toi la tao ten toi la tao ten  tao ten toi la tao ten toi la tao ten  tao ten toi la tao ten toi la tao ten  tao ten toi la tao ten toi la tao ten  tao ten toi la tao ten toi la tao ten  tao ten toi la tao ten toi la tao ten toi la tao"]
    # result = head_tail_api_pred_human(input_text)
    # print(result)
    verify()
