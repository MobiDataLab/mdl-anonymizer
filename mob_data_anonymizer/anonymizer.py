import io
import json
import os

from mob_data_anonymizer import PARAMETERS_FILE_DOESNT_EXIST, SUCCESS, PARAMETERS_FILE_NOT_JSON, PARAMETERS_NOT_VALID, \
    WRONG_METHOD, INPUT_FILE_NOT_EXIST, OUTPUT_FOLDER_NOT_EXIST, DEFAULT_OUTPUT_FILE, DEFAULT_SAVE_FILTERED_DATASET, \
    DEFAULT_FILTERED_FILE
from mob_data_anonymizer.anonymization_methods.SwapLocations.SwapLocations import SwapLocations
from mob_data_anonymizer.anonymization_methods.Microaggregation.Microaggregation import Microaggregation
from mob_data_anonymizer.anonymization_methods.SwapMob.SwapMob import SwapMob

VALID_METHODS = ['SwapLocations', 'SwapMob', 'Microaggregation']


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

    method = data['method']
    if method == 'SwapLocations':
        anonymizer_method = SwapLocations.get_instance(data)
    elif method == 'SwapMob':
        anonymizer_method = SwapMob.get_instance(data)
    elif method == 'Microaggregation':
        anonymizer_method = Microaggregation.get_instance(data)

    output_folder = data.get('output_folder', '')
    if output_folder != '':
        output_folder += '/'

    save_filtered_dataset = data.get('save_preprocessed_dataset', DEFAULT_SAVE_FILTERED_DATASET)
    if save_filtered_dataset:
        filtered_file = data.get('preprocessed_file', DEFAULT_FILTERED_FILE)
        anonymizer_method.dataset.export_to_scikit(f"{output_folder}{filtered_file}")

    anonymizer_method.run()

    output_dataset = anonymizer_method.get_anonymized_dataset()

    output_file = data.get('main_output_file', DEFAULT_OUTPUT_FILE)
    output_dataset.export_to_scikit(f"{output_folder}{output_file}")
