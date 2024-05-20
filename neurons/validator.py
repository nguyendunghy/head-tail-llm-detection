# The MIT License (MIT)
# Copyright © 2024 It's AI

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.


from typing import List

import numpy as np

from detection.base.validator import BaseValidatorNeuron
from detection.model.data_generator import DataGenerator
from detection.model.text_completion import OllamaModel


class Validator(BaseValidatorNeuron):
    """
    Your validator neuron class. You should use this class to define your validator's behavior. In particular, you should replace the forward function with your own logic.

    This class inherits from the BaseValidatorNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a validator such as keeping a moving average of the scores of the miners and using them to set weights at the end of each epoch. Additionally, the scores are reset for new hotkeys at the end of each epoch.
    """

    def __init__(self, config=None):
        super(Validator, self).__init__(config=config)

        self.load_state()

        models = [OllamaModel(model_name='mistral:text'),
                  OllamaModel(model_name='llama3:text'),
                  OllamaModel(model_name='mixtral:text'),

                  OllamaModel(model_name='gemma:7b'),
                  OllamaModel(model_name='command-r'),
                  OllamaModel(model_name='neural-chat'),
                  OllamaModel(model_name='zephyr:7b-beta'),
                  OllamaModel(model_name='openhermes'),
                  OllamaModel(model_name='wizardcoder'),
                  OllamaModel(model_name='starling-lm:7b-beta'),
                  OllamaModel(model_name='yi:34b'),
                  OllamaModel(model_name='openchat:7b'),
                  OllamaModel(model_name='dolphin-mistral'),
                  OllamaModel(model_name='solar'),
                  OllamaModel(model_name='llama2:13b'),]


        self.generator = DataGenerator(models, None)

    async def build_queries(self) -> tuple[List[str], np.array]:
        data = self.generator.generate_data(n_human_samples=150, n_ai_samples=150)
        texts = [el.text for el in data]
        labels = np.array([int(el.label) for el in data])
        return texts, labels


