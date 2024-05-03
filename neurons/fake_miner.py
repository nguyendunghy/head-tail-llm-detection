import copy
import hashlib
import sys
import time

import bittensor as bt

from neurons.miners import jackie_upgrade, restful_api
from neurons.miners.deberta_classifier import DebertaClassifier
from neurons.miners.gpt_zero import PPLModel
from neurons.miners.utils import write


class FakeMiner:
    def __init__(self, model_type='deberta'):
        self.device = 'cuda:0'
        self.model_type = model_type
        if model_type == 'ppl':
            self.ppl_model = PPLModel(device=self.device)
            self.ppl_model.load_pretrained('models/ppl_model.pk')
        elif model_type == 'deberta':
            self.deberta_model = DebertaClassifier(foundation_model_path='models/deberta-v3-large-hf-weights',
                                                   model_path='models/deberta-large-ls03-ctx1024.pth',
                                                   device=self.device)
        elif model_type == 'combine_ppl_deberta':
            self.ppl_model = PPLModel(device=self.device)
            self.ppl_model.load_pretrained('models/ppl_model.pk')
            self.deberta_model = DebertaClassifier(foundation_model_path='models/deberta-v3-large-hf-weights',
                                                   model_path='models/deberta-large-ls03-ctx1024.pth',
                                                   device=self.device)
        else:
            bt.logging.error("invalid model type : " + str(model_type))
            sys.exit(1)

        self.human_data_path = '/root/jackie-dir/head-tail-llm-detection/human_data.txt'
        self.ai_data_path = '/root/jackie-dir/head-tail-llm-detection/ai_data.txt'
        self.combine_data_path = '/root/jackie-dir/head-tail-llm-detection/combine_data.txt'


    def fake_miner(self, input_data):
        start_time = time.time()
        bt.logging.info(f"Amount of texts received: {len(input_data)}")
        if len(input_data) == 300:
            write(str(input_data[:150]), self.ai_data_path)
            write(str(input_data[150:]), self.human_data_path)
            write(str(input_data), self.combine_data_path)

            if self.model_type == 'ppl':
                self.ppl_model_pred(input_data)
                self.jackie_upgrade_ppl_model_pred(input_data)
            elif self.model_type == 'deberta':
                self.deberta_model_pred(input_data)
                self.jackie_upgrade_deberta_model_pred(input_data)
            elif self.model_type == 'combine_ppl_deberta':
                self.ppl_model_pred(input_data)
                # self.jackie_upgrade_ppl_model_pred(input_data)
                self.deberta_model_pred(input_data)
                # self.jackie_upgrade_deberta_model_pred(input_data)
                self.combine_ppl_deberta_pred(input_data)



        bt.logging.info(f"Made predictions in {int(time.time() - start_time)}s")

    def deberta_model_pred(self, input_data):
        bt.logging.info("start deberta_model_pred")
        try:
            preds = self.deberta_model.predict_batch(input_data)
            preds = [el > 0.5 for el in preds]
        except Exception as e:
            bt.logging.error('Could not proceed text "{}..."'.format(input_data))
            bt.logging.error(e)
            preds = [0] * len(input_data)
        bt.logging.info("deberta_model_pred preds: " + str(preds))
        self.accuracy_monitor(preds, 'deberta_model_pred', input_data)
        return preds

    def deberta_model_prob(self, input_data):
        bt.logging.info("start deberta_model_prob")
        try:
            probs = self.deberta_model.predict_batch(input_data)
        except Exception as e:
            bt.logging.error('Could not proceed text "{}..."'.format(input_data))
            bt.logging.error(e)
            probs = [0] * len(input_data)
        bt.logging.info("deberta_model_prob prob: " + str(probs))
        return probs

    def ppl_model_pred(self, input_data):
        bt.logging.info("start ppl_model_pred")
        try:
            preds = self.ppl_model.predict_batch(input_data)
            preds = [el > 0.5 for el in preds]
        except Exception as e:
            bt.logging.error('Could not proceed text')
            bt.logging.error(e)
            preds = [0] * len(input_data)

        bt.logging.info("ppl_model_pred preds: " + str(preds))
        self.accuracy_monitor(preds, 'ppl_model_pred', input_data)
        return preds

    def ppl_model_prob(self, input_data):
        bt.logging.info("start ppl_model_prob")
        try:
            probs = self.ppl_model.predict_batch(input_data)
        except Exception as e:
            bt.logging.error('Could not proceed text')
            bt.logging.error(e)
            probs = [0] * len(input_data)

        bt.logging.info("ppl_model_prob probs: " + str(probs))
        self.accuracy_monitor(probs, 'ppl_model_prob', input_data)
        return probs
    def jackie_upgrade_ppl_model_pred(self, input_data):
        bt.logging.info("start jackie_upgrade_ppl_model_pred")
        try:
            prob_list = self.ppl_model.predict_batch(input_data)
        except Exception as e:
            bt.logging.error('Could not proceed text')
            bt.logging.error(e)
            prob_list = [0] * len(input_data)

        bt.logging.info("jackie_upgrade_ppl_model_pred prob_list: " + str(prob_list))
        pred_list = jackie_upgrade.order_prob(prob_list)
        bt.logging.info("jackie_upgrade_ppl_model_pred pred_list: " + str(pred_list))
        self.accuracy_monitor(pred_list, '50_50_ppl_model_pred', input_data)
        return pred_list, prob_list

    def jackie_upgrade_deberta_model_pred(self, input_data):
        bt.logging.info("start jackie_upgrade_deberta_model_pred")
        try:
            prob_list = self.deberta_model.predict_batch(input_data)
        except Exception as e:
            bt.logging.error('Could not proceed text "{}..."')
            bt.logging.error(e)
            prob_list = [0] * len(input_data)

        bt.logging.info("jackie_upgrade_deberta_model_pred prob_list: " + str(prob_list))
        pred_list = jackie_upgrade.order_prob(prob_list)
        bt.logging.info("jackie_upgrade_deberta_model_pred pred_list: " + str(pred_list))
        self.accuracy_monitor(pred_list, '50_50_deberta_model_pred', input_data)
        return pred_list, prob_list

    def combine_ppl_deberta_pred(self, input_data):
        bt.logging.info("start combine_ppl_deberta_pred")
        ppl_model_pred, ppl_model_prob = self.jackie_upgrade_ppl_model_pred(input_data)
        deberta_model_pred, deberta_model_prob = self.jackie_upgrade_deberta_model_pred(input_data)
        not_agree_list = []
        not_agree_point = []
        arr_len = len(input_data)
        for i in range(arr_len):
            if ppl_model_pred[i] != deberta_model_pred[i]:
                not_agree_list.append(i)
                not_agree_point.append(ppl_model_prob[i] + deberta_model_prob[i])
        bt.logging.info("not_agree_list: " + str(not_agree_list))
        bt.logging.info("not_agree_point: " + str(not_agree_point))

        agree_pred = jackie_upgrade.order_prob(not_agree_point)
        pt = 0
        for i in not_agree_list:
            ppl_model_pred[i] = agree_pred[pt]
            pt += 1
        self.accuracy_monitor(ppl_model_pred, '50_50_combine_ppl_deberta', input_data)
        return ppl_model_pred

    def combine_ppl_for_human_pred(self, input_data):
        bt.logging.info("start combine_ppl_for_human_pred")
        ppl_model_pred, ppl_model_prob = self.jackie_upgrade_ppl_model_pred(input_data)
        deberta_model_pred, deberta_model_prob = self.jackie_upgrade_deberta_model_pred(input_data)
        not_agree_list = []
        not_agree_point = []
        arr_len = len(input_data)
        for i in range(arr_len):
            if ppl_model_pred[i] != deberta_model_pred[i]:
                not_agree_list.append(i)
                not_agree_point.append(ppl_model_prob[i] + deberta_model_prob[i])
        bt.logging.info("not_agree_list: " + str(not_agree_list))
        bt.logging.info("not_agree_point: " + str(not_agree_point))

        agree_pred = jackie_upgrade.order_prob(not_agree_point)
        pt = 0
        for i in not_agree_list:
            ppl_model_pred[i] = agree_pred[pt]
            pt += 1
        self.accuracy_monitor(ppl_model_pred, '50_50_combine_ppl_deberta', input_data)
        return ppl_model_pred

    def accuracy_monitor(self, pred_list, model_type, input_list):
        bt.logging.info("start accuracy_monitor")
        tmp_pred_list = copy.deepcopy(pred_list)
        first_half = tmp_pred_list[:len(pred_list) // 2]
        second_half = tmp_pred_list[len(pred_list) // 2:]
        count_true = first_half.count(True)
        count_false = second_half.count(False)
        bt.logging.info(model_type + " correct count_true: " + str(count_true))
        bt.logging.info(model_type + " correct count_false: " + str(count_false))

        fail_ai_pred = []
        fail_hu_pred = []
        for i in range(len(pred_list)):
            if i < len(pred_list) // 2:
                if not pred_list[i]:
                    fail_ai_pred.append(input_list[i])
            else:
                if pred_list[i]:
                    fail_hu_pred.append(input_list[i])
        bt.logging.info(model_type + " fail_ai_pred: " + str(len(fail_ai_pred)))
        bt.logging.info(model_type + " fail_hu_pred: " + str(len(fail_hu_pred)))

        input_string = str(input_list)
        sha256_hash = hashlib.sha256(input_string.encode()).hexdigest()
        sha128_hash = sha256_hash[:32]
        restful_api.call_insert(text_hash=sha128_hash, model_type=model_type, count_human=count_false,
                                count_ai=count_true)
