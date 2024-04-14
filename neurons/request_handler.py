from abc import ABC
import json
from abc import ABC
from neurons.app_config import AppConfig
import time
import traceback
import typing
import bittensor as bt
from neurons import jackie_upgrade
from neurons.miners.head_tail_index import head_tail_api_pred_human


class RequestHandler(ABC):
    def __init__(self, model, app_config=None):
        if app_config is None:
            self.app_config = AppConfig()
        self.model = model

    def handle(self, input_data, result=None):
        start_time = time.time()
        bt.logging.info(f"Amount of texts received: {len(input_data)}")
        if self.app_config.allow_show_input():
            bt.logging.info("input_data: " + str(input_data))

        if self.app_config.allow_predict_with_custom_model(len(input_data)):
            try:
                if self.app_config.allow_predict_by_redis():
                    preds = self.head_tail_api_pred(input_data, result)
                elif self.app_config.allow_predict_50_50_standard_model():
                    preds = self.current_model_50_50_pred(input_data, result)
                else:
                    preds = self.standard_model_pred(input_data)
            except Exception as e:
                bt.logging.error(e)
                preds = self.standard_model_pred(input_data)
        else:
            preds = self.standard_model_pred(input_data)

        bt.logging.info(f"Made predictions in {int(time.time() - start_time)}s")
        return preds

    def standard_model_pred(self, input_data):
        bt.logging.info("start standard_model_pred")
        start_time = time.time()
        bt.logging.info(f"Amount of texts recieved: {len(input_data)}")

        try:
            preds = self.model.predict_batch(input_data)
            preds = [el > 0.5 for el in preds]
        except Exception as e:
            bt.logging.error('Couldnt proceed text "{}..."'.format(input_data))
            bt.logging.error(e)
            preds = [0] * len(input_data)
        self.log_prediction_result(pred_type='standard_model', pred_list=preds)
        bt.logging.info(f"Made standard_model_pred predictions in {int(time.time() - start_time)}s")
        return preds

    def current_model_50_50_pred(self, input_data, result=None):
        bt.logging.info("start current_model_50_50_pred")
        start_time = time.time()
        bt.logging.info(f"Amount of texts received: {len(input_data)}")

        try:
            prob_list = self.model.predict_batch(input_data)
        except Exception as e:
            bt.logging.error('Couldnt proceed text "{}..."'.format(input_data))
            bt.logging.error(e)
            prob_list = [0] * len(input_data)

        pred_list = jackie_upgrade.order_prob(prob_list)
        self.log_prediction_result(pred_type='current_model_50_50', pred_list=pred_list, result=result)
        bt.logging.info(f"Made predictions in {int(time.time() - start_time)}s")
        return pred_list

    def head_tail_api_pred(self, input_data, result=None):
        bt.logging.info("start head_tail_api_pred")
        start_time = time.time()
        pred_list = head_tail_api_pred_human(input_data, self.app_config.get_redis_urls())
        pred_list = [not pred for pred in pred_list]
        # Make some prediction incorrect to downgrade incentive
        num_incorrect = min(self.app_config.get_number_predict_incorrect(), len(pred_list))
        bt.logging.info("num_incorrect: " + str(num_incorrect))
        for i in range(num_incorrect):
            bt.logging.info("make pred at {} incorrect".format(str(i)))
            pred_list[i] = not pred_list[i]

        self.log_prediction_result(pred_type='head_tail', pred_list=pred_list, result=result)
        bt.logging.info(f"Made predictions in {int(time.time() - start_time)}s")
        return pred_list

    def log_prediction_result(self, pred_type, pred_list, result=None):
        try:
            bt.logging.info(pred_type + " pred_list: " + str(pred_list))
            bt.logging.info(pred_type + ' result of prediction: ' + str(result))
            if result is None:
                bt.logging.info(pred_type + " count ai: " + str(pred_list.count(True)))
                bt.logging.info(pred_type + " count hu: " + str(pred_list.count(False)))
            else:
                count_ai_correct = 0
                count_hu_correct = 0
                for i in range(len(pred_list)):
                    if str(pred_list[i]) == 'True' and str(result[i]) == 'True':
                        count_ai_correct += 1
                    if str(pred_list[i]) == 'False' and str(result[i]) == 'False':
                        count_hu_correct += 1
                bt.logging.info(pred_type + " count_ai_correct: " + str(count_ai_correct))
                bt.logging.info(pred_type + " count_hu_correct: " + str(count_hu_correct))
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()

