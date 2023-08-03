import importlib
import json
import os

from mob_data_anonymizer.aggregation.TrajectoryAggregationInterface import TrajectoryAggregationInterface
from mob_data_anonymizer import CONFIG_FILE, WRONG_METHOD_PARAMETER, ERRORS


class AggregationMethodFactory:
    @staticmethod
    def get(method_name: str, params: dict = None) -> TrajectoryAggregationInterface:

        if params is None:
            params = {}

        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)

        if method_name not in config['aggregation_methods']:
            raise ValueError(f'Aggregation method not valid: {method_name}')

        method_config = config['aggregation_methods'][method_name]
        module_name, class_name = method_config['class'].rsplit('.', 1)
        module = importlib.import_module(module_name)
        method_class = getattr(module, class_name)

        try:
            return method_class(**params)
        except TypeError:
            # Wrong parameter
            raise ValueError(ERRORS[WRONG_METHOD_PARAMETER]) from None





