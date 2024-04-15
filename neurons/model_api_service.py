import time
from abc import ABC

import bittensor as bt
from transformers.utils import logging as hf_logging

from miners.gpt_zero import PPLModel
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

        if model_type == 'ppl':
            self.model = PPLModel(device=device)
            self.model.load_pretrained(ppl_model_path)
        else:
            self.model = DebertaClassifier(foundation_model_path=deberta_foundation_model_path,
                                           model_path=deberta_model_path,
                                           device=device)

    def predict(self, input_data):
        bt.logging.info("start predict")
        start_time = time.time()
        bt.logging.info(f"Amount of texts received: {len(input_data)}")

        try:
            preds = self.model.predict_batch(input_data)
        except Exception as e:
            bt.logging.error('Could not proceed text "{}..."'.format(input_data))
            bt.logging.error(e)
            preds = [0] * len(input_data)

        result = preds.tolist()
        bt.logging.info("predict_list: " + str(result))
        bt.logging.info(f"standard model predictions in {int(time.time() - start_time)}s")
        return result
