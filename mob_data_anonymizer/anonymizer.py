import io
import json
import os
import sys

from make_api_call import MakeApiCall
from mob_data_anonymizer import PARAMETERS_FILE_DOESNT_EXIST, SUCCESS, PARAMETERS_FILE_NOT_JSON, PARAMETERS_NOT_VALID, \
    WRONG_METHOD, INPUT_FILE_NOT_EXIST, OUTPUT_FOLDER_NOT_EXIST, DEFAULT_OUTPUT_FILE, DEFAULT_SAVE_FILTERED_DATASET, \
    DEFAULT_FILTERED_FILE
from mob_data_anonymizer.analysis_methods.AnalysisMethodInterface import AnalysisMethodInterface
from mob_data_anonymizer.anonymization_methods.AnonymizationMethodInterface import AnonymizationMethodInterface
from mob_data_anonymizer.anonymization_methods.SwapLocations.SwapLocations import SwapLocations
from mob_data_anonymizer.anonymization_methods.Microaggregation.Microaggregation import Microaggregation
from mob_data_anonymizer.anonymization_methods.Microaggregation.Microaggregation2 import Microaggregation2
from mob_data_anonymizer.anonymization_methods.SwapMob.SwapMob import SwapMob
from mob_data_anonymizer.analysis_methods.QuadTreeHeatMap import QuadTreeHeatMap

VALID_METHODS = ['SwapLocations', 'SwapMob', 'Microaggregation', 'Microaggregation2']


def check_parameters_file(file_path: str) -> int:
    if not os.path.exists(file_path):
        return PARAMETERS_FILE_DOESNT_EXIST

    try:
        with open(file_path) as param_file:
            data = json.load(param_file)
    except io.UnsupportedOperation:
        return PARAMETERS_FILE_NOT_JSON

    try:
        # Check if input file exists
        if not os.path.exists(data['input_file']):
            return INPUT_FILE_NOT_EXIST

        # Check if output folder exist
        if not os.path.exists(data['output_folder']):
            return OUTPUT_FOLDER_NOT_EXIST

        method = data['method']
        if method not in VALID_METHODS:
            return WRONG_METHOD
    except KeyError:
        return PARAMETERS_NOT_VALID

    return SUCCESS


def anonymizer(file_path: str) -> int:
    with open(file_path) as param_file:
        data = json.load(param_file)

    # Get instance of requested method
    class_object = getattr(sys.modules[__name__], data['method'])
    print("Anonymization method: ", class_object.__name__)
    method = class_object.get_instance(data)

    # Filtered dataset
    output_folder = data.get('output_folder', '')
    if output_folder != '':
        output_folder += '/'

    save_filtered_dataset = data.get('save_preprocessed_dataset', DEFAULT_SAVE_FILTERED_DATASET)
    if save_filtered_dataset:
        filtered_file = data.get('preprocessed_file', DEFAULT_FILTERED_FILE)
        method.dataset.to_csv(f"{output_folder}{filtered_file}")

    # Run method
    method.run()

    # Save output file
    output_file = data.get('main_output_file', DEFAULT_OUTPUT_FILE)

    output = method.get_anonymized_dataset()
    output.to_csv(f"{output_folder}{output_file}")


def anonymizer_api(param_file_path: str) -> int:
    with open(param_file_path) as param_file:
        data = json.load(param_file)

    input_file = data["input_file"]
    api = MakeApiCall()

    action = "anonymize"
    action += "/" + data['method']
    response = api.post_user_data(action, data, input_file)

    output_file_path = data["output_folder"] + "/" + data["main_output_file"]
    with open(output_file_path, 'wb') as f:
        f.write(response.content)

    print(f"Received: {response}")


def anonymizer_api_back(param_file_path: str):
    with open(param_file_path) as param_file:
        data = json.load(param_file)

    input_file = data["input_file"]
    api = MakeApiCall()

    action = "anonymizeback"
    action += "/" + data['method']
    response = api.post_user_data(action, data, input_file)

    output_file_path = data["output_folder"] + "/" + data["main_output_file"]
    with open(output_file_path, 'wb') as f:
        f.write(response.content)

    print(f"Received: {response}")


def anonymizer_api_back_db(param_file_path: str):
    with open(param_file_path) as param_file:
        data = json.load(param_file)

    input_file = data["input_file"]
    api = MakeApiCall()

    action = "anonymizeback"
    action += "/" + data['method']
    response = api.post_user_data(action, data, input_file)

    # with open(CONFIG_DB_FILE) as param_file:
    #     data = json.load(param_file)
    # output_file_path = data['db_folder'] + data['db_file']
    # with open(output_file_path, 'w') as f:
    #     json.dump(response.json(), f, indent=4)

    print(f"Response: {response}")
    print(f"Received: {response.json()['message']}")
