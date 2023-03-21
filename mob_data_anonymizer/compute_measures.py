import io
import json
import os
import skmob
import typer
import warnings

from mob_data_anonymizer.make_api_call import MakeApiCall
from shapely.errors import ShapelyDeprecationWarning

from mob_data_anonymizer import PARAMETERS_FILE_DOESNT_EXIST, PARAMETERS_FILE_NOT_JSON, INPUT_FILE_NOT_EXIST, \
    OUTPUT_FOLDER_NOT_EXIST, PARAMETERS_NOT_VALID, SUCCESS, WRONG_METHOD, WRONG_MODE
from mob_data_anonymizer import CONFIG_DB_FILE
from mob_data_anonymizer.utils.Measures import Measures
from mob_data_anonymizer.distances.trajectory.Martinez2021.Distance import Distance
from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.utils.Stats import Stats
from mob_data_anonymizer.utils.utils import round_tuple

VALID_METHODS = ['mean_square_displacement',
                 'random_location_entropy',
                 'uncorrelated_location_entropy',
                 'visits_per_location',
                 'distance_straight_line']

VALID_MODES = ['average', 'export']

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)


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
        if not os.path.exists(data['original_dataset']):
            return INPUT_FILE_NOT_EXIST

        if not os.path.exists(data['anonymized_dataset']):
            return INPUT_FILE_NOT_EXIST

        # Check if output folder exist
        if not os.path.exists(data['output_folder']):
            return OUTPUT_FOLDER_NOT_EXIST

        # # Check if mode is valid
        # if not data['mode'] in VALID_MODES:
        #     return WRONG_MODE
        #
        # # Check if all methods are valid
        # if not all(x in VALID_METHODS for x in data['methods']):
        #     return WRONG_METHOD

    except KeyError:
        return PARAMETERS_NOT_VALID

    return SUCCESS


