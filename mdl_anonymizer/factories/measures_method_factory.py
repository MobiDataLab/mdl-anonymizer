import importlib
import json
import inspect
import logging

from mdl_anonymizer.measures_methods.MeasuresMethodInterface import MeasuresMethodInterface
from mdl_anonymizer.factories.trajectory_distance_factory import TrajectoryDistanceFactory
from mdl_anonymizer.entities.Dataset import Dataset
from mdl_anonymizer import CONFIG_FILE, DEFAULT_TRAJECTORY_DISTANCE, DEFAULT_CLUSTERING, DEFAULT_AGGREGATION, \
    WRONG_METHOD_PARAMETER


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
                distance_params = params['trajectory_distance'].get('params', {})
                params['trajectory_distance'] = TrajectoryDistanceFactory.get(distance_name, original_dataset,
                                                                              distance_params)
                name = distance_name
            else:
                # Default
                params['trajectory_distance'] = TrajectoryDistanceFactory.get(DEFAULT_TRAJECTORY_DISTANCE,
                                                                              original_dataset, {})
                name = DEFAULT_TRAJECTORY_DISTANCE
            logging.info(f"Trajectory distance for measures: {name}")

        try:
            return method_class(original_dataset, anom_dataset, **params)
        except TypeError:
            # Wrong parameter
            raise ValueError(WRONG_METHOD_PARAMETER) from None





