import io
import json
import os
import typer
import warnings
import sys
from mdl_anonymizer.client.make_api_call import MakeApiCall
from shapely.errors import ShapelyDeprecationWarning
from mdl_anonymizer import PARAMETERS_FILE_DOESNT_EXIST, PARAMETERS_FILE_NOT_JSON, INPUT_FILE_NOT_EXIST, \
    PARAMETERS_NOT_VALID, SUCCESS, WRONG_METHOD, OUTPUT_FOLDER_NOT_EXIST
from mdl_anonymizer.entities.Dataset import Dataset

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)

VALID_METHODS = ['min_locations',
                 'max_speed']


def check_parameters_file(file_path: str) -> int:
    if not os.path.exists(file_path):
        return PARAMETERS_FILE_DOESNT_EXIST

    try:
        with open(file_path) as param_file:
            data = json.load(param_file)
    except io.UnsupportedOperation:
        return PARAMETERS_FILE_NOT_JSON

    try:
        # Check if input files exist
        if not os.path.exists(data['input_filename']):
            return INPUT_FILE_NOT_EXIST

        # Check if all methods are valid
        methods = set().union(*(d.keys() for d in data['methods']))
        if not all(x in VALID_METHODS for x in methods):
            return WRONG_METHOD

    except KeyError:
        return PARAMETERS_NOT_VALID

    return SUCCESS


def check_parameters_file_api(file_path: str) -> int:
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

        # Check if all methods are valid
        methods = set().union(*(d.keys() for d in data['methods']))
        if not all(x in VALID_METHODS for x in methods):
            return WRONG_METHOD

    except KeyError:
        return PARAMETERS_NOT_VALID

    return SUCCESS


def filter_dataset(param_file_path: str):
    with open(param_file_path) as param_file:
        data = json.load(param_file)

    typer.secho(f'Loading original dataset')
    filename = data.get("input_filename")
    dataset = Dataset()
    methods = data["methods"]
    min_locations = 0
    max_speed = sys.maxsize
    for method in methods:
        if "min_locations" in method:
            min_locations = method["min_locations"]
        if "max_speed" in method:
            max_speed = method["max_speed"]
    dataset.from_file(filename, min_locations=min_locations, datetime_key="timestamp")
    dataset.filter_by_speed(max_speed_kmh=max_speed)
    dataset.to_csv(filename=data.get("output_filename"))


def filter_dataset_api(param_file_path: str):
    with open(param_file_path) as param_file:
        data = json.load(param_file)

    original_file = data["original_dataset"]
    api = MakeApiCall()

    action = "filter"
    response = api.post_user_data(action, original_file, param_file_path)

    print(f"Response: {response}")
    print(f"Received: {response.json()['message']}")
