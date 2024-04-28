import json
import traceback
from abc import ABC
import bittensor as bt


class AppConfig(ABC):

    def __init__(self, config_path='application.json'):
        self.config_path = config_path
        self.value = self.default_app_config()
        try:
            self.load_app_config()
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()

    def default_app_config(self):
        bt.logging.info("start default_app_config")
        value = {
            "application": {
                "miner": {
                    "show_input": False,
                    "black_list_enable": True,
                    "blacklist_hotkeys": [],
                    "whitelist_hotkeys": [],
                    "custom_model": {
                        "active": True,
                        "num_input": [50]
                    },
                    "validator_change": {
                        "active": True,
                        "num_input": [
                            300
                        ]
                    },
                    "standard_model": {
                        "urls": [
                            "http://154.20.200.88:44893/predict",
                            "http://154.20.200.88:44825/predict",
                            "http://174.95.185.181:41742/predict",
                            "http://174.95.185.181:41739/predict",
                            "http://70.48.87.64:41359/predict",
                            "http://70.48.87.64:41300/predict",
                            "http://108.53.57.130:50200/predict",
                            "http://108.53.57.130:50296/predict"
                        ],
                        "timeout": 10
                    },
                    "test_net": {
                        "enable_input_from_file": False,
                        "input_dir_path": "/root/head-tail-llm-detection",
                        "processed_dir_path": "/root/head-tail-llm-detection"
                    },
                    "num_make_incorrect": 0
                },
                "validator": {
                    "target_miner_uids": [-1],
                    "test_net": {
                        "enable_write_input_to_file": False,
                        "output_dir_path": "/root/head-tail-llm-detection"
                    }
                }
            },
            "redis": {
                "active": False,
                "verify_data": {
                    "urls": [
                        "http://69.67.150.21:8080/check-exists",
                        "http://103.219.170.221:8080/check-exists"
                    ],
                    "timeout": 12
                }
            },
            "50_50_standard_model": {
                "active": True
            }
        }
        return value

    def allow_predict_with_custom_model(self, input_len):
        try:
            if not self.value['application']['miner']['custom_model']['active']:
                return False
            num_input = self.value['application']['miner']['custom_model']['num_input']

            # use custom model for all input_len
            if len(num_input) == 1 and num_input[0] == -1:
                return True

            if input_len in num_input:
                return True

            return False
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
        return False

    def allow_predict_for_validator_change(self, input_len):
        try:
            if not self.value['application']['miner']['validator_change']['active']:
                return False
            num_input = self.value['application']['miner']['validator_change']['num_input']

            # use validator_change for all input_len
            if len(num_input) == 1 and num_input[0] == -1:
                return True

            if input_len in num_input:
                return True

            return False
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
        return True

    def allow_50_50_model_in_validator_change(self):
        try:
            return self.value['application']['miner']['validator_change']['50_50_model']
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

    def get_redis_urls(self):
        try:
            return self.value['redis']['verify_data']['urls']
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
        return ["http://69.67.150.21:8080/check-exists", "http://103.219.170.221:8080/check-exists"]

    def get_redis_timeout(self):
        try:
            return self.value['redis']['verify_data']['timeout']
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
        return 10

    def allow_predict_by_redis(self):
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

    def get_blacklist_hotkeys(self):
        try:
            return self.value['application']['miner']['blacklist_hotkeys']
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
        return []

    def get_whitelist_hotkeys(self):
        try:
            return self.value['application']['miner']['whitelist_hotkeys']
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
        return []

    def get_miner_uids_to_send_request(self):
        try:
            uids = self.value['application']['validator']['target_miner_uids']
            if len(uids) == 0:
                return [-1]
            return uids
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
        return [-1]

    def get_miner_test_input_dir_path(self):
        try:
            return self.value['application']['miner']['test_net']['input_dir_path']
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
        return '/root/head-tail-llm-detection'

    def get_miner_test_processed_dir_path(self):
        try:
            return self.value['application']['miner']['test_net']['processed_dir_path']
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
        return '/root/head-tail-llm-detection'

    def get_validator_test_output_dir_path(self):
        try:
            return self.value['application']['validator']['test_net']['output_dir_path']
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
        return '/root/head-tail-llm-detection'

    def enable_miner_get_input_from_file(self):
        try:
            return self.value['application']['miner']['test_net']['enable_input_from_file']
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
        return False

    def enable_validator_write_data_to_file(self):
        try:
            return self.value['application']['validator']['test_net']['enable_write_input_to_file']
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
        return False

    def get_number_predict_incorrect(self):
        try:
            return self.value['application']['miner']['num_make_incorrect']
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
        return 0

    def get_model_url(self):
        try:
            return self.value['application']['miner']['standard_model']['urls']
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
        return []

    def get_model_timeout(self):
        try:
            return self.value['application']['miner']['standard_model']['timeout']
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
        return 10

    def load_app_config(self):
        bt.logging.info("start load_app_config")

        try:
            with open(self.config_path, 'r') as file:
                self.value = json.load(file)
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
            self.value = self.default_app_config()
        finally:
            bt.logging.info("finish load_app_config " + str(self.value))

    def get_server_urls(self):
        try:
            return self.value['application']['miner']['server']['urls']
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
        return []

if __name__ == '__main__':
    app_config = AppConfig('/Users/nannan/IdeaProjects/bittensor/head-tail-llm-detection/application.json')
    print(app_config)
    print(app_config.value)
    print('allow_predict_50_50_standard_model', app_config.allow_predict_50_50_standard_model())
    print('allow_predict_with_custom_model', app_config.allow_predict_with_custom_model(50))
    print('allow_predict_by_redis', app_config.allow_predict_by_redis())
    print('get_redis_urls', app_config.get_redis_urls())
    print('enable_blacklist_validator', app_config.enable_blacklist_validator())
    print('allow_show_input', app_config.allow_show_input())
    print('get_blacklist_hotkeys', app_config.get_blacklist_hotkeys())
    print('get_whitelist_hotkeys', app_config.get_whitelist_hotkeys())
    print('get_miner_uids_to_send_request', app_config.get_miner_uids_to_send_request())

    print('enable_miner_get_input_from_file', app_config.enable_miner_get_input_from_file())
    print('enable_validator_write_data_to_file', app_config.enable_validator_write_data_to_file())
    print('get_miner_test_input_dir_path', app_config.get_miner_test_input_dir_path())
    print('get_miner_test_processed_dir_path', app_config.get_miner_test_processed_dir_path())
    print('get_validator_test_output_dir_path', app_config.get_validator_test_output_dir_path())
    print('get_number_predict_incorrect', app_config.get_number_predict_incorrect())
    print('get_model_url', app_config.get_model_url())
    print('get_redis_timeout', app_config.get_redis_timeout())
    print('get_model_timeout', app_config.get_model_timeout())

    print('allow_predict_for_validator_change', app_config.allow_predict_for_validator_change(300))
    print('get_server_urls', app_config.get_server_urls())

    while True:
        ...
