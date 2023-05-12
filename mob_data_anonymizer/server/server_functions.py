import sys
import logging
import typer
import json
from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer import CONFIG_DB_FILE
from mob_data_anonymizer.factories.anonymization_method_factory import AnonymizationMethodFactory
from mob_data_anonymizer.factories.analysis_method_factory import AnalysisMethodFactory
from mob_data_anonymizer.factories.measures_method_factory import MeasuresMethodFactory
from pathlib import Path
import warnings

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO)
warnings.filterwarnings('ignore')


def anonymize(file, filename, params, task_id):
    print("Anonymization method: ", params['method'])

    # Load dataset
    dataset = Dataset()
    dataset.from_file(file, filename)

    # Get instance of requested method
    method = AnonymizationMethodFactory.get(params['method'], dataset, params['params'])

    # Run method
    method.run()

    # Save output file
    with open(CONFIG_DB_FILE) as param_file:
        data = json.load(param_file)
    output_file = data["db_folder"] + "/" + task_id + ".csv"
    output = method.get_anonymized_dataset()
    output.to_csv(f"{output_file}")

    logging.info("Done!")


def analyze(file, filename, params, task_id):
    print("Analysis method: ", params['method'])

    # Load dataset
    dataset = Dataset()
    dataset.from_file(file, filename)

    # Get instance of requested method
    method = AnalysisMethodFactory.get(params['method'], dataset, params['params'])

    # Run method
    method.run()

    # Save output file
    with open(CONFIG_DB_FILE) as param_file:
        data = json.load(param_file)
    output_file = data["db_folder"] + "/" + task_id + ".json"
    method.export_result(f"{output_file}")

    logging.info("Done!")


def measures(original_file, anom_file, original_filename, anom_filename, params, task_id):
    typer.secho(f'Loading original dataset')
    original_dataset = Dataset()
    original_dataset.from_file(original_file, original_filename)

    typer.secho(f'Loading anonymized dataset')
    anonymized_dataset = Dataset()
    anonymized_dataset.from_file(anom_file, anom_filename)

    results = {}
    measures = params['measures']
    for measure in measures:
        print("Measures method: ", measure['name'])
        # Get instance of requested method
        method = MeasuresMethodFactory.get(measure['name'], original_dataset, anonymized_dataset, measure['params'])

        # Run method
        method.run()

        result = method.get_result()
        results.update(result)

    with open(CONFIG_DB_FILE) as param_file:
        data = json.load(param_file)
    output_file_path = data["db_folder"] + "/" + task_id + ".json"
    with open(output_file_path, 'w') as f:
        json.dump(results, f, indent=4)

    logging.info("Done!")


def filter(file, filename, params, task_id):
    typer.secho(f'Loading original dataset')

    dataset = Dataset()

    methods = params["methods"]
    min_locations = 0
    max_speed = sys.maxsize
    for method in methods:
        if "min_locations" in method:
            min_locations = method["min_locations"]
        if "max_speed" in method:
            max_speed = method["max_speed"]

    dataset.from_file(file, filename, min_locations=min_locations, datetime_key="timestamp")
    dataset.filter_by_speed(max_speed_kmh=max_speed)

    # Save filtered file
    with open(CONFIG_DB_FILE) as param_file:
        data = json.load(param_file)
    output_file = data["db_folder"] + "/" + task_id + ".csv"
    dataset.to_csv(f"{output_file}")

    logging.info("Done!")


def return_task(task_id):
    with open(CONFIG_DB_FILE) as param_file:
        data = json.load(param_file)
    filename = data['db_folder'] + task_id + ".json"
    path = Path(filename)
    if path.is_file():
        return filename
    filename = data['db_folder'] + task_id + ".csv"
    path = Path(filename)
    if path.is_file():
        return filename

    return None
