import io
import json
import os

from mob_data_anonymizer import PARAMETERS_FILE_DOESNT_EXIST, SUCCESS, PARAMETERS_FILE_NOT_JSON, PARAMETERS_NOT_VALID, \
    WRONG_METHOD, INPUT_FILE_NOT_EXIST
from mob_data_anonymizer.anonymization_methods.MegaSwap.MegaDynamicSwap import MegaDynamicSwap


def check_parameters_file(file_path: str) -> int:
    if not os.path.exists(file_path):
        return PARAMETERS_FILE_DOESNT_EXIST

    try:
        with open(file_path) as param_file:
            data = json.load(param_file)
    except io.UnsupportedOperation:
        return PARAMETERS_FILE_NOT_JSON

    try:
        #Check if input file exist
        if not os.path.exists(data['input']):
            return INPUT_FILE_NOT_EXIST

        method = data['method']
        if method == 'MegaSwap':
            pass
        elif method == 'SwapMob':
            pass
        elif method == 'Microaggregation':
            pass
        else:
            return WRONG_METHOD
    except KeyError:
        return PARAMETERS_NOT_VALID

    return SUCCESS


def anonymizer(file_path: str) -> int:

    with open(file_path) as param_file:
        data = json.load(param_file)

    method = data['method']
    if method == 'MegaSwap':
        anonymizer_method = MegaDynamicSwap.get_instance(data)
    elif method == 'SwapMob':
        pass
    elif method == 'Microaggregation':
        pass

