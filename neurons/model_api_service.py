import time
from abc import ABC

import bittensor as bt
from transformers.utils import logging as hf_logging

from detection.utils.config import config
from miners.gpt_zero import PPLModel
from neurons.app_config import AppConfig
from neurons.miners.deberta_classifier import DebertaClassifier

hf_logging.set_verbosity(40)


class ModelService(ABC):
    def __int__(self, device='cuda:0'):

        self.app_config = AppConfig()
        self.config = config()
        bt.logging.info("config: " + str(self.config))
        self.device = self.config.neuron.device
        if self.config.neuron.model_type == 'ppl':
            self.model = PPLModel(device=self.device)
            self.model.load_pretrained(self.config.neuron.ppl_model_path)
        else:
            self.model = DebertaClassifier(foundation_model_path=self.config.neuron.deberta_foundation_model_path,
                                           model_path=self.config.neuron.deberta_model_path,
                                           device=self.device)

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

        bt.logging.info("predict_list: " + str(preds))
        bt.logging.info("count ai: " + str(preds.count(True)))
        bt.logging.info("count hu: " + str(preds.count(False)))
        bt.logging.info(f"standard model predictions in {int(time.time() - start_time)}s")
        return preds
