import importlib
import inspect
import json
import logging

from mob_data_anonymizer.distances.trajectory.DistanceInterface import DistanceInterface
from mob_data_anonymizer.entities.Dataset import Dataset
from mob_data_anonymizer.factories.aggregation_method_factory import AggregationMethodFactory
from mob_data_anonymizer.factories.trajectory_distance_factory import TrajectoryDistanceFactory
from mob_data_anonymizer import CONFIG_FILE, DEFAULT_TRAJECTORY_DISTANCE, DEFAULT_AGGREGATION


class ClusteringMethodFactory:
    @staticmethod
    def get(method_name: str, dataset: Dataset, params: dict) -> DistanceInterface:

        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)

        if method_name not in config['clustering_methods']:
            raise ValueError(f'Clustering method not valid: {method_name}')

        method_config = config['clustering_methods'][method_name]
        module_name, class_name = method_config['class'].rsplit('.', 1)
        module = importlib.import_module(module_name)
        method_class = getattr(module, class_name)

        params['dataset'] = dataset

        method_signature = inspect.signature(method_class.__init__)

        # Special parameters (if required):
        if 'trajectory_distance' in method_signature.parameters:
            if 'trajectory_distance' in params:
                method_name = params['trajectory_distance'].pop('name')
                method_params = params['trajectory_distance'].get('params', {})
                params['trajectory_distance'] = TrajectoryDistanceFactory.get(method_name, dataset, method_params)
                name = method_name
            else:
                # Default
                params['trajectory_distance'] = TrajectoryDistanceFactory.get(DEFAULT_TRAJECTORY_DISTANCE, dataset,{})
                name = DEFAULT_TRAJECTORY_DISTANCE
            logging.info(f"Trajectory distance for clustering: {name}")

        if 'aggregation_method' in method_signature.parameters:
            if 'aggregation_method' in params:
                method_name = params['aggregation_method'].pop('name')
                method_params = params['aggregation_method'].get('params', {})
                params['aggregation_method'] = AggregationMethodFactory.get(method_name, method_params)
                name = method_name
            else:
                # Default
                params['aggregation_method'] = AggregationMethodFactory.get(DEFAULT_AGGREGATION, {})
                name = DEFAULT_AGGREGATION
            logging.info(f"Aggregation method for clustering: {name}")

        return method_class(**params)





