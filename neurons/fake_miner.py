import copy
import hashlib
import time
import bittensor as bt
from miners.gpt_zero import PPLModel
from neurons.miners import jackie_upgrade, restful_api
from neurons.miners.gpt_zero_api import is_human_generated_files
from neurons.miners.old_gpt_zero import GPT2PPL


class FakeMiner:
    def __init__(self):
        self.device = 'cuda:0'
        self.model = PPLModel(device=self.device)
        self.model.load_pretrained('neurons/miners/ppl_model.pk')
        self.old_model = GPT2PPL(device=self.device)

    def fake_miner(self, texts):
        bt.logging.info(f"All of texts received: {str(texts)}")

        input_data = copy.deepcopy(texts)
        for i in range(len(input_data)):
            input_data[i] = input_data[i][3:]

        start_time = time.time()
        bt.logging.info(f"Amount of texts received: {len(input_data)}")
        preds = []
        if len(input_data) == 50:
            preds = self.calculate_pred(input_data)
            self.standard_current_model_pred(input_data)
            self.consider_text_length(input_data)
        else:
            preds = self.standard_model_pred(input_data)

        bt.logging.info(f"Made predictions in {int(time.time() - start_time)}s")

    def gpt_zero_api_pred(self, input_data):
        bt.logging.info("start gpt_zero_api_pred")
        pred_list = is_human_generated_files(input_data)
        self.accuracy_monitor(pred_list, 'gpt_zero_api', input_data)
        return pred_list

    def jackie_old_model_pred(self, input_data):
        bt.logging.info("start jackie_old_model_pred")
        prob_list = []
        for text in input_data:
            try:
                pred_prob = self.old_model(text)
            except Exception as e:
                pred_prob = 0
                bt.logging.error('Couldnt proceed text "{}..."'.format(input_data))
                bt.logging.error(e)
            prob_list.append(pred_prob)

        bt.logging.info("jackie_old_model_pred prob_list: " + str(prob_list))
        pred_list = jackie_upgrade.order_prob(prob_list)
        bt.logging.info("jackie_old_model_pred pred_list: " + str(pred_list))
        self.accuracy_monitor(pred_list, '50_50_old_model', input_data)
        return pred_list, prob_list

    def standard_model_pred(self, input_data):
        bt.logging.info("start standard_model_pred")
        preds = []
        for text in input_data:
            try:
                prob = self.model(text)
                pred_prob = prob > 0.5
            except Exception as e:
                pred_prob = 0
                bt.logging.error('Couldnt proceed text "{}..."'.format(input_data))
                bt.logging.error(e)
            preds.append(pred_prob)
        return preds

    def calculate_pred(self, input_data):
        bt.logging.info("start calculate_pred")
        curr_model_pred, curr_model_prob = self.jackie_current_model_pred(input_data)
        old_model_pred, old_model_prob = self.jackie_old_model_pred(input_data)
        not_agree_list = []
        not_agree_point = []
        arr_len = len(input_data)
        for i in range(arr_len):
            if curr_model_pred[i] != old_model_pred[i]:
                not_agree_list.append(i)
                not_agree_point.append(curr_model_prob[i] + old_model_prob[i])
        bt.logging.info("not_agree_list: " + str(not_agree_list))
        bt.logging.info("not_agree_point: " + str(not_agree_point))

        agree_pred = jackie_upgrade.order_prob(not_agree_point)
        pt = 0
        for i in not_agree_list:
            curr_model_pred[i] = agree_pred[pt]
            pt += 1
        self.accuracy_monitor(curr_model_pred, '50_50_combine_models', input_data)
        return curr_model_pred

    def accuracy_monitor(self, pred_list, model_type, input_list):
        bt.logging.info("start accuracy_monitor")
        tmp_pred_list = copy.deepcopy(pred_list)
        first_half = tmp_pred_list[:len(pred_list) // 2]
        second_half = tmp_pred_list[len(pred_list) // 2:]
        count_true = first_half.count(True)
        count_false = second_half.count(False)
        bt.logging.info(model_type + " correct count_true: " + str(count_true))
        bt.logging.info(model_type + " correct count_false: " + str(count_false))

        input_string = str(input_list)
        sha256_hash = hashlib.sha256(input_string.encode()).hexdigest()
        sha128_hash = sha256_hash[:32]
        restful_api.call_insert(text_hash=sha128_hash, model_type=model_type, count_human=count_true,
                                count_ai=count_false)

    def standard_current_model_pred(self, input_data):
        pred_list = []
        for text in input_data:
            try:
                # true is ai, false is human
                pred = self.model(text) > 0.5
            except Exception as e:
                pred = 0
                bt.logging.error('Couldnt proceed text "{}..."'.format(input_data))
                bt.logging.error(e)
            pred_list.append(pred)

        self.accuracy_monitor(pred_list, 'standard_current_model', input_data)
        return pred_list

    def consider_text_length(self, input_data):
        pred_list = []
        short_text_list = []
        for i in range(len(input_data)):
            text = input_data[i]
            try:
                if len(text) < 250:
                    short_text_list.append(i)
                    pred = True
                else:
                    pred = self.model(text) > 0.5
            except Exception as e:
                pred = 0
                bt.logging.error('Couldnt proceed text "{}..."'.format(input_data))
                bt.logging.error(e)
            pred_list.append(pred)
        bt.logging.info('short_text_list: ' + str(short_text_list) + str(len(short_text_list)))
        self.accuracy_monitor(pred_list, 'consider_text_length', input_data)
        return pred_list

    def jackie_current_model_pred(self, input_data):
        bt.logging.info("start jackie_current_model_pred")
        prob_list = []
        for text in input_data:
            try:
                pred_prob = self.model(text)
            except Exception as e:
                pred_prob = 0
                bt.logging.error('Couldnt proceed text "{}..."'.format(input_data))
                bt.logging.error(e)
            prob_list.append(pred_prob)

        bt.logging.info("jackie_current_model_pred prob_list: " + str(prob_list))
        pred_list = jackie_upgrade.order_prob(prob_list)
        bt.logging.info("jackie_current_model_pred pred_list: " + str(pred_list))
        self.accuracy_monitor(pred_list, '50_50_current_model', input_data)
        return pred_list, prob_list