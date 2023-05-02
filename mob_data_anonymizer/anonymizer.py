import io
import json
import os

from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.factories.anonymization_method_factory import AnonymizationMethodFactory
from mob_data_anonymizer.make_api_call import MakeApiCall
from mob_data_anonymizer import PARAMETERS_FILE_DOESNT_EXIST, SUCCESS, PARAMETERS_FILE_NOT_JSON, PARAMETERS_NOT_VALID, \
    WRONG_METHOD, INPUT_FILE_NOT_EXIST, OUTPUT_FOLDER_NOT_EXIST, DEFAULT_OUTPUT_FILE, CONFIG_FILE


def check_parameters_file(file_path: str) -> int:
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    valid_methods = config['anonymization_methods']

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
        if method not in valid_methods:
            return WRONG_METHOD
    except KeyError:
        return PARAMETERS_NOT_VALID

    return SUCCESS


def anonymizer(file_path: str):
    with open(file_path) as param_file:
        data = json.load(param_file)

    # Load dataset
    filename = data.get("input_file")
    dataset = Dataset()
    dataset.from_file(filename)

    # Get instance of requested method
    method = AnonymizationMethodFactory.get(data['method'], dataset, data['params'])

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
    response = api.post_user_data(action, input_file, param_file_path)

    print(f"Response: {response}")
    print(f"Received: {response.json()['message']}")
