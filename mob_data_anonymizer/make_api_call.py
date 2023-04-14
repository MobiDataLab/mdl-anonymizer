import requests
import json
from mob_data_anonymizer import CONFIG_API_FILE


class MakeApiCall:

    def __init__(self):
        with open(CONFIG_API_FILE) as f:
            config_api = json.load(f)
        self.api = config_api['api_server']

    def get_data(self):
        response = requests.get(f"{self.api}")
        if response.status_code == 200:
            print("successfully fetched the data")
            self.formatted_print(response.json())
        else:
            print(
                f"Hello person, there's a {response.status_code} error with your request")

        return response

    def get_user_data(self, parameters):
        print(parameters)
        parameters = {"task_id": str(parameters["task_id"])}
        response = requests.get(f"{self.api}/task", params=parameters)
        # response = requests.get(f"{self.api}/task", params={'task_id': "0000"})
        if response.status_code == 200:
            print("successfully fetched the data with parameters provided")
            # self.formatted_print(response.json())
        else:
            print(
                f"Hello person, there's a {response.status_code} error with your request")

        return response

    def post_user_data(self, action, input_file, param_file):
        # print(parameters)
        files = [('data_file', open(input_file, 'rb')), ('config_file', open(param_file, 'rb'))]
        response = requests.post(f"{self.api}/{action}", files=files)
        if response.status_code == 200:
            print("successfully posted the data with parameters provided")
        else:
            print(
                f"Hello person, there's a {response.status_code} error with your request")

        return response

    def post_user_data_old(self, action, parameters, input_file, param_file):
        # print(parameters)
        files = [('files', open(input_file, 'rb')), ('files', open(param_file, 'rb'))]
        response = requests.post(f"{self.api}/{action}", params=parameters, files=files)
        if response.status_code == 200:
            print("successfully posted the data with parameters provided")
            print(f"Sent: {parameters}")
            # print(f"Sent: {self.formatted_print(response.json())}")
        else:
            print(
                f"Hello person, there's a {response.status_code} error with your request")

        return response

    def post_user_data2(self, action, parameters, original_file, anom_file):
        # print(parameters)
        files = [('files', open(original_file, 'rb')), ('files', open(anom_file, 'rb'))]
        response = requests.post(f"{self.api}/{action}", params=parameters, files=files)
        if response.status_code == 200:
            print("successfully posted the data with parameters provided")
            print(f"Sent: {parameters}")
            # print(f"Sent: {self.formatted_print(response.json())}")
        else:
            print(
                f"Hello person, there's a {response.status_code} error with your request")

        return response

    def formatted_print(self, obj):
        text = json.dumps(obj, sort_keys=True, indent=4)
        print(text)
