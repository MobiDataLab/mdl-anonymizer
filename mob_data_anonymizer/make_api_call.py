import requests
import json


class MakeApiCall:

    def __init__(self, api):
        self.api = api

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
        response = requests.get(f"{self.api}", params=parameters)
        if response.status_code == 200:
            print("successfully fetched the data with parameters provided")
            self.formatted_print(response.json())
        else:
            print(
                f"Hello person, there's a {response.status_code} error with your request")

        return response

    def post_user_data(self, action, parameters, input_file):
        # print(parameters)
        files = [('files', open(input_file, 'rb'))]
        response = requests.post(f"{self.api}/{action}", params=parameters, files= files)
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
        response = requests.post(f"{self.api}/{action}", params=parameters, files= files)
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

