import json
import time
import bittensor as bt

from detection.validator.data_augmentation import DataAugmentator
from neurons.miners.gpt_zero import PPLModel


def find_incorrect_human_text(file_path, start_line, end_line):
    """
    human writen text has model(text) < 0.5. In this function, we will find al sub-sentence that has mode(text)>0.5
    even it's human written text
    :param file_path:
    :param start_line:
    :param end_line:
    :return:
    """
    data_aug = DataAugmentator()
    model = PPLModel(device='cuda:0')
    model.load_pretrained('neurons/miners/ppl_model.pk')
    with open(file_path, 'r') as file:
        count = 1
        for line in file:
            if start_line <= count < end_line:
                data = json.loads(line)
                list_sub_sentence = data_aug.get_all_sub_sentences(data['text'])
                # bt.logging.info("list sub sentences: " + str(list_sub_sentence))
                bt.logging.info(
                    "text in line {} has {} sub-sentences".format(str(count), str(len(list_sub_sentence))))
                for i in range(len(list_sub_sentence)):
                    try:
                        res = model(list_sub_sentence[i])
                        bt.logging.info("process sub-sentence {} of line {}".format(str(i+1),str(count)))
                        if res > 0.5:
                            bt.logging.info("bad human text:" + str(count) + ":" + list_sub_sentence[i])
                    except Exception as e:
                        bt.logging.error(e)
            count += 1


if __name__ == '__main__':
    # model = PPLModel(device='cpu')
    # model.load_pretrained('neurons/miners/ppl_model.pk')
    # text = 'Hello world, i am here'
    # res = model(text)
    # print(res)
    start_time = time.time_ns()
    # file_path = "/root/c4_dataset/c4/extracted_file/c4-train.00001-of-01024.json"
    file_path = "/root/c4_dataset/c4/extracted_file/head-1000-00001.json"
    # file_path = "/root/c4_dataset/c4/extracted_file/head-10000-00001.json"

    find_incorrect_human_text(file_path, 0, 10001)
    bt.logging.info(f"time loading {int(time.time_ns() - start_time)}nanosecond")