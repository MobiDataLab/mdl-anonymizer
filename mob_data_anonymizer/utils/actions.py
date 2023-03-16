import sys
import logging
import skmob
import typer
import json

from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.distances.trajectory.Martinez2021.Distance import Distance
from mob_data_anonymizer.utils.Stats import Stats
from mob_data_anonymizer import PARAMETERS_FILE_DOESNT_EXIST, SUCCESS, PARAMETERS_FILE_NOT_JSON, PARAMETERS_NOT_VALID, \
    WRONG_METHOD, INPUT_FILE_NOT_EXIST, OUTPUT_FOLDER_NOT_EXIST, DEFAULT_OUTPUT_FILE, DEFAULT_SAVE_FILTERED_DATASET, \
    DEFAULT_FILTERED_FILE, CONFIG_DB_FILE
from mob_data_anonymizer.methodName import MethodName
from mob_data_anonymizer.analysis_methods.AnalysisMethodInterface import AnalysisMethodInterface
from mob_data_anonymizer.anonymization_methods.AnonymizationMethodInterface import AnonymizationMethodInterface
from mob_data_anonymizer.anonymization_methods.SwapLocations.SwapLocations import SwapLocations
from mob_data_anonymizer.anonymization_methods.Microaggregation.Microaggregation import Microaggregation
from mob_data_anonymizer.anonymization_methods.Microaggregation.Microaggregation2 import Microaggregation2
from mob_data_anonymizer.anonymization_methods.Generalization.Simple import SimpleGeneralization
from mob_data_anonymizer.anonymization_methods.SwapMob.SwapMob import SwapMob
from mob_data_anonymizer.analysis_methods.QuadTreeHeatMap import QuadTreeHeatMap
from mob_data_anonymizer.utils.Measures import Measures

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO)


def anonymize(method, params, file) -> str:
    data = params.dict()
    print(method)

    # Get instance of requested method
    class_object = getattr(sys.modules[__name__], method)
    print("Anonymization method: ", class_object.__name__)
    method = class_object.get_instance(data, file)

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

    output_file_path = data["output_folder"] + "/" + data["main_output_file"]
    return output_file_path


def anonymize_back(method, params, file, filename, task_id) -> str:
    data = params.dict()
    print(method)

    # Get instance of requested method
    class_object = getattr(sys.modules[__name__], method)
    print("Anonymization method: ", class_object.__name__)
    method = class_object.get_instance(data, file, filename)

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
    with open(CONFIG_DB_FILE) as param_file:
        data = json.load(param_file)
    output_file = data["db_folder"] + "/" + task_id + ".csv"
    output = method.get_anonymized_dataset()
    output.to_csv(f"{output_file}")


def analyze(params, file) -> str:
    data = params.dict()
    method = data["method"]
    print(method)

    # Get instance of requested method
    class_object = getattr(sys.modules[__name__], data['method'])
    print("Analysis method: ", class_object.__name__)
    method = class_object.get_instance(data, file)

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

    method.export_result(f"{output_folder}{output_file}")
    return output_file


def analyze_back(params, file, filename, task_id):
    data = params.dict()
    method = data["method"]
    print(data)

    # Get instance of requested method
    class_object = getattr(sys.modules[__name__], data['method'])
    print("Analysis method: ", class_object.__name__)
    method = class_object.get_instance(data, file, filename)

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
    with open(CONFIG_DB_FILE) as param_file:
        data = json.load(param_file)
    output_file = data["db_folder"] + "/" + task_id + ".json"
    method.export_result(f"{output_file}")


def measures(params, original_file, anom_file) -> dict:
    data = params.dict()
    typer.secho(f'Loading original dataset')

    original_dataset = Dataset()
    if original_file is None:
        filename = data.get("original_file")
    else:
        filename = original_file

    original_dataset.from_file(filename, datetime_key="timestamp")

    typer.secho(f'Loading anonymized dataset')

    anonymized_dataset = Dataset()
    if anom_file is None:
        filename = data.get("anonymized_file")
    else:
        filename = anom_file

    anonymized_dataset.from_file(filename, datetime_key="timestamp")

    martinez21_distance = Distance(original_dataset)
    martinez21_distance_norm = Distance(original_dataset, landa=martinez21_distance.landa,
                                        max_dist=martinez21_distance.max_dist, normalized=True)

    stats = Stats(original_dataset, anonymized_dataset)
    results = {}
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

    return results


def measures_back(params, original_file, anom_file, original_filename, anom_filename, task_id):
    data = params.dict()
    typer.secho(f'Loading original dataset')

    original_dataset = Dataset()
    if original_file is None:
        filename = data.get("original_file")
    else:
        filename = original_file

    original_dataset.from_file(filename, original_filename, datetime_key="timestamp")

    typer.secho(f'Loading anonymized dataset')

    anonymized_dataset = Dataset()
    if anom_file is None:
        filename = data.get("anonymized_file")
    else:
        filename = anom_file

    anonymized_dataset.from_file(filename, anom_filename, datetime_key="timestamp")

    martinez21_distance = Distance(original_dataset)
    martinez21_distance_norm = Distance(original_dataset, landa=martinez21_distance.landa,
                                        max_dist=martinez21_distance.max_dist, normalized=True)

    stats = Stats(original_dataset, anonymized_dataset)
    results = {}
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

    # output_file_path = data["output_folder"] + "/" + task_id + ".json"
    with open(CONFIG_DB_FILE) as param_file:
        data = json.load(param_file)
    output_file_path = data["db_folder"] + "/" + task_id + ".json"
    with open(output_file_path, 'w') as f:
        json.dump(results, f, indent=4)