def compute_measures_old(file_path: str) -> int:
    with open(file_path) as param_file:
        data = json.load(param_file)

    typer.secho(f'Loading original dataset')
    tdf_1 = skmob.TrajDataFrame.from_file(data['original_dataset'],
                                          latitude='lat',
                                          longitude='lon',
                                          user_id='user_id',
                                          datetime='timestamp')

    typer.secho(f'Loading anonymized dataset')
    tdf_2 = skmob.TrajDataFrame.from_file(data['anonymized_dataset'],
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


def compute_measures(param_file_path: str):
    with open(param_file_path) as param_file:
        data = json.load(param_file)

    typer.secho(f'Loading original dataset')
    filename = data.get("original_dataset")
    original_dataset = Dataset()
    original_dataset.from_file(filename, datetime_key="timestamp")

    typer.secho(f'Loading anonymized dataset')
    filename = data.get("anonymized_dataset")
    anonymized_dataset = Dataset()
    anonymized_dataset.from_file(filename, datetime_key="timestamp")

    martinez21_distance = Distance(original_dataset)
    martinez21_distance_norm = Distance(original_dataset, landa=martinez21_distance.landa,
                                        max_dist=martinez21_distance.max_dist, normalized=True)


    results = {}
    # @TODO: Unify Stats and Measures classes

    stats = Stats(original_dataset, anonymized_dataset)
    results["percen_traj_removed"] = round(stats.get_perc_of_removed_trajectories() * 100, 2)
    print(f'% Removed trajectories: {results["percen_traj_removed"]}%')
    results["percen_loc_removed"] = round(stats.get_perc_of_removed_locations() * 100, 2)
    print(f'% Removed locations: {results["percen_loc_removed"]}%')
    results["rsme"] = round(stats.get_rsme(martinez21_distance), 4)
    print(f'RSME: {results["rsme"]}')
    results["rsme_normalized"] = round(stats.get_rsme(martinez21_distance_norm), 4)
    print(f'RSME normalized: {results["rsme_normalized"]}')
    results["propensity"] = round(stats.get_propensity_score(), 4)
    print(f'Propensity score: {results["propensity"]}')
    results["percen_record_linkage"] = round(stats.get_fast_record_linkage(martinez21_distance), 2)
    print(f'% Record linkage: {results["percen_record_linkage"]}')

    # typer.secho(f'Loading original dataset')
    # tdf_1 = skmob.TrajDataFrame.from_file(data.get("original_dataset"),
    #                                       latitude='lat',
    #                                       longitude='lon',
    #                                       user_id='user_id',
    #                                       datetime='timestamp')
    #
    # typer.secho(f'Loading anonymized dataset')
    # tdf_2 = skmob.TrajDataFrame.from_file(data.get("anonymized_dataset"),
    #                                       latitude='lat',
    #                                       longitude='lon',
    #                                       user_id='user_id',
    #                                       datetime='timestamp')

    measures = Measures(original_dataset.to_tdf(), anonymized_dataset.to_tdf())
    results["visits_per_location_original"], results["visits_per_location_anonymized"] \
        = round_tuple(measures.cmp_visits_per_location(), 4)
    print(f"visits per location: Original={results['visits_per_location_original']} - "
          f"Anonymized={results['visits_per_location_anonymized']}")
    results["distance_straight_line_original"], results["distance_straight_line_anonymized"] \
        = round_tuple(measures.cmp_distance_straight_line(), 4)
    print(f"Distance straight line: Original={results['distance_straight_line_original']} - "
          f"Anonymized={results['distance_straight_line_anonymized']}")
    results["uncorrelated_location_entropy_original"], results["uncorrelated_location_entropy_anonymized"] \
        = round_tuple(measures.cmp_uncorrelated_location_entropy(), 4)
    print(f"Uncorrelated location entropy: Original={results['uncorrelated_location_entropy_original']} - "
          f"Anonymized={results['uncorrelated_location_entropy_a']}")
    results["random_location_entropy_original"], results["random_location_entropy_anonymized"] \
        = round_tuple(measures.cmp_random_location_entropy(), 4)
    print(f"Random location entropy: Original={results['random_location_entropy_original']} - "
          f"Anonymized={results['random_location_entropy_anonymized']}")
    results["mean_square_displacement_original"], results["mean_square_displacement_anonymized"] \
        = round_tuple(measures.cmp_mean_square_displacement(), 4)
    print(f"Mean square displacement: Original={results['mean_square_displacement_original']} - "
          f"Anonymized={results['mean_square_displacement_anonymized']}")

    output_file_path = data["output_folder"] + "/" + data["main_output_file"]
    with open(output_file_path, 'w') as f:
        json.dump(results, f, indent=4)


def compute_measures_api(param_file_path: str):
    with open(param_file_path) as param_file:
        data = json.load(param_file)

    original_file = data["original_dataset"]
    anom_file = data["anonymized_dataset"]
    api = MakeApiCall()

    action = "compute_measures"
    response = api.post_user_data2(action, data, original_file, anom_file)

    output_file_path = data["output_folder"] + "/" + data["main_output_file"]
    with open(output_file_path, 'w') as f:
        json.dump(response.json(), f, indent=4)

    print(f"Received: {response}")


def compute_measures_api_back(param_file_path: str):
    with open(param_file_path) as param_file:
        data = json.load(param_file)

    original_file = data["original_dataset"]
    anom_file = data["anonymized_dataset"]
    api = MakeApiCall()

    action = "compute_measures"
    response = api.post_user_data2(action, data, original_file, anom_file)

    output_file_path = data["output_folder"] + "/" + data["main_output_file"]
    with open(output_file_path, 'w') as f:
        json.dump(response.json(), f, indent=4)

    print(f"Received: {response}")


def compute_measures_api_back_db(param_file_path: str):
    with open(param_file_path) as param_file:
        data = json.load(param_file)

    original_file = data["original_dataset"]
    anom_file = data["anonymized_dataset"]
    api = MakeApiCall()

    action = "compute_measures"
    response = api.post_user_data2(action, data, original_file, anom_file)

    # with open(CONFIG_DB_FILE) as param_file:
    #     data = json.load(param_file)
    # output_file_path = data['db_folder'] + data['db_file']
    # with open(output_file_path, 'w') as f:
    #     json.dump(response.json(), f, indent=4)

    print(f"Response: {response}")
    print(f"Received: {response.json()['message']}")
