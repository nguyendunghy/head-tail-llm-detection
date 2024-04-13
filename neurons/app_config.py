import json
import traceback
from abc import ABC
import bittensor as bt


class AppConfig(ABC):

    def __init__(self, config_path='application.json'):
        self.config_path = config_path
        self.value = None
        try:
            self.default_app_config()
            self.load_app_config()
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()

    def default_app_config(self):
        bt.logging.info("start default_app_config")
        self.value = {
            "application": {
                "miner": {
                    "show_input": False,
                    "black_list_enable": True,
                    "custom_model": {
                        "active": True,
                        "num_input": [50]
                    }
                },
                "validator": {
                    "for_miner": [-1]
                }
            },
            "redis": {
                "active": False,
                "verify_data": {
                    "urls": [
                        "http://69.67.150.21:8080/verify-data",
                        "http://103.219.170.221:8080/verify-data"
                    ]
                }
            },
            "50_50_standard_model": {
                "active": True
            }
        }

    def allow_predict_with_custom_model(self, input_len):
        try:
            if not self.value['application']['miner']['custom_model']['active']:
                return False
            num_input = self.value['application']['miner']['custom_model']['num_input']

            # use custom model for all input_len
            if input_len == -1:
                return True

            if input_len in num_input:
                return True

            return False
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
        return False

    def allow_show_input(self):
        try:
            return self.value['application']['miner']['show_input']
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
        return True

    def enable_blacklist_validator(self):
        try:
            return self.value['application']['miner']['black_list_enable']
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
        return False

    def allow_predict_by_redis(self):
        try:
            return self.value['redis']['verify_data']['urls']
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
        return ["http://69.67.150.21:8080/verify-data", "http://103.219.170.221:8080/verify-data"]

    def get_redis_urls(self):
        try:
            return self.value['redis']['active']
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
        return False

    def allow_predict_50_50_standard_model(self):
        try:
            return self.value['50_50_standard_model']['active']
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
        return True

    def load_app_config(self):
        bt.logging.info("start load_app_config")

        try:
            with open(self.config_path, 'r') as file:
                self.value = json.load(file)
        except Exception as e:
            bt.logging.error(e)
            self.value = None
        finally:
            bt.logging.info("finish load_app_config " + str(self.value))
