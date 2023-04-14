import io
import json
import os
import sys

from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.factories.anonymization_method_factory import AnoymizationMethodFactory
from mob_data_anonymizer.make_api_call import MakeApiCall
from mob_data_anonymizer import PARAMETERS_FILE_DOESNT_EXIST, SUCCESS, PARAMETERS_FILE_NOT_JSON, PARAMETERS_NOT_VALID, \
    WRONG_METHOD, INPUT_FILE_NOT_EXIST, OUTPUT_FOLDER_NOT_EXIST, DEFAULT_OUTPUT_FILE, DEFAULT_SAVE_FILTERED_DATASET, \
    DEFAULT_FILTERED_FILE
from mob_data_anonymizer.analysis_methods.AnalysisMethodInterface import AnalysisMethodInterface
from mob_data_anonymizer.anonymization_methods.AnonymizationMethodInterface import AnonymizationMethodInterface
# from mob_data_anonymizer.anonymization_methods.SwapLocations.SwapLocations import SwapLocations
from mob_data_anonymizer.anonymization_methods.Microaggregation.Microaggregation import Microaggregation
from mob_data_anonymizer.anonymization_methods.Microaggregation.TimePartMicroaggregation import TimePartMicroaggregation
from mob_data_anonymizer.anonymization_methods.Generalization.Simple import SimpleGeneralization
from mob_data_anonymizer.anonymization_methods.SwapMob.SwapMob import SwapMob
from mob_data_anonymizer.analysis_methods.QuadTreeHeatMap import QuadTreeHeatMap

VALID_METHODS = ['SwapLocations', 'SwapMob', 'Microaggregation', 'TimePartMicroaggregation', 'SimpleGeneralization']


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

    # Load dataset
    filename = data.get("input_file")
    dataset = Dataset()
    dataset.from_file(filename)

    # Get instance of requested method
    method = AnoymizationMethodFactory.get(data['method'], dataset, data['params'])

    # Filtered dataset

    #
    # save_filtered_dataset = data.get('save_preprocessed_dataset', DEFAULT_SAVE_FILTERED_DATASET)
    # if save_filtered_dataset:
    #     filtered_file = data.get('preprocessed_file', DEFAULT_FILTERED_FILE)
    #     method.dataset.to_csv(f"{output_folder}{filtered_file}")

    # Run method
    method.run()

    # Save output file
    output_folder = data.get('output_folder', '')
    if output_folder != '':
        output_folder += '/'
    output_file = data.get('main_output_file', DEFAULT_OUTPUT_FILE)

    output = method.get_anonymized_dataset()
    output.to_csv(f"{output_folder}{output_file}")


def anonymizer_api(param_file_path: str):
    with open(param_file_path) as param_file:
        data = json.load(param_file)

    input_file = data["input_file"]
    api = MakeApiCall()

    action = "anonymize"
    action += "/" + data['method']
    response = api.post_user_data(action, input_file, param_file_path)

    # with open(CONFIG_DB_FILE) as param_file:
    #     data = json.load(param_file)
    # output_file_path = data['db_folder'] + data['db_file']
    # with open(output_file_path, 'w') as f:
    #     json.dump(response.json(), f, indent=4)

    print(f"Response: {response}")
    print(f"Received: {response.json()['message']}")


def anonymizer_api_old(param_file_path: str):
    with open(param_file_path) as param_file:
        data = json.load(param_file)

    input_file = data["input_file"]
    api = MakeApiCall()

    action = "anonymize"
    action += "/" + data['method']
    response = api.post_user_data(action, data, input_file)

    # with open(CONFIG_DB_FILE) as param_file:
    #     data = json.load(param_file)
    # output_file_path = data['db_folder'] + data['db_file']
    # with open(output_file_path, 'w') as f:
    #     json.dump(response.json(), f, indent=4)

    print(f"Response: {response}")
    print(f"Received: {response.json()['message']}")
