# The MIT License (MIT)
 # Copyright © 2024 It's AI
import copy

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

import bittensor as bt

from detection.protocol import TextSynapse
from detection.validator.reward import get_rewards
from detection.utils.uids import get_random_uids

import time
from typing import List
import torch

from neurons.miner import Miner

miner = Miner()

async def forward(self):
    """
    The forward function is called by the validator every time step.

    It is responsible for querying the network and scoring the responses.

    Args:
        self (:obj:`bittensor.neuron.Neuron`): The neuron object which contains all the necessary state for the validator.

    """
    bt.logging.info("Updating and querying available uids")
    # Define how the validator selects a miner to query, how often, etc.
    # bt.logging.info(f"STEPS {self.step} {self.step%300} {not (self.step % 300)}")

    available_axon_size = len(self.metagraph.axons) - 1 # Except our own
    miner_selection_size = min(available_axon_size, self.config.neuron.sample_size)
    # miner_uids = get_random_uids(self, k=miner_selection_size)
    miner_uids = [28, 31]
    axons = [self.metagraph.axons[uid] for uid in miner_uids]

    start_time = time.time()
    texts, labels = await self.build_queries()
    end_time = time.time()
    fake_miner(texts)
    bt.logging.info(f"Time to generate challenges: {int(end_time - start_time)}")

    responses: List[TextSynapse] = await self.dendrite(
        axons=axons,
        synapse=TextSynapse(texts=texts, predictions=[]),
        deserialize=True,
        timeout=self.config.neuron.timeout,
    )

    # Log the results for monitoring purposes.
    bt.logging.info(f"Received responses: {responses}")

    # Adjust the scores based on responses from miners.
    rewards, metrics = get_rewards(self, labels=labels, responses=responses)
    bt.logging.info("Rewards: {}".format(rewards))

    rewards_tensor = torch.tensor(rewards).to(self.device)
    uids_tensor = torch.tensor(miner_uids).to(self.device)
    self.update_scores(rewards_tensor, uids_tensor)

    self.log_step(miner_uids, metrics, rewards)


def fake_miner(texts):
    bt.logging.info(f"All of texts received: {str(texts)}")


    input_data = copy.deepcopy(texts)
    for i in range(len(input_data)):
        input_data[i] = input_data[i][3:]

    start_time = time.time()
    bt.logging.info(f"Amount of texts received: {len(input_data)}")
    preds = []
    if len(input_data) == 50:
        preds = miner.calculate_pred(input_data)
        miner.standard_current_model_pred(input_data)
        miner.consider_text_length(input_data)
    else:
        preds = miner.standard_model_pred(input_data)

    bt.logging.info(f"Made predictions in {int(time.time() - start_time)}s")