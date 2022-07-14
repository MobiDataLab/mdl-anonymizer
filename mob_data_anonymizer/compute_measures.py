import io
import json
import os
import skmob
import typer

from mob_data_anonymizer import PARAMETERS_FILE_DOESNT_EXIST, PARAMETERS_FILE_NOT_JSON, INPUT_FILE_NOT_EXIST, \
    OUTPUT_FOLDER_NOT_EXIST, PARAMETERS_NOT_VALID, SUCCESS, WRONG_METHOD, WRONG_MODE
from mob_data_anonymizer.utils.Measures import Measures

VALID_METHODS = ['mean_square_displacement',
                 'random_location_entropy',
                 'uncorrelated_location_entropy',
                 'visits_per_location',
                 'distance_straight_line']

VALID_MODES = ['average', 'export']


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
        if not os.path.exists(data['input_1']):
            return INPUT_FILE_NOT_EXIST

        if not os.path.exists(data['input_2']):
            return INPUT_FILE_NOT_EXIST

        # Check if output folder exist
        if not os.path.exists(data['output_folder']):
            return OUTPUT_FOLDER_NOT_EXIST

        # Check if mode is valid
        if not data['mode'] in VALID_MODES:
            return WRONG_MODE

        # Check if all methods are valid
        if not all(x in VALID_METHODS for x in data['methods']):
            return WRONG_METHOD

    except KeyError:
        return PARAMETERS_NOT_VALID

    return SUCCESS


def compute_measures(file_path: str) -> int:
    with open(file_path) as param_file:
        data = json.load(param_file)

    typer.secho(f'Loading first file')
    tdf_1 = skmob.TrajDataFrame.from_file(data['input_1'],
                                          latitude='lat',
                                          longitude='lon',
                                          user_id='user_id',
                                          datetime='timestamp')

    typer.secho(f'Loading second file')
    tdf_2 = skmob.TrajDataFrame.from_file(data['input_2'],
                                          latitude='lat',
                                          longitude='lon',
                                          user_id='user_id',
                                          datetime='timestamp')

    measures = Measures(tdf_1, tdf_2)

    for method in data['methods']:
        class_method = getattr(Measures, f'cmp_{method}')
        try:
            class_method(measures, data['mode'])
        except TypeError:
            class_method(measures)
