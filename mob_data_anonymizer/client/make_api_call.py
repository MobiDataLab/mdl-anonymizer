import requests
import json
from mob_data_anonymizer import CONFIG_API_FILE


class MakeApiCall:

    def __init__(self):
        with open(CONFIG_API_FILE) as f:
            config_api = json.load(f)
        self.api = config_api['api_server']

    def get_user_data(self, parameters):
        print(parameters)
        parameters = {"task_id": str(parameters["task_id"])}
        response = requests.get(f"{self.api}/task", params=parameters)
        if response.status_code == 200:
            print("successfully fetched the data with parameters provided")
        else:
            print(
                f"Hello person, there's a {response.status_code} error with your request")

        return response

    def post_user_data(self, action, input_file, param_file):
        files = [('input_dataset', open(input_file, 'rb')), ('config_file', open(param_file, 'rb'))]
        response = requests.post(f"{self.api}/{action}", files=files)
        if response.status_code == 200:
            print("successfully posted the data with parameters provided")
        else:
            print(
                f"Hello person, there's a {response.status_code} error with your request")

        return response

    def post_user_data2(self, action, original_file, anom_file, param_file):
        # print(parameters)
        files = [('original_dataset', open(original_file, 'rb')), ('anonymized_dataset', open(anom_file, 'rb')),
                 ('config_file', open(param_file, 'rb'))]
        response = requests.post(f"{self.api}/{action}", files=files)
        if response.status_code == 200:
            print("successfully posted the data with parameters provided")
        else:
            print(
                f"Hello person, there's a {response.status_code} error with your request")

        return response

