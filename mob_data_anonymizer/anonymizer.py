import io
import json
import os

from mob_data_anonymizer import PARAMETERS_FILE_DOESNT_EXIST, SUCCESS, PARAMETERS_FILE_NOT_JSON, PARAMETERS_NOT_VALID, \
    WRONG_METHOD, INPUT_FILE_NOT_EXIST, OUTPUT_FOLDER_NOT_EXIST
from mob_data_anonymizer.anonymization_methods.MegaSwap.MegaDynamicSwap import MegaDynamicSwap

VALID_METHODS = ['MegaSwap', 'SwapMob', 'Microaggregation']


def check_parameters_file(file_path: str) -> int:
    if not os.path.exists(file_path):
        return PARAMETERS_FILE_DOESNT_EXIST

    try:
        with open(file_path) as param_file:
            data = json.load(param_file)
    except io.UnsupportedOperation:
        return PARAMETERS_FILE_NOT_JSON

    try:
        # Check if input file exist
        if not os.path.exists(data['input']):
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

    save_filtered_dataset = data.get('save_filtered_dataset', True)

    method = data['method']
    if method == 'MegaSwap':
        anonymizer_method = MegaDynamicSwap.get_instance(data, save_filtered_dataset)
    elif method == 'SwapMob':
        pass
    elif method == 'Microaggregation':
        pass

    anonymizer_method.run()
    output_dataset = anonymizer_method.get_anonymized_dataset()

    output_dataset.export_to_scikit(f"{data['output_folder']}output.csv")
