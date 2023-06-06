import importlib
import json
import os

from mob_data_anonymizer.aggregation.TrajectoryAggregationInterface import TrajectoryAggregationInterface
from mob_data_anonymizer import CONFIG_FILE


class AggregationMethodFactory:
    @staticmethod
    def get(method_name: str, params: dict) -> TrajectoryAggregationInterface:

        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)

        if method_name not in config['aggregation_methods']:
            raise ValueError(f'Aggregation method not valid: {method_name}')

        method_config = config['aggregation_methods'][method_name]
        module_name, class_name = method_config['class'].rsplit('.', 1)
        module = importlib.import_module(module_name)
        method_class = getattr(module, class_name)

        return method_class(**params)





