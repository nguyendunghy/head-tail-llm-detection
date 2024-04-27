import time
from abc import ABC

import bittensor as bt
from transformers.utils import logging as hf_logging

from miners.gpt_zero import PPLModel
from neurons import jackie_upgrade
from neurons.app_config import AppConfig
from neurons.miners.deberta_classifier import DebertaClassifier

hf_logging.set_verbosity(40)


class ModelService(ABC):

    def __init__(self,
                 model_type='deberta',
                 device='cuda:0',
                 ppl_model_path='models/ppl_model.pk',
                 deberta_foundation_model_path='models/deberta-v3-large-hf-weights',
                 deberta_model_path='models/deberta-large-ls03-ctx1024.pth'):
        self.app_config = AppConfig()
        self.model_type = model_type
        if model_type == 'ppl':
            self.model = PPLModel(device=device)
            self.model.load_pretrained(ppl_model_path)
        else:
            self.model = DebertaClassifier(foundation_model_path=deberta_foundation_model_path,
                                           model_path=deberta_model_path,
                                           device=device)

    def predict(self, input_data):
        app_config = AppConfig()
        bt.logging.info("app_config: " + str(app_config))
        if app_config.allow_predict_50_50_standard_model():
            return self.predict_50_50(input_data)
        else:
            return self.predict_baseline(input_data)

    def predict_baseline(self, input_data):
        bt.logging.info("start predict")
        start_time = time.time()
        bt.logging.info(f"Amount of texts received: {len(input_data)}")

        try:
            preds = self.model.predict_batch(input_data)
        except Exception as e:
            bt.logging.error('Could not proceed text "{}..."'.format(input_data))
            bt.logging.error(e)
            preds = [0] * len(input_data)

        result = preds.tolist() if self.model_type != 'ppl' else preds
        bt.logging.info("predict_list: " + str(result))
        bt.logging.info(f"standard model predictions in {int(time.time() - start_time)}s")
        return result

    def predict_50_50(self, input_data):
        bt.logging.info("start predict_50_50")
        start_time = time.time()
        bt.logging.info(f"Amount of texts received: {len(input_data)}")
        try:
            preds = self.model.predict_batch(input_data)
        except Exception as e:
            bt.logging.error('Could not proceed text "{}..."'.format(input_data))
            bt.logging.error(e)
            preds = [0] * len(input_data)

        temp_pred = preds.tolist() if self.model_type != 'ppl' else preds
        pred_list = jackie_upgrade.order_prob(temp_pred)
        result = [1 if value else 0 for value in pred_list]
        bt.logging.info(f"current_model_50_50_pred Made predictions in {int(time.time() - start_time)}s")
        return result
