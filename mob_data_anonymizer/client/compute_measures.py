import io
import json
import os
import typer
import warnings
from client.make_api_call import MakeApiCall
from shapely.errors import ShapelyDeprecationWarning
from mob_data_anonymizer.factories.measures_method_factory import MeasuresMethodFactory
from mob_data_anonymizer import PARAMETERS_FILE_DOESNT_EXIST, PARAMETERS_FILE_NOT_JSON, INPUT_FILE_NOT_EXIST, \
    OUTPUT_FOLDER_NOT_EXIST, PARAMETERS_NOT_VALID, SUCCESS, WRONG_METHOD, DEFAULT_OUTPUT_FILE, CONFIG_FILE
from mob_data_anonymizer.entities.Dataset import Dataset

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)


def check_parameters_file(file_path: str) -> int:
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    valid_methods = config['measures_methods']

    if not os.path.exists(file_path):
        return PARAMETERS_FILE_DOESNT_EXIST

    try:
        with open(file_path) as param_file:
            data = json.load(param_file)
    except io.UnsupportedOperation:
        return PARAMETERS_FILE_NOT_JSON

    try:
        # Check if input files exist
        if not os.path.exists(data['original_dataset']):
            return INPUT_FILE_NOT_EXIST

        if not os.path.exists(data['anonymized_dataset']):
            return INPUT_FILE_NOT_EXIST

        # Check if output folder exist
        if not os.path.exists(data['output_folder']):
            return OUTPUT_FOLDER_NOT_EXIST

        measures = data['measures']
        for measure in measures:
            if measure['name'] not in valid_methods:
                return WRONG_METHOD

    except KeyError:
        return PARAMETERS_NOT_VALID

    return SUCCESS


def check_parameters_file_api(file_path: str) -> int:
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    valid_methods = config['measures_methods']

    if not os.path.exists(file_path):
        return PARAMETERS_FILE_DOESNT_EXIST

    try:
        with open(file_path) as param_file:
            data = json.load(param_file)
    except io.UnsupportedOperation:
        return PARAMETERS_FILE_NOT_JSON

    try:
        # Check if input files exist
        if not os.path.exists(data['original_dataset']):
            return INPUT_FILE_NOT_EXIST

        if not os.path.exists(data['anonymized_dataset']):
            return INPUT_FILE_NOT_EXIST

        measures = data['measures']
        for measure in measures:
            if measure['name'] not in valid_methods:
                return WRONG_METHOD

    except KeyError:
        return PARAMETERS_NOT_VALID

    return SUCCESS


def compute_measures(param_file_path: str):
    with open(param_file_path) as param_file:
        data = json.load(param_file)

    typer.secho(f'Loading original dataset')
    filename = data.get("original_dataset")
    original_dataset = Dataset()
    original_dataset.from_file(filename)

    typer.secho(f'Loading anonymized dataset')
    filename = data.get("anonymized_dataset")
    anonymized_dataset = Dataset()
    anonymized_dataset.from_file(filename)

    output_folder = data.get('output_folder', '')
    if output_folder != '':
        output_folder += '/'

    results = {}
    measures = data['measures']
    for measure in measures:
        # Get instance of requested method
        method = MeasuresMethodFactory.get(measure['name'], original_dataset, anonymized_dataset, measure['params'])

        # Run method
        method.run()

        result = method.get_result()
        results.update(result)

    # Save output file
    output_file = data.get('main_output_file', DEFAULT_OUTPUT_FILE)

    output_file_path = data["output_folder"] + "/" + output_file
    with open(output_file_path, 'w') as f:
        json.dump(results, f, indent=4)


def compute_measures_api(param_file_path: str):
    with open(param_file_path) as param_file:
        data = json.load(param_file)

    original_file = data["original_dataset"]
    anom_file = data["anonymized_dataset"]
    api = MakeApiCall()

    action = "compute_measures"
    response = api.post_user_data2(action, original_file, anom_file, param_file_path)

    print(f"Response: {response}")
    print(f"Received: {response.json()['message']}")
