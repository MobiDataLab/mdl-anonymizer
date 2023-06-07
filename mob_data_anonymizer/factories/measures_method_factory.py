import importlib
import json
import inspect
import logging

from mob_data_anonymizer.measures_methods.MeasuresMethodInterface import MeasuresMethodInterface
from mob_data_anonymizer.factories.trajectory_distance_factory import TrajectoryDistanceFactory
from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer import CONFIG_FILE, DEFAULT_TRAJECTORY_DISTANCE, DEFAULT_CLUSTERING, DEFAULT_AGGREGATION


class MeasuresMethodFactory:
    @staticmethod
    def get(method_name: str, original_dataset: Dataset, anom_dataset, params: dict = None) -> MeasuresMethodInterface:
        if params is None:
            params = {}

        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)

        if method_name not in config['measures_methods']:
            raise ValueError(f'Measure method not valid: {method_name}')

        method_config = config['measures_methods'][method_name]
        module_name, class_name = method_config['class'].rsplit('.', 1)
        module = importlib.import_module(module_name)
        method_class = getattr(module, class_name)

        method_signature = inspect.signature(method_class.__init__)

        # Special parameters (if required):
        # print(method_signature.parameters)
        if 'trajectory_distance' in method_signature.parameters:
            if 'trajectory_distance' in params:
                distance_name = params['trajectory_distance'].pop('name')
                params['trajectory_distance'] = TrajectoryDistanceFactory.get(distance_name, original_dataset,
                                                                              params['trajectory_distance']['params'])
                name = distance_name
            else:
                # Default
                params['trajectory_distance'] = TrajectoryDistanceFactory.get(DEFAULT_TRAJECTORY_DISTANCE,
                                                                              original_dataset, {})
                name = DEFAULT_TRAJECTORY_DISTANCE
            logging.info(f"Trajectory distance for measures: {name}")

        return method_class(original_dataset, anom_dataset, **params)





