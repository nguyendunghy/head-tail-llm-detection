# The MIT License (MIT)
# Copyright © 2023 Nikita Dilman

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

import copy
import hashlib
import sys
import time
import typing

import bittensor as bt
from transformers.utils import logging as hf_logging

# Bittensor Miner Template:
import detection
# import base miner class which takes care of most of the boilerplate
from detection.base.miner import BaseMinerNeuron
from miners.gpt_zero import PPLModel
from neurons.miners import jackie_upgrade, restful_api
from neurons.miners.deberta_classifier import DebertaClassifier

hf_logging.set_verbosity(40)


class Miner(BaseMinerNeuron):
    """
    Your miner neuron class. You should use this class to define your miner's behavior. In particular, you should replace the forward function with your own logic. You may also want to override the blacklist and priority functions according to your needs.

    This class inherits from the BaseMinerNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a miner such as blacklisting unrecognized hotkeys, prioritizing requests based on stake, and forwarding requests to the forward function. If you need to define custom
    """

    def __init__(self, config=None):
        super(Miner, self).__init__(config=config)
        if self.config.neuron.model_type == 'upgrade_ppl':
            self.ppl_model = PPLModel(device=self.device)
            self.ppl_model.load_pretrained(self.config.neuron.ppl_model_path)
        elif self.config.neuron.model_type == 'upgrade_deberta':
            self.deberta_model = DebertaClassifier(
                foundation_model_path=self.config.neuron.deberta_foundation_model_path,
                model_path=self.config.neuron.deberta_model_path,
                device=self.device)
        elif self.config.neuron.model_type == 'combine_ppl_deberta':

            self.ppl_model = PPLModel(device=self.device)
            self.ppl_model.load_pretrained(self.config.neuron.ppl_model_path)

            self.deberta_model = DebertaClassifier(
                foundation_model_path=self.config.neuron.deberta_foundation_model_path,
                model_path=self.config.neuron.deberta_model_path,
                device=self.device)

        self.load_state()

    async def forward(
            self, synapse: detection.protocol.TextSynapse
    ) -> detection.protocol.TextSynapse:
        """
        Processes the incoming 'TextSynapse' synapse by performing a predefined operation on the input data.
        This method should be replaced with actual logic relevant to the miner's purpose.

        Args:
            synapse (detection.protocol.TextSynapse): The synapse object containing the 'texts' data.

        Returns:
            detection.protocol.TextSynapse: The synapse object with the 'predictions'.

        The 'forward' function is a placeholder and should be overridden with logic that is appropriate for
        the miner's intended operation. This method demonstrates a basic transformation of input data.
        """
        start_time = time.time()

        input_data = synapse.texts
        bt.logging.info(f"Amount of texts received: {len(input_data)}")

        if self.config.neuron.model_type == 'upgrade_ppl':
            preds, probs = self.jackie_upgrade_ppl_model_pred(input_data)
        elif self.config.neuron.model_type == 'upgrade_deberta':
            preds, probs = self.jackie_upgrade_deberta_model_pred(input_data)
        elif self.config.neuron.model_type == 'combine_ppl_deberta':
            preds = self.combine_ppl_deberta_pred(input_data)
        else:
            sys.exit(1)
        end_time = time.time()
        bt.logging.info("Time processing: " + str(end_time - start_time))
        synapse.predictions = preds
        return synapse

    async def blacklist(
            self, synapse: detection.protocol.TextSynapse
    ) -> typing.Tuple[bool, str]:
        """
        Determines whether an incoming request should be blacklisted and thus ignored. Your implementation should
        define the logic for blacklisting requests based on your needs and desired security parameters.

        Blacklist runs before the synapse data has been deserialized (i.e. before synapse.data is available).
        The synapse is instead contructed via the headers of the request. It is important to blacklist
        requests before they are deserialized to avoid wasting resources on requests that will be ignored.

        Args:
            synapse (detection.protocol.TextSynapse): A synapse object constructed from the headers of the incoming request.

        Returns:
            Tuple[bool, str]: A tuple containing a boolean indicating whether the synapse's hotkey is blacklisted,
                            and a string providing the reason for the decision.

        This function is a security measure to prevent resource wastage on undesired requests. It should be enhanced
        to include checks against the metagraph for entity registration, validator status, and sufficient stake
        before deserialization of synapse data to minimize processing overhead.

        Example blacklist logic:
        - Reject if the hotkey is not a registered entity within the metagraph.
        - Consider blacklisting entities that are not validators or have insufficient stake.

        In practice it would be wise to blacklist requests from entities that are not validators, or do not have
        enough stake. This can be checked via metagraph.S and metagraph.validator_permit. You can always attain
        the uid of the sender via a metagraph.hotkeys.index( synapse.dendrite.hotkey ) call.

        Otherwise, allow the request to be processed further.
        """
        if synapse.dendrite.hotkey not in self.metagraph.hotkeys:
            # Ignore requests from unrecognized entities.
            bt.logging.trace(
                f"Blacklisting unrecognized hotkey {synapse.dendrite.hotkey}"
            )
            self.blacklist_hotkeys.add(synapse.dendrite.hotkey)
            bt.logging.info(f'List of blacklisted hotkeys: {self.blacklist_hotkeys}')
            return True, "Unrecognized hotkey"

        uid = self.metagraph.hotkeys.index(synapse.dendrite.hotkey)

        stake = self.metagraph.S[uid].item()
        if stake < self.config.blacklist.minimum_stake_requirement:
            self.blacklist_hotkeys.add(synapse.dendrite.hotkey)
            bt.logging.info(f'List of blacklisted hotkeys: {self.blacklist_hotkeys}')
            return True, "pubkey stake below min_allowed_stake"

        bt.logging.trace(
            f"Not Blacklisting recognized hotkey {synapse.dendrite.hotkey}"
        )

        bt.logging.info("Receive request from hotkey {}".format(str(self.blacklist_hotkeys)))

        white_list = ["5GWxNNk1pabmXYJhDs9YTuFQyFjtP7PY1vHQ9146H3fbupcg",
                      "5F4QGegVgPQXtjaPT7FcZSmZoMim7WjBV6Eunh4Tkz7wJtzE",
                      "5FgrHxz3KAuXaeEy48siYaQs9MyZUVxdrghaXmpGmC51AkXk",
                      "5Fet4PZ7XeLdc5o65hWXSY7jHUgieHKKT5Nb2HS4yGqqoMw3",
                      "5GudRU6YNWMoR6cW9L567nr9pg5HYkXnqCDgfXMEp4sCTuPv",
                      "5FnmM3aSCmGQstQuVrQDQor6w4MpmyUZDCWmqkGqsateqTBk",
                      "5EJHh9ca5w194ufHrnDiEBgA7AoWwD5aGzKuUAgEEBxdjBbD",
                      "5CJkaV6Xujf12PY8fJRfPFCm3WDWHuzrCr7yrfi5AH4Gunmg",
                      "5DPdXPrYCTnsUDh2nYZMCAUb3d6h8eouDCF3zhdw8ru3czSm"]
        if str(synapse.dendrite.hotkey) in white_list:
            return False, "whitelist hotkey"

        return True, "Not team's hotkey !"

    async def priority(self, synapse: detection.protocol.TextSynapse) -> float:
        """
        The priority function determines the order in which requests are handled. More valuable or higher-priority
        requests are processed before others. You should design your own priority mechanism with care.

        This implementation assigns priority to incoming requests based on the calling entity's stake in the metagraph.

        Args:
            synapse (detection.protocol.TextSynapse): The synapse object that contains metadata about the incoming request.

        Returns:
            float: A priority score derived from the stake of the calling entity.

        Miners may recieve messages from multiple entities at once. This function determines which request should be
        processed first. Higher values indicate that the request should be processed first. Lower values indicate
        that the request should be processed later.

        Example priority logic:
        - A higher stake results in a higher priority value.
        """
        caller_uid = self.metagraph.hotkeys.index(
            synapse.dendrite.hotkey
        )  # Get the caller index.
        prirority = float(
            self.metagraph.S[caller_uid]
        )  # Return the stake as the priority.
        bt.logging.trace(
            f"Prioritizing {synapse.dendrite.hotkey} with value: ", prirority
        )
        return prirority

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
        return ppl_model_pred


# This is the main function, which runs the miner.
if __name__ == "__main__":
    with Miner() as miner:
        while True:
            bt.logging.info("Miner running...", time.time())
            time.sleep(30)
