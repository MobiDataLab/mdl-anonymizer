import importlib
import json
import inspect

from mob_data_anonymizer.measures_methods.MeasuresMethodInterface import MeasuresMethodInterface
from mob_data_anonymizer.factories.trajectory_distance_factory import TrajectoryDistanceFactory
from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer import CONFIG_FILE, DEFAULT_TRAJECTORY_DISTANCE, DEFAULT_CLUSTERING, DEFAULT_AGGREGATION


class MeasuresMethodFactory:
    @staticmethod
    def get(method_name: str, original_dataset: Dataset, anom_dataset, params: dict) -> MeasuresMethodInterface:

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
            print("TD required")
            if 'trajectory_distance' in params:
                print("TD")
                distance_name = params['trajectory_distance'].pop('name')
                params['trajectory_distance'] = TrajectoryDistanceFactory.get(distance_name, original_dataset,
                                                                              params['trajectory_distance']['params'])
                print(params['trajectory_distance'])
            else:
                # Default
                params['trajectory_distance'] = TrajectoryDistanceFactory.get(DEFAULT_TRAJECTORY_DISTANCE,
                                                                              original_dataset, {})

        return method_class(original_dataset, anom_dataset, **params)





