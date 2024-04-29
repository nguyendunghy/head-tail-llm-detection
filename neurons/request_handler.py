import copy
import time
import traceback
from abc import ABC
import random
import bittensor as bt
import requests

from neurons import jackie_upgrade
from neurons.app_config import AppConfig
from neurons.miners.head_tail_index import head_tail_api_pred_human
from neurons.miners.utils import gen_hash
from neurons.model_api_service import ModelService


class RequestHandler(ABC):
    def __init__(self, app_config=None):
        self.app_config = AppConfig() if app_config is None else app_config
        self.model_service = ModelService(model_type='deberta')

    def handle(self, input_data, result=None):
        start_time = time.time()
        bt.logging.info(f"Amount of texts received: {len(input_data)}")
        self.app_config.load_app_config()
        bt.logging.info("app_config: " + str(self.app_config))

        if self.app_config.allow_show_input():
            bt.logging.info("input_data: " + str(input_data))

        key_hash = gen_hash(str(input_data))
        # check in cache first
        if self.app_config.allow_using_cache_redis():
            # get first because 90% cache hit
            cached_pred = self.get_redis_cached(input_data, self.app_config.get_redis_cached_get_urls())
            bt.logging.info("existed cache: " + str(cached_pred))
            if cached_pred is not None and len(cached_pred) == len(input_data):
                return cached_pred

            exist = self.check_key_exist(input_data, self.app_config.get_redis_check_hash_existed_urls(), hash=key_hash)
            if exist == 'EXISTED_VALUE_NULL':
                bt.logging.info("key existed, value null, start waiting value inserted from hash: " + str(key_hash))
                count = 0
                while exist != 'EXISTED_VALUE_NOT_NULL':
                    if count > 2 * self.app_config.get_model_timeout():
                        break
                    bt.logging.info("wait for value from hash: {}  count: {}".format(str(key_hash), str(count)))
                    time.sleep(0.5)
                    exist = self.check_key_exist(input_data, self.app_config.get_redis_check_hash_existed_urls(),
                                                 hash=key_hash)
                    count = count + 1

                bt.logging.info("value filled to key {}, start getting cache. existed state: {}"
                                .format(str(key_hash), str(exist)))
                if exist == 'EXISTED_VALUE_NOT_NULL':
                    cached_pred = self.get_redis_cached(input_data, self.app_config.get_redis_cached_get_urls(),
                                                        hash=key_hash)
                    bt.logging.info("prediction in cache: " + str(cached_pred))
                    if cached_pred is not None and len(cached_pred) == len(input_data):
                        return cached_pred

            elif exist == 'EXISTED_VALUE_NOT_NULL':
                cached_pred = self.get_redis_cached(input_data, self.app_config.get_redis_cached_get_urls())
                bt.logging.info("cache in memory: " + str(cached_pred))
                if cached_pred is not None and len(cached_pred) == len(input_data):
                    return cached_pred

            elif exist == 'NOT_EXISTED':
                bt.logging.info("hash key not exists,start running prediction")

        # predict using model
        if self.app_config.allow_predict_with_custom_model(len(input_data)):
            bt.logging.info("CASE I")
            preds = self.custom_model_pred(input_data=input_data, result=result)
        elif self.app_config.allow_predict_for_validator_change(len(input_data)):
            bt.logging.info("CASE II")
            preds = self.custom_model_pred_for_validator_change(input_data=input_data, result=result)
        else:
            bt.logging.info("CASE IV")
            preds = self.standard_model_pred(input_data)

        if self.app_config.allow_using_cache_redis() and preds.count(False) != len(input_data):
            self.save_pred_to_reds(input_data=input_data, preds=preds, urls=self.app_config.get_redis_cached_set_urls(),
                                   hash=key_hash)

        bt.logging.info(f"Made predictions in {int(time.time() - start_time)}s")
        return preds

    def save_pred_to_reds(self, input_data, preds, urls, hash=None):
        bt.logging.info("start save_pred_to_reds {}".format(str(urls)))
        hash_key = hash if hash is not None else gen_hash(str(input_data))
        random.shuffle(urls)
        for url in urls:
            try:
                body_data = {"hash_key": hash_key, "preds": preds}
                bt.logging.info("body_data: " + str(body_data))
                headers = {
                    'Content-Type': 'application/json'
                }
                response = requests.request("POST", url, headers=headers, json=body_data, timeout=10)
                if response.status_code == 200:
                    bt.logging.info("Save preds to redis cache url {} success".format(url))

            except Exception as e:
                bt.logging.error(e)
                traceback.print_exc()

    def check_key_exist(self, input_data, urls, hash=None):
        bt.logging.info("start check_key_exist {}".format(str(urls)))
        hash_key = hash if hash is not None else gen_hash(str(input_data))
        random.shuffle(urls)
        for url in urls:
            try:
                body_data = {"hash_key": hash_key, "preds": []}
                bt.logging.info("body_data: " + str(body_data))
                headers = {
                    'Content-Type': 'application/json'
                }
                response = requests.request("POST", url, headers=headers, json=body_data, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    result = data['result']
                    if result == 'EXISTED_VALUE_NULL' or result == 'EXISTED_VALUE_NOT_NULL' or result == 'NOT_EXISTED':
                        return result
            except Exception as e:
                bt.logging.error(e)
                traceback.print_exc()
        return 'NOT_EXISTED'

    def get_redis_cached(self, input_data, urls, hash=None):
        bt.logging.info("start get_redis_cached urls {} ".format(str(urls)))
        random.shuffle(urls)
        hash_key = hash if hash is not None else gen_hash(str(input_data))
        for url in urls:
            try:
                body_data = {"hash_key": hash_key}
                bt.logging.info("body_data: " + str(body_data))
                headers = {
                    'Content-Type': 'application/json'
                }
                response = requests.request("POST", url, headers=headers, json=body_data, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    cached_result = data['result']
                    if cached_result is not None and len(cached_result) == len(input_data):
                        return cached_result

            except Exception as e:
                bt.logging.error(e)
                traceback.print_exc()
        return []

    def custom_model_pred(self, input_data, result=None):
        bt.logging.info("start custom_model_pred")
        try:
            if self.app_config.allow_predict_by_redis():
                redis_prediction = self.head_tail_api_pred(input_data, result)
                return redis_prediction
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()

        try:
            if self.app_config.allow_predict_50_50_standard_model():
                _50_50_standard_predict = self.current_model_50_50_pred(input_data, result)
                return _50_50_standard_predict
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()

        standard_prediction = self.standard_model_pred(input_data)
        return standard_prediction

    def custom_model_pred_for_validator_change(self, input_data, result=None):
        try:
            bt.logging.info("CASE V")
            if self.app_config.allow_predict_50_50_standard_model():
                _50_50_standard_predict = self.current_model_50_50_pred(input_data, result)
                return _50_50_standard_predict
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
        bt.logging.info("CASE VI")
        standard_prediction = self.standard_model_pred(input_data)
        return standard_prediction

    def standard_model_pred(self, input_data):
        bt.logging.info("start standard_model_pred")
        start_time = time.time()
        bt.logging.info(f"Amount of texts received: {len(input_data)}")
        try:
            prob_list = self.model_service.predict(input_data)
            preds = [el > 0.5 for el in prob_list]
            self.log_prediction_result(pred_type='standard_model', pred_list=preds)
            bt.logging.info(f"Made standard_model_pred predictions in {int(time.time() - start_time)}s")
            return preds
        except Exception as e:
            bt.logging.error('Could not proceed text "{}..."'.format(input_data))
            bt.logging.error(e)
            traceback.print_exc()

        bt.logging.info(f"Made standard_model_pred predictions in {int(time.time() - start_time)}s")
        return [False] * len(input_data)

    def current_model_50_50_pred(self, input_data, result=None):
        bt.logging.info("start current_model_50_50_pred")
        start_time = time.time()
        bt.logging.info(f"Amount of texts received: {len(input_data)}")
        try:
            prob_list = self.model_service.predict(input_data)
            pred_list = jackie_upgrade.order_prob(prob_list)
            self.log_prediction_result(pred_type='current_model_50_50', pred_list=pred_list, result=result)
            bt.logging.info(f"current_model_50_50_pred Made predictions in {int(time.time() - start_time)}s")
            return pred_list
        except Exception as e:
            bt.logging.error('Couldnt proceed text "{}..."'.format(input_data))
            bt.logging.error(e)
        bt.logging.info(f"current_model_50_50_pred Made predictions in {int(time.time() - start_time)}s")
        return [False] * len(input_data)

    def head_tail_api_pred(self, input_data, result=None):
        bt.logging.info("start head_tail_api_pred")
        start_time = time.time()
        pred_list = head_tail_api_pred_human(list_text=input_data, urls=self.app_config.get_redis_urls(),
                                             timeout=self.app_config.get_redis_timeout())
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


if __name__ == '__main__':
    ...
